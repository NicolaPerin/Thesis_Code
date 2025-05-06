import h5py
import os
import io
import time
import json
import traceback
import base64
import zipfile
import logging
import boto3
import numpy as np
from PIL import Image
from django.utils import timezone
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.http import FileResponse, JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from botocore.exceptions import NoCredentialsError, ClientError
from .nexus_integration import build_nexus_from_tiff_TEM_ED

METADATA_DIR = os.path.join(settings.BASE_DIR, "file_manager", "data")

logger = logging.getLogger(__name__)

def my_logout_view(request):
    # 1. Log out locally
    logout(request)
    logger.debug("Local Django session ended for user %s", request.user)

    # 2. Construct the end-session URL dynamically
    id_token = request.session.get('oidc_id_token', '')

    end_session_url = (
        f"{settings.OIDC_OP_LOGOUT_ENDPOINT}"
        f"?id_token_hint={id_token}"
        f"&post_logout_redirect_uri={settings.OIDC_LOGOUT_REDIRECT_URL}"
    )
    
    logger.debug("Redirecting user to Authentik end-session endpoint: %s", end_session_url)

    return redirect(end_session_url)

# ============================
# Debug Helper Function
# ============================
def print_hdf5_structure_with_values(file_path, max_preview_elements=10, small_dataset_threshold=20):
    import numpy as np
    with h5py.File(file_path, "r") as f:
        def visitor(name, obj):
            if isinstance(obj, h5py.Dataset):
                try:
                    data = obj[()]
                    if np.isscalar(data) or data.size <= small_dataset_threshold:
                        print(f"{name} (Dataset): {data}")
                    else:
                        flat = np.array(data).flatten()
                        preview = flat[:max_preview_elements]
                        print(f"{name} (Dataset): shape {obj.shape}, dtype {obj.dtype}, preview {preview.tolist()} ...")
                except Exception as e:
                    print(f"{name} (Dataset): [Error reading dataset: {e}]")
            elif isinstance(obj, h5py.Group):
                try:
                    attr_dict = {key: obj.attrs[key] for key in obj.attrs}
                except Exception as e:
                    attr_dict = f"Error reading attributes: {e}"
                print(f"{name} (Group): attributes {attr_dict}")
        f.visititems(visitor)

# ============================
# View Functions
# ============================
@login_required
def homepage_view(request):
    return render(request, 'file_manager/homepage.html')

def load_metadata_schema(schema_filename):
    schema_path = os.path.join(METADATA_DIR, schema_filename)
    with open(schema_path, "r") as f:
        schema = json.load(f)
    return schema

@login_required
def new_experiment_view(request):
    if request.method == 'POST':
        # Get fields from the form
        operator_name = request.POST.get('operator_name', '')
        description = request.POST.get('description', '')
        schema_file_name = request.POST.get('schema_file_name', '')
        material = request.POST.get('material', '')
        if material == "Other":
            material = request.POST.get('custom_material', '')
        hypothetical_composition = request.POST.get('hypothetical_composition', '')
        initial_composition = request.POST.get('initial_composition', '')
        final_composition = request.POST.get('final_composition', '')

        image_files = request.FILES.getlist('image_files')
        if not image_files:
            return JsonResponse({"status": "error", "message": "No image files uploaded."}, status=400)

        # For this minimal version, use only the first uploaded image.
        image_file = image_files[0]
        tiff_path = f"/tmp/{image_file.name}"
        with open(tiff_path, 'wb') as f:
            for chunk in image_file.chunks():
                f.write(chunk)

        # Extra experiment fields to store in the NeXus file.
        extra_fields = {
            "operator_name":      operator_name,
            "description":        description,
            "material":           material,
            "sample_identifier":  request.POST.get("sample_identifier", ""),
            "preparation_date":   request.POST.get("preparation_date", ""),   # ISO date
            "atom_types":         request.POST.get("atom_types", ""),
            "hypothetical_composition": hypothetical_composition,
            "initial_composition":      initial_composition,
            "final_composition":        final_composition,
            "instrument_name":          request.POST.get("instrument_name", ""),
            "instrument_location":      request.POST.get("instrument_location", ""),
        }

        # Use the schema (mapping JSON) selected by the user.
        exp_type = request.POST.get('experiment_type')
        mapping_json_path = os.path.join(
            METADATA_DIR,
            {
                "ED":    "ED_mapping.json",
                "TVIPS": "TVIPS_mapping.json",
                "TEM":   request.POST.get('schema_file_name', '')  # fall‑back
            }.get(exp_type, request.POST.get('schema_file_name', ''))
        )
        unique_filename = f"TEM_{int(time.time())}.nxs"
        nexus_file_tmp = f"/tmp/{unique_filename}"

        try:
            build_nexus_from_tiff_TEM_ED(
                tiff_path,
                mapping_json_path,
                out_nxs=nexus_file_tmp,
                extra_fields=extra_fields,
            )

            s3_client = boto3.client(
                "s3",
                endpoint_url=settings.AWS_S3_ENDPOINT_URL,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            )
            with open(nexus_file_tmp, "rb") as nexus_file:
                s3_client.upload_fileobj(
                    nexus_file,
                    settings.AWS_STORAGE_BUCKET_NAME,
                    unique_filename
                )

            print("NeXus file uploaded to MinIO:", unique_filename)

        except NoCredentialsError:
            return JsonResponse({"status": "error", "message": "MinIO credentials not found."}, status=500)
        except ClientError as e:
            return JsonResponse({"status": "error", "message": f"MinIO error: {str(e)}"}, status=500)
        except Exception as e:
            print(traceback.format_exc())
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
        finally:
            # cleanup both temp files
            for p in (tiff_path, nexus_file_tmp):
                if os.path.exists(p):
                    os.remove(p)

        return render(request, 'file_manager/upload_success.html', {'filename': unique_filename})

    else:
        # GET request: prepare form with available schema files, material suggestions, and experiment types.
        schema_files = [f for f in os.listdir(METADATA_DIR) if f.endswith(".json")]
        materials = ["Suggestion 1", "Suggestion 2", "Suggestion 3", "Other"]
        experiment_types = ["TEM_ED", "TVIPS"]
        today = timezone.now().date().isoformat()
        return render(request, 'file_manager/new_experiment.html', {
            'schema_files': schema_files,
            'materials': materials,
            'experiment_types': experiment_types,
            'current_year': timezone.now().year,
            'default_date': today,
            'default_location': "Trieste",
        })

