import tifffile as tf
import numpy as np
import json
import os
import time

# Path to files
INPUT_FOLDER = "path\\to\\tiff_files"
OUTPUT_FOLDER = os.path.join(INPUT_FOLDER, "JSON metadata")

# Create OUTPUT_FOLDER if it doesnt exist
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Function to find best divisor for CZ_SEM
def find_best_divisor(values):
    candidates = [8, 9, 10, 11, 12, 16]
    return next((num for num in candidates if len(values) % num == 0), None)

# Extraction and optimization for CZ_SEM values
def extract_cz_sem(tag_value):
    parameters = [
        "Pixel Size", "Magnification", "Output Device Index", 
        "EHT (Electron High Tension)", "Filament Current",
        "Probe Current", "Working Distance", "Max Scan Speed"
    ]

    if not tag_value:
        return {}

    if isinstance(tag_value, dict) and '' in tag_value:
        values = list(tag_value[''])
    elif isinstance(tag_value, (list, tuple)):
        values = list(tag_value)
    else:
        return {}

    # Delete first 3 values if they are all zeros
    if len(values) > 3 and all(v == 0 for v in values[:3]):
        values = values[3:]

    # Determine number of parameters per scan
    values_per_scan = find_best_divisor(values)
    if values_per_scan is None:
        return {}

    # Extract first set of parameters (no repetitions)
    scan_data = {parameters[j]: values[j] for j in range(values_per_scan)}
    
    return scan_data  # Returns just one dictionary instead of a list

# Convert to JSON serializable
def convert_to_serializable(obj):
    if isinstance(obj, np.ndarray):
        return np.array2string(obj.flatten(), separator=",")  # Converts the array in just a line
    elif isinstance(obj, dict):
        return {k: convert_to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_serializable(i) for i in obj]
    return obj  # Returns the objects as such if it's not serializable

# Anlayze all tiff files in the directory 
for filename in os.listdir(INPUT_FOLDER):
    if filename.endswith(".tif") or filename.endswith(".tiff"):
        file_path = os.path.join(INPUT_FOLDER, filename)

        print(f"Analyzing file: {filename}")

        with tf.TiffFile(file_path) as tif:
            metadata_dict = {}

            # Reads metadata from tiff
            for page in tif.pages:
                for tag in page.tags:
                    tag_name, tag_value = tag.name, tag.value
                    if tag_name == '':
                        tag_name = "Unknown_Metadata"

                    if tag_name == "CZ_SEM":
                        metadata_dict[tag_name] = extract_cz_sem(tag_value)
                    else:
                        metadata_dict[tag_name] = convert_to_serializable(tag_value)

            # Obtain creation date 
            metadata_dict["Creation Date"] = time.ctime(os.path.getctime(file_path))

            # Save to JSON
            json_filename = f"{os.path.splitext(filename)[0]}.json"
            json_output_path = os.path.join(OUTPUT_FOLDER, json_filename)
            with open(json_output_path, "w") as json_file:
                json.dump(metadata_dict, json_file, indent=4)

            print(f"Metadata saved in: {json_output_path}")
