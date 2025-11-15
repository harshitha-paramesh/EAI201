# class_normalize.py
import sys
from pathlib import Path

# -----------------------------
# Path to your CSV file
# -----------------------------
CSV_PATH = Path(r"C:\Users\ub13-glab-017\Desktop\Final_lab\class.csv")

# -----------------------------
# Check dependencies
# -----------------------------
try:
    import chardet
except ImportError:
    print("Missing dependency: chardet. Install with: pip install chardet")
    sys.exit(1)

try:
    import pandas as pd
except ImportError:
    print("Missing dependency: pandas. Install with: pip install pandas")
    sys.exit(1)

# -----------------------------
# Check if file exists
# -----------------------------
if not CSV_PATH.exists():
    print(f"CSV not found: {CSV_PATH}")
    sys.exit(1)

# -----------------------------
# Detect file encoding
# -----------------------------
with CSV_PATH.open("rb") as f:
    raw = f.read()
det = chardet.detect(raw)
det_enc = det.get("encoding")
det_conf = det.get("confidence", 0)
print(f"chardet detected: {det_enc!r} (confidence={det_conf})")

# -----------------------------
# Try to read CSV with fallbacks
# -----------------------------
fallbacks = [det_enc, "utf-8-sig", "utf-8", "latin-1", "cp1252"]
seen = set()
for enc in fallbacks:
    if not enc or enc in seen:
        continue
    seen.add(enc)
    try:
        df = pd.read_csv(CSV_PATH, encoding=enc)
        print(f"Loaded successfully with encoding: {enc!r}")
        break
    except Exception as e:
        print(f"Failed with encoding {enc!r}: {e}")
else:
    print("All attempts to read the CSV failed.")
    sys.exit(1)

# -----------------------------
# Normalize Animal_Names column to UPPERCASE
# -----------------------------
if "Animal_Names" in df.columns:
    df["Animal_List"] = df["Animal_Names"].astype(str).apply(
        lambda s: [p.strip().upper() for p in s.split(",") if p.strip() != ""]
    )
    df["Animal_Names"] = df["Animal_List"].apply(lambda lst: ", ".join(lst))
else:
    df["Animal_List"] = None
    print("Warning: 'Animal_Names' column not found in the CSV.")

# Preview first 5 rows
print("\nPreview:")
print(df.head().to_string(index=False))

# -----------------------------
# Save cleaned CSV
# -----------------------------
OUT = CSV_PATH.with_name("class_normalized.csv")
try:
    df.to_csv(OUT, index=False, encoding="utf-8")
    print(f"\nSaved cleaned CSV to: {OUT}")
except Exception as e:
    print(f"Failed to save cleaned CSV: {e}")
