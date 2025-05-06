import json
import os

# === PATH ===
EXPERIMENT_FILE = "path\\to\\experiment.json"
SAMPLES_FILE = "path\\to\\samples.json"
OUTPUT_DIR = "path\\to\\output_folder"

# === OUTPUT FOLDER ===
os.makedirs(OUTPUT_DIR, exist_ok=True)

# === LOAD JSON ===
with open(EXPERIMENT_FILE, "r", encoding="utf-8") as f:
    experiment_data = json.load(f)

with open(SAMPLES_FILE, "r", encoding="utf-8") as f:
    samples_data = json.load(f)

# === EXPERIMENT DICTIONARY ===
experiment_dict = {exp["experiment_id"]: exp for exp in experiment_data}

# === SAMPLE + EXPERIMENT ===
for sample in samples_data:
    sample_experiment_id = sample.get("experiment_id")
    sample_name = sample.get("name", "unnamed_sample").replace(" ", "_")

    experiment = experiment_dict.get(sample_experiment_id)

    if experiment:
        combined = {
            "experiment": experiment,
            "sample": sample
        }

        output_filename = f"{sample_name}.json"
        output_path = os.path.join(OUTPUT_DIR, output_filename)

        with open(output_path, "w", encoding="utf-8") as out_file:
            json.dump(combined, out_file, indent=4)
        print(f"File: {output_filename}")
    else:
        print(f"No experiment for sample: '{sample_name}' (experiment_id: {sample_experiment_id})")
