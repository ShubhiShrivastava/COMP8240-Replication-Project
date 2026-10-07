import pandas as pd
from pathlib import Path


# ==================================================
# PATHS
# ==================================================

DATA_DIR = Path("data/constructed/australian_gov_media")
RESULTS_DIR = Path("results")

INPUT = DATA_DIR / "combined_annotation_stage.csv"
AUDIT_INPUT = DATA_DIR / "annotation_decisions.csv"

FINAL_OUTPUT = DATA_DIR / "australian_gov_media_final.csv"
SUMMARY_OUTPUT = RESULTS_DIR / "constructed_dataset_final_summary.txt"

RESULTS_DIR.mkdir(exist_ok=True)


# ==================================================
# LOAD DATA
# ==================================================

df = pd.read_csv(INPUT)
audit = pd.read_csv(AUDIT_INPUT)

print(f"Loaded annotation-stage dataset: {len(df)} records")


# ==================================================
# BASIC CLEANING
# ==================================================

text_columns = [
    "title",
    "text",
    "date",
    "department",
    "label",
    "source_url"
]

for column in text_columns:
    df[column] = (
        df[column]
        .astype(str)
        .str.strip()
    )


# ==================================================
# FINAL VALIDATION
# ==================================================

missing_counts = df[text_columns].isna().sum()

blank_counts = (
    df[text_columns]
    .eq("")
    .sum()
)

duplicate_urls = df.duplicated(
    subset=["source_url"],
    keep=False
).sum()

duplicate_text = df.duplicated(
    subset=["text"],
    keep=False
).sum()

duplicate_titles = df.duplicated(
    subset=["title"],
    keep=False
).sum()


# ==================================================
# TEXT LENGTH STATISTICS
# ==================================================

df["text_length_words"] = (
    df["text"]
    .str.split()
    .str.len()
)

class_counts = (
    df["label"]
    .value_counts()
    .sort_index()
)

class_length_stats = (
    df.groupby("label")["text_length_words"]
    .agg(["count", "mean", "median", "min", "max"])
    .round(1)
)


# ==================================================
# ANNOTATION STATISTICS
# ==================================================

exclusion_count = (
    audit["action"] == "exclude"
).sum()

relabel_count = (
    audit["action"] == "relabel"
).sum()


# ==================================================
# SAVE FINAL DATASET
# ==================================================

df.to_csv(
    FINAL_OUTPUT,
    index=False
)


# ==================================================
# BUILD SUMMARY
# ==================================================

summary_lines = []

summary_lines.append(
    "AUSTRALIAN GOVERNMENT MEDIA RELEASE "
    "TOPIC CLASSIFICATION DATASET"
)

summary_lines.append("=" * 65)

summary_lines.append(
    f"\nFinal number of records: {len(df)}"
)

summary_lines.append(
    f"Number of topic classes: {df['label'].nunique()}"
)

summary_lines.append(
    f"Confirmed manual exclusions: {exclusion_count}"
)

summary_lines.append(
    f"Confirmed manual relabels: {relabel_count}"
)

summary_lines.append(
    "\nCLASS DISTRIBUTION"
)

summary_lines.append("-" * 65)

summary_lines.append(
    class_counts.to_string()
)

summary_lines.append(
    "\n\nMISSING / BLANK VALUE CHECK"
)

summary_lines.append("-" * 65)

for column in text_columns:
    summary_lines.append(
        f"{column}: "
        f"{missing_counts[column]} missing, "
        f"{blank_counts[column]} blank"
    )

summary_lines.append(
    "\nDUPLICATE CHECK"
)

summary_lines.append("-" * 65)

summary_lines.append(
    f"Records involved in duplicate source URLs: "
    f"{duplicate_urls}"
)

summary_lines.append(
    f"Records involved in duplicate exact text: "
    f"{duplicate_text}"
)

summary_lines.append(
    f"Records involved in duplicate titles: "
    f"{duplicate_titles}"
)

summary_lines.append(
    "\nTEXT LENGTH BY CLASS (WORDS)"
)

summary_lines.append("-" * 65)

summary_lines.append(
    class_length_stats.to_string()
)

summary_lines.append(
    "\n\nANNOTATION PROCESS"
)

summary_lines.append("-" * 65)

summary_lines.append(
    "Initial topic labels were assigned from the "
    "official Australian Government portfolio/source."
)

summary_lines.append(
    "Cross-class title similarity and keyword-based "
    "screening were then used to identify potentially "
    "ambiguous records for manual review."
)

summary_lines.append(
    "Manual content inspection resulted in "
    f"{exclusion_count} confirmed exclusions and "
    f"{relabel_count} confirmed relabelling decisions."
)

summary_lines.append(
    "All manual decisions and reasons are preserved "
    "in annotation_decisions.csv."
)

summary_lines.append(
    "\nFINAL DATASET"
)

summary_lines.append("-" * 65)

summary_lines.append(
    str(FINAL_OUTPUT)
)


summary_text = "\n".join(summary_lines)


# ==================================================
# SAVE SUMMARY
# ==================================================

with open(
    SUMMARY_OUTPUT,
    "w",
    encoding="utf-8"
) as file:
    file.write(summary_text)


# ==================================================
# PRINT RESULTS
# ==================================================

print("\n" + "=" * 70)
print("FINAL CONSTRUCTED DATASET VALIDATION")
print("=" * 70)

print(summary_text)

print("\n" + "=" * 70)

print(
    f"Summary saved to:\n{SUMMARY_OUTPUT}"
)

print(
    f"\nFinal dataset saved to:\n{FINAL_OUTPUT}"
)

print("=" * 70)