@login_required
def list_files_view(request):
    """
    Fetch a list of files stored in MinIO.
    """
    try:
        s3_client = boto3.client(
            "s3",
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )

        objects = s3_client.list_objects_v2(Bucket=settings.AWS_STORAGE_BUCKET_NAME)

        files = [obj["Key"] for obj in objects.get("Contents", [])]

        return render(request, "file_manager/file_list.html", {"files": files})

    except NoCredentialsError:
        return HttpResponse("Missing MinIO credentials.", status=500)

    except ClientError as e:
        return HttpResponse(f"MinIO error: {str(e)}", status=500)

@login_required
def view_file_view(request, file_name):
    """
    Fetch a NeXus file from MinIO, extract images, and display them.
    """
    try:
        # Create a MinIO client and fetch the file
        s3_client = boto3.client(
            "s3",
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        file_obj = s3_client.get_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=file_name
        )
        file_content = file_obj["Body"].read()

        # Open the HDF5 in-memory and process with Nexus logic
        with h5py.File(io.BytesIO(file_content), "r") as h5_file:
            # dump structure via the helper (using a real path)
            tmp_path = f"/tmp/{file_name}"
            with open(tmp_path, "wb") as tmp:
                tmp.write(file_content)
            print_hdf5_structure_with_values(tmp_path)
            os.remove(tmp_path)

            image_data_list = []
            try:
                nxentry    = h5_file["NXentry"]
                image_2d   = nxentry["image_2d"]
                data_ds    = image_2d["data"]
                image_array = data_ds[()]

                # normalize for display
                if np.issubdtype(image_array.dtype, np.floating):
                    low, high = np.percentile(image_array, (2, 98))
                    if high > low:
                        image_array = np.clip(image_array, low, high)
                        image_array = (image_array - low) / (high - low) * 255.0
                    else:
                        image_array = np.zeros_like(image_array)
                    image_array = image_array.astype(np.uint8)
                elif image_array.dtype == np.uint16:
                    image_array = (image_array / 256).astype(np.uint8)
                else:
                    image_array = image_array - image_array.min()
                    if image_array.max() > 0:
                        image_array = (image_array / image_array.max() * 255).astype(np.uint8)

                # turn into PNG + base64
                image = Image.fromarray(image_array)
                buffer = io.BytesIO()
                image.save(buffer, format="PNG")
                buffer.seek(0)
                image_b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
                image_data_list.append(image_b64)

            except Exception as e:
                print("Error processing HDF5:", e)
                image_data_list = []

        return render(
            request,
            "file_manager/view_file.html",
            {"file_name": file_name, "image_data_list": image_data_list}
        )

    except NoCredentialsError:
        return HttpResponse("Missing MinIO credentials.", status=500)

    except ClientError as e:
        return HttpResponse(f"MinIO error: {str(e)}", status=500)

    except KeyError as e:
        return HttpResponse(f"KeyError: {e}", status=500)

    except Exception as e:
        return HttpResponse(f"An unexpected error occurred: {e}", status=500)

@login_required
def download_file_view(request, file_name):
    """
    Download a file from MinIO. If ?image=true, extract the single NXentry/image_2d/data
    as a PNG (new-branch logic). Otherwise, stream the raw file bytes.
    """
    try:
        # — MinIO client & fetch (old branch) —
        s3_client = boto3.client(
            "s3",
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        file_obj     = s3_client.get_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=file_name
        )
        file_content = file_obj["Body"].read()

        # — new-branch image extraction —
        if request.GET.get("image") == "true":
            with h5py.File(io.BytesIO(file_content), "r") as h5_file:
                try:
                    nxentry     = h5_file["NXentry"]
                    image_2d    = nxentry["image_2d"]
                    data_ds     = image_2d["data"]
                    image_array = data_ds[()]

                    # normalize / convert to 8-bit
                    if np.issubdtype(image_array.dtype, np.floating):
                        low, high = np.percentile(image_array, (2, 98))
                        if high > low:
                            image_array = np.clip(image_array, low, high)
                            image_array = (image_array - low) / (high - low) * 255.0
                        else:
                            image_array = np.zeros_like(image_array)
                    elif image_array.dtype == np.uint16:
                        image_array = image_array / 256
                    # else assume already in 0–255 range
                    image_array = image_array.astype(np.uint8)

                    # render to PNG in memory
                    buf = io.BytesIO()
                    Image.fromarray(image_array).save(buf, format="PNG")
                    buf.seek(0)
                    return FileResponse(buf, as_attachment=True, filename="extracted_image.png")

                except Exception:
                    return HttpResponse("No NXentry/image_2d/data found.", status=404)

        # — raw download for all other cases —
        return FileResponse(io.BytesIO(file_content), as_attachment=True, filename=file_name)

    except NoCredentialsError:
        return HttpResponse("Missing MinIO credentials.", status=500)
    except ClientError as e:
        return HttpResponse(f"MinIO error: {e}", status=500)
    except Exception as e:
        traceback.print_exc()
        return HttpResponse(f"An error occurred while processing the file: {e}", status=500)
