import pandas as pd

# -----------------------------
# FILES
# -----------------------------
INPUT_FILE = "boz_rates_raw.xlsx"
OUTPUT_FILE = "boz_rates_clean.xlsx"

# -----------------------------
# LOAD EXCEL (NO ASSUMPTIONS)
# -----------------------------
df = pd.read_excel(INPUT_FILE, dtype=str)

# Normalize column names
df.columns = df.columns.str.strip().str.upper()

# Keep only expected columns (safety)
expected_cols = ["DATE", "TIME", "BUYING RATE", "MID RATE", "SELLING RATE"]
df = df[expected_cols]

# Strip whitespace from all cells
df = df.apply(lambda col: col.str.strip())

# -----------------------------
# FORWARD-FILL DATE
# -----------------------------
df["DATE"] = df["DATE"].replace("", pd.NA)
df["DATE"] = df["DATE"].ffill()

# -----------------------------
# REMOVE INVALID ROWS
# -----------------------------

# Drop rows where TIME is missing
df = df[df["TIME"].notna()]

# Remove AVERAGE rows
df = df[~df["TIME"].str.contains("AVERAGE", case=False, na=False)]

# Remove fully blank numeric rows
df = df.dropna(subset=["BUYING RATE", "MID RATE", "SELLING RATE"], how="all")

# -----------------------------
# DATE PARSING (ROBUST)
# -----------------------------
df["DATE"] = pd.to_datetime(
    df["DATE"],
    errors="coerce",
    dayfirst=True
)

# Drop rows where date still invalid
df = df[df["DATE"].notna()]

# -----------------------------
# CLEAN TIME FORMAT
# -----------------------------
df["TIME"] = df["TIME"].str.replace(".", ":", regex=False)

# -----------------------------
# CONVERT RATES TO NUMERIC
# -----------------------------
rate_cols = ["BUYING RATE", "MID RATE", "SELLING RATE"]
for col in rate_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Drop rows where rates are missing
df = df.dropna(subset=rate_cols)

# -----------------------------
# SORT & EXPORT
# -----------------------------
df = df.sort_values(["DATE", "TIME"])

df.to_excel(OUTPUT_FILE, index=False)

print(f"✅ Clean Excel created: {OUTPUT_FILE}")
print(f"📊 Rows exported: {len(df)}")
