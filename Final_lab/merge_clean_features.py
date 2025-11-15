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
MERGED_OUT = BASE_FOLDER / "merged_data_features.csv"

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
    class_df["Animal_Names"] = class_df["Animal_List"].apply(lambda lst: ", ".join(lst))

# -----------------------------
# Load auxiliary metadata JSON
# -----------------------------
with AUX_JSON.open("r", encoding="utf-8") as f:
    aux_data = json.load(f)

aux_df = pd.DataFrame(aux_data)

# -----------------------------
# Merge datasets
# -----------------------------
if "Animal_Names" in class_df.columns:
    class_exploded = class_df.explode("Animal_List").rename(columns={"Animal_List": "animal_name"})

    # Ensure zoo_df has a matching animal_name column
    if "animal_name" not in zoo_df.columns:
        zoo_df["animal_name"] = zoo_df.iloc[:, 0].astype(str).str.upper()
    else:
        zoo_df["animal_name"] = zoo_df["animal_name"].astype(str).str.upper()

    if "animal_name" in aux_df.columns:
        aux_df["animal_name"] = aux_df["animal_name"].astype(str).str.upper()

    merged = pd.merge(zoo_df, class_exploded, on="animal_name", how="outer")
    merged = pd.merge(merged, aux_df, on="animal_name", how="outer")
else:
    print("Cannot find 'Animal_Names' in class.csv")
    merged = pd.DataFrame()

# -----------------------------
# Handle missing values
# -----------------------------
for col in merged.columns:
    if merged[col].dtype == object:
        # Categorical → fill with mode
        if merged[col].mode().empty:
            merged[col].fillna("Unknown", inplace=True)
        else:
            merged[col].fillna(merged[col].mode()[0], inplace=True)
    else:
        # Numerical → fill with mean
        merged[col].fillna(merged[col].mean(), inplace=True)

# -----------------------------
# Feature engineering
# -----------------------------
# Habitat risk score
def habitat_risk(habitat):
    habitat = str(habitat).lower()
    if "marine" in habitat:
        return 3
    elif "freshwater" in habitat or "fresh water" in habitat:
        return 2
    elif "terrestrial" in habitat:
        return 1
    else:
        return 1  # default

merged["habitat_risk_score"] = merged.get("habitat", "terrestrial").apply(habitat_risk)

# Trophic level
def trophic_level(diet):
    diet = str(diet).lower()
    if "carnivore" in diet:
        return 3
    elif "omnivore" in diet:
        return 2
    else:
        return 1  # herbivore or other

merged["trophic_level"] = merged.get("diet", "herbivore").apply(trophic_level)

# -----------------------------
# Save final dataset
# -----------------------------
try:
    merged.to_csv(MERGED_OUT, index=False, encoding="utf-8")
    print(f"Final merged dataset with features saved to: {MERGED_OUT}")
except Exception as e:
    print(f"Failed to save merged dataset: {e}")
