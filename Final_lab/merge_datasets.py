import pandas as pd
import json
from pathlib import Path
import chardet

# -----------------------------
# Paths
# -----------------------------
BASE_FOLDER = Path(r"C:\Users\ub13-glab-017\Desktop\Final_lab")
ZOO_CSV = BASE_FOLDER / "zoo.csv"
CLASS_CSV = BASE_FOLDER / "class.csv"
AUX_JSON = BASE_FOLDER / "auxiliary_metadata_cleaned.json"
MERGED_OUT = BASE_FOLDER / "merged_data.csv"

# -----------------------------
# Helper: detect encoding
# -----------------------------
def detect_encoding(file_path):
    with open(file_path, "rb") as f:
        raw = f.read()
    det = chardet.detect(raw)
    return det.get("encoding", "utf-8")

# -----------------------------
# Load CSV safely
# -----------------------------
def load_csv(path):
    enc = detect_encoding(path)
    for fallback in [enc, "utf-8-sig", "utf-8", "latin-1", "cp1252"]:
        try:
            df = pd.read_csv(path, encoding=fallback)
            print(f"Loaded {path.name} with encoding {fallback}")
            return df
        except Exception:
            continue
    raise ValueError(f"Failed to load CSV: {path}")

zoo_df = load_csv(ZOO_CSV)
class_df = load_csv(CLASS_CSV)

# -----------------------------
# Normalize animal names in class_df
# -----------------------------
if "Animal_Names" in class_df.columns:
    class_df["Animal_List"] = class_df["Animal_Names"].astype(str).apply(
        lambda s: [p.strip().upper() for p in s.split(",") if p.strip() != ""]
    )
    # Update the Animal_Names column to cleaned string
    class_df["Animal_Names"] = class_df["Animal_List"].apply(lambda lst: ", ".join(lst))

# -----------------------------
# Load auxiliary metadata JSON
# -----------------------------
with AUX_JSON.open("r", encoding="utf-8") as f:
    aux_data = json.load(f)

# Convert JSON list of dicts into DataFrame
aux_df = pd.DataFrame(aux_data)

# -----------------------------
# Merge datasets
# -----------------------------
# Assume merge key is 'animal name'; match uppercase
if "Animal_Names" in class_df.columns:
    # Explode Animal_List to have one row per animal for merging
    class_exploded = class_df.explode("Animal_List")
    class_exploded = class_exploded.rename(columns={"Animal_List": "animal_name"})

    # Uppercase the zoo_df animal names as well for matching
    if "animal_name" in zoo_df.columns:
        zoo_df["animal_name"] = zoo_df["animal_name"].astype(str).str.upper()
    else:
        # Try common columns
        zoo_df["animal_name"] = zoo_df.iloc[:, 0].astype(str).str.upper()

    if "animal_name" in aux_df.columns:
        aux_df["animal_name"] = aux_df["animal_name"].astype(str).str.upper()

    # Merge zoo + class
    merged = pd.merge(zoo_df, class_exploded, on="animal_name", how="outer")
    # Merge with auxiliary metadata
    merged = pd.merge(merged, aux_df, on="animal_name", how="outer")

else:
    print("Cannot find 'Animal_Names' in class.csv")
    merged = pd.DataFrame()  # empty

# -----------------------------
# Save merged dataset
# -----------------------------
try:
    merged.to_csv(MERGED_OUT, index=False, encoding="utf-8")
    print(f"Merged dataset saved to: {MERGED_OUT}")
except Exception as e:
    print(f"Failed to save merged dataset: {e}")
