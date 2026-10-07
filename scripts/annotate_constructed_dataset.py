import pandas as pd
from pathlib import Path


# ==================================================
# PATHS
# ==================================================

DATA_DIR = Path("data/constructed/australian_gov_media")

INPUT = DATA_DIR / "combined_raw.csv"

OUTPUT = DATA_DIR / "combined_annotation_stage.csv"

AUDIT_OUTPUT = DATA_DIR / "annotation_decisions.csv"

REVIEW_OUTPUT = DATA_DIR / "annotation_review_candidates.csv"


# ==================================================
# LOAD RAW DATASET
# ==================================================

df = pd.read_csv(INPUT)

print(f"Loaded raw combined dataset: {len(df)} records")


# ==================================================
# CONFIRMED MANUAL EXCLUSIONS
# ==================================================
#
# These records were inspected manually after
# duplicate / cross-class / topic review.
#
# They are identified by title rather than row
# number so the process remains reproducible.
# ==================================================

EXCLUSIONS = {

    "Australia backs stronger coastlines and communities in the Pacific":
        (
            "Cross-class duplicate/joint release. "
            "The Environment / Climate version was retained because "
            "the substantive topic concerns climate resilience and "
            "coastal communities."
        ),

    "Joint media release: Additional fuel excise relief for the month of July":
        (
            "Overlapping fuel-excise policy release. "
            "The Economy / Finance version was retained because "
            "manual content review showed that the substantive topic "
            "concerns fuel taxation, cost-of-living relief and "
            "economic support."
        ),

    "Crisis housing for Queenslanders that need it most":
        (
            "Manual content review showed that this release focuses "
            "on crisis housing and homelessness. It does not fit any "
            "of the five target topic classes sufficiently well, "
            "so it was excluded."
        )
}


# ==================================================
# CONFIRMED MANUAL RELABELLING
# ==================================================

RELABELS = {

    "$10K incentives backing more Tasmanians into a trade": {
        "new_label": "education",
        "reason": (
            "Manual content review showed that the release focuses "
            "on apprenticeships, vocational training and workforce "
            "skills. Education is therefore more appropriate than "
            "the original Health label."
        )
    },

    "Funding doubled for Logan Medicare Mental Health Centre": {
        "new_label": "health",
        "reason": (
            "Manual content review showed that the release focuses "
            "on mental health services, Medicare and healthcare "
            "access. Health is therefore more appropriate than "
            "the original Economy / Finance label."
        )
    }
}


# ==================================================
# AUDIT TRAIL
# ==================================================

audit_rows = []


# ==================================================
# APPLY CONFIRMED EXCLUSIONS
# ==================================================

exclude_indices = []

for title, reason in EXCLUSIONS.items():

    matches = df[df["title"] == title]

    if len(matches) == 0:
        print(f"\nWARNING: exclusion title not found:\n{title}")
        continue

    for index, row in matches.iterrows():

        exclude_indices.append(index)

        audit_rows.append({
            "action": "exclude",
            "title": row["title"],
            "original_label": row["label"],
            "final_label": "",
            "source_url": row["source_url"],
            "reason": reason
        })

        print(
            f"\nConfirmed exclusion:\n"
            f"  [{row['label']}] {row['title']}"
        )


# Remove confirmed exclusions

annotated = (
    df.drop(index=exclude_indices)
    .reset_index(drop=True)
)


# ==================================================
# APPLY CONFIRMED RELABELS
# ==================================================

for title, decision in RELABELS.items():

    matches = annotated[
        annotated["title"] == title
    ]

    if len(matches) == 0:
        print(f"\nWARNING: relabel title not found:\n{title}")
        continue

    for index, row in matches.iterrows():

        old_label = row["label"]
        new_label = decision["new_label"]

        annotated.loc[index, "label"] = new_label

        audit_rows.append({
            "action": "relabel",
            "title": row["title"],
            "original_label": old_label,
            "final_label": new_label,
            "source_url": row["source_url"],
            "reason": decision["reason"]
        })

        print(
            f"\nConfirmed relabel:\n"
            f"  {old_label} -> {new_label}\n"
            f"  {row['title']}"
        )


# ==================================================
# SAVE AUDIT TRAIL
# ==================================================

audit_df = pd.DataFrame(
    audit_rows,
    columns=[
        "action",
        "title",
        "original_label",
        "final_label",
        "source_url",
        "reason"
    ]
)

audit_df.to_csv(
    AUDIT_OUTPUT,
    index=False
)


# ==================================================
# FLAG POTENTIALLY AMBIGUOUS RECORDS
# ==================================================
#
# These keywords are only used to identify records
# worth reviewing.
#
# A keyword match does NOT automatically mean that
# the label is wrong.
# ==================================================

REVIEW_TERMS = {

    "education": [
        "visa",
        "migration",
        "health",
        "climate",
        "housing"
    ],

    "health": [
        "ndis",
        "disability",
        "trade",
        "climate",
        "education"
    ],

    "foreign_affairs": [
        "climate",
        "energy",
        "economic",
        "trade",
        "environment"
    ],

    "economy_finance": [
        "housing",
        "health",
        "medicare",
        "climate",
        "energy"
    ],

    "environment_climate": [
        "fuel excise",
        "fuel security",
        "tax",
        "economic",
        "trade"
    ]
}


review_rows = []

for index, row in annotated.iterrows():

    label = row["label"]

    title_lower = str(row["title"]).lower()

    terms = REVIEW_TERMS.get(label, [])

    matched_terms = [
        term
        for term in terms
        if term in title_lower
    ]

    if matched_terms:

        review_rows.append({
            "row_id": index,
            "title": row["title"],
            "current_label": label,
            "matched_terms": ", ".join(matched_terms),
            "source_url": row["source_url"]
        })


review_df = pd.DataFrame(
    review_rows,
    columns=[
        "row_id",
        "title",
        "current_label",
        "matched_terms",
        "source_url"
    ]
)

review_df.to_csv(
    REVIEW_OUTPUT,
    index=False
)


# ==================================================
# SAVE ANNOTATION-STAGE DATASET
# ==================================================

annotated.to_csv(
    OUTPUT,
    index=False
)


# ==================================================
# FINAL SUMMARY
# ==================================================

print("\n" + "=" * 70)
print("ANNOTATION PASS COMPLETE")
print("=" * 70)

print(f"Raw records: {len(df)}")

print(
    f"Confirmed exclusions: "
    f"{len(exclude_indices)}"
)

print(
    f"Confirmed relabels: "
    f"{sum(a['action'] == 'relabel' for a in audit_rows)}"
)

print(
    f"Records after exclusions: "
    f"{len(annotated)}"
)

print("\nClass counts after annotation:")

print(
    annotated["label"]
    .value_counts()
    .sort_index()
)

print(
    f"\nRecords currently flagged by keyword review: "
    f"{len(review_df)}"
)

print("\nAnnotation-stage dataset:")
print(OUTPUT)

print("\nAudit trail:")
print(AUDIT_OUTPUT)

print("\nManual-review candidates:")
print(REVIEW_OUTPUT)

print(
    "\nNOTE: Keyword-flagged records have not been "
    "automatically removed or relabelled."
)

print("=" * 70)