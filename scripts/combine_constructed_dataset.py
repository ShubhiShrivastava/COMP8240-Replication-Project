import pandas as pd
from pathlib import Path

# --------------------------------------------------
# Paths
# --------------------------------------------------

DATA_DIR = Path(
    "data/constructed/australian_gov_media"
)

FILES = {
    "education": DATA_DIR / "education.csv",
    "health": DATA_DIR / "health.csv",
    "foreign_affairs": DATA_DIR / "foreign_affairs.csv",
    "economy_finance": DATA_DIR / "economy_finance.csv",
    "environment_climate": DATA_DIR / "environment_climate.csv",
}

OUTPUT = DATA_DIR / "combined_raw.csv"


# --------------------------------------------------
# STEP 1: Load all five datasets
# --------------------------------------------------

frames = []

print("Loading constructed datasets...\n")

for expected_label, path in FILES.items():

    df = pd.read_csv(path)

    print(
        f"{expected_label}: "
        f"{len(df)} records"
    )

    # Keep track of which CSV each record came from
    df["source_class"] = expected_label

    frames.append(df)


# --------------------------------------------------
# STEP 2: Combine
# --------------------------------------------------

combined = pd.concat(
    frames,
    ignore_index=True
)

print("\n" + "=" * 65)
print("COMBINED RAW DATASET")
print("=" * 65)

print(
    f"Total records: {len(combined)}"
)

print("\nClass counts:")

print(
    combined["label"]
    .value_counts()
    .sort_index()
)


# --------------------------------------------------
# STEP 3: Missing-value checks
# --------------------------------------------------

print("\n" + "=" * 65)
print("MISSING VALUE CHECK")
print("=" * 65)

for column in [
    "title",
    "text",
    "date",
    "department",
    "label",
    "source_url"
]:

    print(
        f"{column}: "
        f"{combined[column].isna().sum()}"
    )


# --------------------------------------------------
# STEP 4: Exact duplicate checks
# --------------------------------------------------

duplicate_urls = combined[
    combined.duplicated(
        subset=["source_url"],
        keep=False
    )
].copy()

duplicate_text = combined[
    combined.duplicated(
        subset=["text"],
        keep=False
    )
].copy()

duplicate_titles = combined[
    combined.duplicated(
        subset=["title"],
        keep=False
    )
].copy()


print("\n" + "=" * 65)
print("CROSS-DATASET DUPLICATE CHECK")
print("=" * 65)

print(
    "Records involved in duplicate source URLs:",
    len(duplicate_urls)
)

print(
    "Records involved in duplicate exact text:",
    len(duplicate_text)
)

print(
    "Records involved in duplicate titles:",
    len(duplicate_titles)
)


# --------------------------------------------------
# STEP 5: Show cross-class duplicate URLs
# --------------------------------------------------

if len(duplicate_urls) > 0:

    print("\nCross-class duplicate URLs:\n")

    display_columns = [
        "title",
        "label",
        "source_class",
        "source_url"
    ]

    print(
        duplicate_urls[
            display_columns
        ]
        .sort_values("source_url")
        .to_string(index=False)
    )


# --------------------------------------------------
# STEP 6: Show duplicate titles
# Useful when the same joint release appears
# on different government websites.
# --------------------------------------------------

if len(duplicate_titles) > 0:

    print("\n" + "=" * 65)
    print("DUPLICATE TITLES FOR MANUAL REVIEW")
    print("=" * 65)

    print(
        duplicate_titles[
            [
                "title",
                "label",
                "source_class",
                "source_url"
            ]
        ]
        .sort_values("title")
        .to_string(index=False)
    )


# --------------------------------------------------
# STEP 7: Save raw combined dataset
# --------------------------------------------------

combined.to_csv(
    OUTPUT,
    index=False
)


# --------------------------------------------------
# STEP 8: Save duplicate-review files
# --------------------------------------------------

duplicate_urls.to_csv(
    DATA_DIR / "review_duplicate_urls.csv",
    index=False
)

duplicate_text.to_csv(
    DATA_DIR / "review_duplicate_text.csv",
    index=False
)

duplicate_titles.to_csv(
    DATA_DIR / "review_duplicate_titles.csv",
    index=False
)


# --------------------------------------------------
# Final summary
# --------------------------------------------------

print("\n" + "=" * 65)
print("VALIDATION COMPLETE")
print("=" * 65)

print(
    f"Raw combined dataset saved to:\n{OUTPUT}"
)

print(
    "\nReview files saved for duplicate "
    "URLs, text and titles."
)

print(
    "\nNo records have been deleted "
    "or relabelled."
)

print("=" * 65)