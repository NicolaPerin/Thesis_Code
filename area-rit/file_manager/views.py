import h5py
import os
import io
import time
import json
import traceback
import base64
import numpy as np
from PIL import Image
from django.utils import timezone
from django.conf import settings
from django.shortcuts import render
from django.http import FileResponse, JsonResponse, HttpResponse
from .nexus_integration import build_nexus_from_tiff_TEM_ED

METADATA_DIR = os.path.join(settings.BASE_DIR, "file_manager", "data")
LOCAL_STORAGE_DIR = os.path.join(settings.BASE_DIR, "local_storage")

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
def homepage_view(request):
    return render(request, 'file_manager/homepage.html')

def load_metadata_schema(schema_filename):
    schema_path = os.path.join(METADATA_DIR, schema_filename)
    with open(schema_path, "r") as f:
        schema = json.load(f)
    return schema

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
            destination_path = os.path.join(LOCAL_STORAGE_DIR, unique_filename)
            os.rename(nexus_file_tmp, destination_path)
            print("File saved to local storage:", destination_path)
        except Exception as e:
            print(traceback.format_exc())
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
        finally:
            if os.path.exists(tiff_path):
                os.remove(tiff_path)

        return render(request, 'file_manager/upload_success.html', {'filename': unique_filename})

    else:
        # GET request: prepare form with available schema files, material suggestions, and experiment types.
        schema_files = [f for f in os.listdir(METADATA_DIR) if f.endswith(".json")]
        materials = ["Suggestion 1", "Suggestion 2", "Suggestion 3", "Other"]
        experiment_types = ["TEM_ED", "TVIPS"]
        today = timezone.now().date().isoformat()
        return render(request, 'file_manager/new_experiment.html', {
            'schema_files': schema_files,
            'experiment_types': experiment_types,
            'current_year': timezone.now().year,
            'default_date': today,
            'default_location': "Trieste",
        })

def list_files_view(request):
    try:
        files = [f for f in os.listdir(LOCAL_STORAGE_DIR) if f != ".gitkeep"]
    except FileNotFoundError:
        return HttpResponse("Local storage directory not found.", status=500)

    return render(request, 'file_manager/file_list.html', {'files': files})

def view_file_view(request, file_name):
    file_path = os.path.join(LOCAL_STORAGE_DIR, file_name)

    if not os.path.exists(file_path):
        return HttpResponse(f"File '{file_name}' not found.", status=404)

    try:
        print("HDF5 file structure with values:")
        print_hdf5_structure_with_values(file_path)

        with open(file_path, "rb") as f:
            with h5py.File(f, "r") as h5_file:

                image_data_list = []
                try:
                    # Access the dataset via chained indexing.
                    nxentry = h5_file["NXentry"]
                    image_2d = nxentry["image_2d"]
                    data_ds = image_2d["data"]

                    # Retrieve the raw NumPy array.
                    image_array = data_ds[()]

                    # Normalize / convert the image data for display:
                    if np.issubdtype(image_array.dtype, np.floating):
                        # Use a percentile-based normalization for contrast enhancement.
                        low, high = np.percentile(image_array, (2, 98))
                        print("Percentiles for contrast stretch:", low, high)
                        if high - low > 0:
                            # Clip and scale the array to the full 0-255 range.
                            image_array = np.clip(image_array, low, high)
                            image_array = (image_array - low) / (high - low) * 255.0
                        else:
                            image_array = np.zeros_like(image_array)
                        image_array = image_array.astype(np.uint8)
                    elif image_array.dtype == np.uint16:
                        # A simple 16-bit to 8-bit conversion.
                        image_array = (image_array / 256).astype(np.uint8)
                    else:
                        # For any other type, perform a basic normalization.
                        image_array = image_array - image_array.min()
                        if image_array.max() > 0:
                            image_array = (image_array / image_array.max() * 255).astype(np.uint8)

                    # Create a PIL Image from the normalized array.
                    image = Image.fromarray(image_array)
                    
                    # Save the image as PNG in an in-memory buffer.
                    buffer = io.BytesIO()
                    image.save(buffer, format="PNG")
                    buffer.seek(0)
                    
                    # Encode the PNG image as Base64 to embed in HTML.
                    image_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                    image_data_list.append(image_b64)
                except Exception as e:
                    print("Error while accessing or converting NXentry/image_2d/data:", e)
                    image_data_list = []

        return render(request, 'file_manager/view_file.html', {
            'file_name': file_name,
            'image_data_list': image_data_list,
        })

    except KeyError as e:
        return HttpResponse(f"KeyError: {e}", status=500)
    except Exception as e:
        return HttpResponse(f"An unexpected error occurred: {e}", status=500)

def download_file_view(request, file_name):
    file_path = os.path.join(LOCAL_STORAGE_DIR, file_name)

    if not os.path.exists(file_path):
        return HttpResponse(f"File '{file_name}' not found.", status=404)

    try:
        with open(file_path, "rb") as f:
            file_data = f.read()

        if request.GET.get("image") == "true":
            with h5py.File(io.BytesIO(file_data), "r") as h5_file:
                # Check for image data under NXentry/image_2d/data
                if (
                    "NXentry" in h5_file and
                    "image_2d" in h5_file["NXentry"] and
                    "data" in h5_file["NXentry"]["image_2d"]
                ):
                    data_ds = h5_file["NXentry"]["image_2d"]["data"]
                    # Retrieve the raw NumPy array
                    image_array = data_ds[()]

                    # Normalize / convert depending on data type.
                    if np.issubdtype(image_array.dtype, np.floating):
                        # Use percentile-based normalization for contrast enhancement.
                        low, high = np.percentile(image_array, (2, 98))
                        if high - low > 0:
                            image_array = np.clip(image_array, low, high)
                            image_array = (image_array - low) / (high - low) * 255.0
                        else:
                            image_array = np.zeros_like(image_array)
                        image_array = image_array.astype(np.uint8)
                    elif image_array.dtype == np.uint16:
                        # Convert 16-bit to 8-bit.
                        image_array = (image_array / 256).astype(np.uint8)
                    else:
                        image_array = image_array.astype(np.uint8)

                    # Create a PIL Image from the array.
                    image = Image.fromarray(image_array)
                    
                    # Save the PIL image to a PNG-format buffer.
                    buffer = io.BytesIO()
                    image.save(buffer, format="PNG")
                    buffer.seek(0)

                    return FileResponse(
                        buffer,
                        as_attachment=True,
                        filename="extracted_image.png"
                    )
                else:
                    return HttpResponse("No image data found in this Nexus file.", status=404)

        # If the GET parameter "image" is not "true", return the entire file.
        return FileResponse(open(file_path, "rb"), as_attachment=True, filename=file_name)

    except Exception as e:
        traceback.print_exc()
        return HttpResponse(f"An error occurred while processing the file: {e}", status=500)
