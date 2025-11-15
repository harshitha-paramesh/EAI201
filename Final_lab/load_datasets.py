import pandas as pd
import json
import os

# Get current folder path
folder_path = os.getcwd()  # saves files in the same folder as the script

# -----------------------------
# 1. Load zoo.csv with proper encoding
# -----------------------------
try:
    zoo_df = pd.read_csv("zoo.csv", encoding='utf-8')
except UnicodeDecodeError:
    zoo_df = pd.read_csv("zoo.csv", encoding='latin1')

print("Zoo DataFrame loaded successfully!")
print(zoo_df.head())

# Save cleaned zoo.csv
zoo_output_path = os.path.join(folder_path, "zoo_cleaned.csv")
zoo_df.to_csv(zoo_output_path, index=False)
print(f"Zoo CSV saved at: {zoo_output_path}")

# -----------------------------
# 2. Load class.csv with appropriate method
# -----------------------------
try:
    class_df = pd.read_csv("class.csv")
except pd.errors.ParserError:
    class_df = pd.read_csv("class.csv", engine='python')

print("\nClass DataFrame loaded successfully!")
print(class_df.head())

# Save cleaned class.csv
class_output_path = os.path.join(folder_path, "class_cleaned.csv")
class_df.to_csv(class_output_path, index=False)
print(f"Class CSV saved at: {class_output_path}")

# -----------------------------
# 3. Load auxiliary_metadata.json handling corrupted fields
# -----------------------------
def load_json_safe(file_path):
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_number, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue  # skip empty lines
            try:
                data.append(json.loads(line))
            except json.JSONDecodeError:
                print(f"Warning: Skipping corrupted JSON at line {line_number}")
    return data

auxiliary_metadata = load_json_safe("auxiliary_metadata.json")
print("\nAuxiliary Metadata loaded successfully!")
print(auxiliary_metadata[:5])

# Save cleaned auxiliary metadata as JSON
aux_output_path = os.path.join(folder_path, "auxiliary_metadata_cleaned.json")
with open(aux_output_path, 'w', encoding='utf-8') as f:
    json.dump(auxiliary_metadata, f, indent=4)
print(f"Auxiliary Metadata saved at: {aux_output_path}")
