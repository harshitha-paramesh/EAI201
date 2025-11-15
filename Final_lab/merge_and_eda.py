import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path
import chardet

# -----------------------------
# Paths
# -----------------------------
BASE_FOLDER = Path(r"C:\Users\ub13-glab-017\Desktop\Final_lab")
MERGED_FILE = BASE_FOLDER / "merged_data_features.csv"

# -----------------------------
# Detect CSV encoding
# -----------------------------
def detect_encoding(file_path):
    with open(file_path, "rb") as f:
        raw = f.read()
    det = chardet.detect(raw)
    return det.get("encoding", "utf-8")

# -----------------------------
# Load CSV
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

# -----------------------------
# Load dataset
# -----------------------------
if not MERGED_FILE.exists():
    print(f"File not found: {MERGED_FILE}")
    exit(1)

df = load_csv(MERGED_FILE)
print("Dataset loaded. Preview:")
print(df.head())

# -----------------------------
# Handle missing values
# -----------------------------
for col in df.columns:
    if df[col].dtype == object:
        df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else "Unknown", inplace=True)
    else:
        df[col].fillna(df[col].mean(), inplace=True)

# -----------------------------
# Feature engineering
# -----------------------------
def habitat_risk(habitat):
    habitat = str(habitat).lower()
    if "marine" in habitat:
        return 3
    elif "freshwater" in habitat or "fresh water" in habitat:
        return 2
    elif "terrestrial" in habitat:
        return 1
    else:
        return 1

def trophic_level(diet):
    diet = str(diet).lower()
    if "carnivore" in diet:
        return 3
    elif "omnivore" in diet:
        return 2
    else:
        return 1

df["habitat_risk_score"] = df.get("habitat", "terrestrial").apply(habitat_risk)
df["trophic_level"] = df.get("diet", "herbivore").apply(trophic_level)

# -----------------------------
# Exploratory Data Analysis
# -----------------------------
def beta_eda_and_cleaning(df, output_folder):
    output_folder = Path(output_folder)
    output_folder.mkdir(exist_ok=True)

    # 1. Pie chart - class distribution
    if "class_type" in df.columns:
        class_counts = df["class_type"].value_counts()
        plt.figure(figsize=(6,6))
        plt.pie(class_counts, labels=class_counts.index, autopct="%1.1f%%", startangle=140,
                colors=sns.color_palette("pastel"))
        plt.title("Class Distribution")
        plt.savefig(output_folder / "pie_class_distribution.png")
        plt.show()

    # 2. KDE plots - fins & legs
    for col in ["fins", "legs"]:
        if col in df.columns:
            plt.figure(figsize=(10,6))
            sns.kdeplot(df[col], fill=True, bw_adjust=0.5)
            plt.title(f"Distribution of {col.capitalize()}")
            plt.xlabel(col)
            plt.ylabel("Density")
            plt.savefig(output_folder / f"kde_{col}.png")
            plt.show()

    # 3. Count plot - habitat types by diet
    if "habitat" in df.columns and "diet" in df.columns:
        plt.figure(figsize=(10,6))
        sns.countplot(data=df, x="habitat", hue="diet", palette="Set2")
        plt.title("Habitat Types by Diet")
        plt.xlabel("Habitat")
        plt.ylabel("Count")
        plt.legend(title="Diet")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(output_folder / "count_habitat_by_diet.png")
        plt.show()

    # 4. Heatmap - feature correlations
    numeric_df = df.select_dtypes(include=["float64","int64"])
    if not numeric_df.empty:
        plt.figure(figsize=(10,8))
        corr = numeric_df.corr()
        sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", linewidths=0.5)
        plt.title("Feature Correlations Heatmap")
        plt.tight_layout()
        plt.savefig(output_folder / "heatmap_feature_correlations.png")
        plt.show()

# -----------------------------
# Run EDA
# -----------------------------
beta_eda_and_cleaning(df, BASE_FOLDER)

# -----------------------------
# Save final dataset (optional)
# -----------------------------
final_out = BASE_FOLDER / "merged_data_features_cleaned.csv"
df.to_csv(final_out, index=False, encoding="utf-8")
print(f"Cleaned dataset with features saved to: {final_out}")
