import pandas as pd
import json
import os

# Excel file path (insert your specific path)
file_path = "path\\to\\file_name.xlsx"
output_folder = "path\\to\\output_folder"

# Load Excel file
xls = pd.ExcelFile(file_path)

# Read data from sheets
samples_df = xls.parse("SAMPLES")
experiment_df = xls.parse("EXPERIMENT")
original_df = xls.parse("ORIGINAL POWDERS SAMPLE")

# Add info about the instrument (not present in the Excel file)
instrument_info = {
    "name": "IMM-CT_SEM/EDX",
    "model": "Zeiss FE-SEM Supra 35",
    "vendor": "Carl Zeiss",
    "manufacturer": "Carl Zeiss Microscopy GmbH",
    "detector": "In-lens",
    "software": {
        "program": "SmartSEM",
        "version": "V0.5.02.05 11_july_2007"
    },
    "source": {
        "emitter_type": "Field Emission",
        "emitter_material": "ZrO/W",
        "probe": "electron"
    }
}

# Converts to JSON
experiments_json = []
for _, row in experiment_df.iterrows():
    experiments_json.append({
        "experiment_id": row["Experiment ID"],
        "title": row["Title"],
        "date": str(row["Date"]),
        "start_time": str(row["Start time"]),
        "end_time": str(row["End time"]),
        "operator": {
            "name": row["Operator"],
            "email": row["Email"],
            "affiliation": row["Affiliation"],
            "address": row["Address"]
        },
        "instrument": instrument_info  # Adds the additional info
    })

# Converts sample data to JSON
samples_json = []
for _, row in samples_df.iterrows():
    samples_json.append({
        "experiment_id": row["Experiment ID"],
        "identifier": row["Sample ID"],
        "identifier_parent": row["Parent ID"],
        "name": row["Sample Name"],
        "atom_types": row["Composition"],
        "date": str(row["Preparation Date"]),
        "description": row["Description"],
        "origin": row["Origin"],
        "analysis_type": row["Analysis Type"],
        "preparation": row["Preparation"],
        "state": row["State"]
    })
# Add original sample data to JSON
original_json = []
for _, row in original_df.iterrows():
    original_json.append({
        "identifier": row["Identifier"],
        "name": row["Sample Name"],
        "date": str(row["Date"]),
        "atom_types": row["Composition"],
        "description": row["Description"],
        "origin": row["Origin"],
        "analysis_type": row["Analysis Type"],
        "preparation": row["Preparation"],
        "state": row["State"],
        "notes": row["Notes"]
    })
# Save JSON files
experiment_json_path = os.path.join(output_folder, "experiment.json")
samples_json_path = os.path.join(output_folder, "samples.json")
original_json_path = os.path.join(output_folder, "original_samples.json")

with open(experiment_json_path, "w") as f:
    json.dump(experiments_json, f, indent=4)

with open(samples_json_path, "w") as f:
    json.dump(samples_json, f, indent=4)

with open(original_json_path, "w") as f:
    json.dump(original_json, f, indent=4)

print(f"JSON files generated:\n - {experiment_json_path}\n - {samples_json_path}\n - {original_json_path}")
