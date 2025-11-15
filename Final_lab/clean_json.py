import json
from pathlib import Path

# -----------------------------
# Paths
# -----------------------------
JSON_PATH = Path(r"C:\Users\ub13-glab-017\Desktop\Final_lab\auxiliary_metadata.json")
OUT_PATH = JSON_PATH.with_name("auxiliary_metadata_cleaned.json")

# -----------------------------
# Field name standardization mapping
# -----------------------------
FIELD_MAPPING = {
    # Conservation
    "conservation_status": "conservation_status",
    "conservation": "conservation_status",
    "status": "conservation_status",

    # Habitat
    "habitat": "habitat",
    "habitats": "habitat",
    "habitat_type": "habitat",

    # Diet
    "diet": "diet",
    "diet_type": "diet",
}

# -----------------------------
# Diet value standardization
# -----------------------------
DIET_MAPPING = {
    "omnivor": "omnivore",
    " omnivore": "omnivore",
    "carnivor": "carnivore",
    " herbivore": "herbivore",
    "fresh water": "freshwater",
    "fresh-water": "freshwater",
    "marine water": "marine",
    # Add more mappings as needed
}

# -----------------------------
# Read JSON safely
# -----------------------------
cleaned_data = []

if not JSON_PATH.exists():
    print(f"JSON file not found: {JSON_PATH}")
    exit(1)

with JSON_PATH.open("r", encoding="utf-8") as f:
    try:
        data = json.load(f)
    except json.JSONDecodeError:
        # If JSON is line-delimited
        f.seek(0)
        data = []
        for line in f:
            try:
                obj = json.loads(line)
                data.append(obj)
            except json.JSONDecodeError:
                print(f"Skipping corrupted line: {line.strip()}")

# -----------------------------
# Normalize field names and fix diet values
# -----------------------------
for entry in data:
    if not isinstance(entry, dict):
        continue
    cleaned_entry = {}
    for key, value in entry.items():
        new_key = FIELD_MAPPING.get(key, key)
        # Clean diet field values
        if new_key == "diet" and isinstance(value, str):
            val = value.strip().lower()
            val = DIET_MAPPING.get(val, val)  # map if in DIET_MAPPING
            cleaned_entry[new_key] = val
        else:
            cleaned_entry[new_key] = value
    cleaned_data.append(cleaned_entry)

# -----------------------------
# Save cleaned JSON
# -----------------------------
try:
    with OUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(cleaned_data, f, indent=4)
    print(f"Cleaned JSON saved to: {OUT_PATH}")
except Exception as e:
    print(f"Failed to save cleaned JSON: {e}")
