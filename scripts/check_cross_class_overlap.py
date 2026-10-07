import pandas as pd
from pathlib import Path
from difflib import SequenceMatcher
import re

# --------------------------------------------------
# Paths
# --------------------------------------------------

DATA_DIR = Path(
    "data/constructed/australian_gov_media"
)

INPUT = DATA_DIR / "combined_raw.csv"

OUTPUT = DATA_DIR / "review_cross_class_overlap.csv"

SIMILARITY_THRESHOLD = 0.75


# --------------------------------------------------
# Helper: normalise titles for comparison
# --------------------------------------------------

def normalise_title(title):

    title = str(title).lower()

    # Remove common prefix so that:
    # "Joint media release: Australia..."
    # can match "Australia..."
    title = re.sub(
        r"^joint\s+media\s+release\s*:\s*",
        "",
        title
    )

    title = re.sub(
        r"^media\s+release\s*:\s*",
        "",
        title
    )

    # Remove punctuation
    title = re.sub(
        r"[^a-z0-9\s]",
        " ",
        title
    )

    # Normalise whitespace
    title = re.sub(
        r"\s+",
        " ",
        title
    ).strip()

    return title


# --------------------------------------------------
# Load combined raw dataset
# --------------------------------------------------

df = pd.read_csv(INPUT)

df["normalised_title"] = (
    df["title"].apply(normalise_title)
)

print(
    f"Loaded {len(df)} records."
)

print(
    "Checking title similarity across "
    "different classes only...\n"
)


# --------------------------------------------------
# Compare records across different classes
# --------------------------------------------------

matches = []

for i in range(len(df)):

    for j in range(i + 1, len(df)):

        # We only care about CROSS-CLASS overlap
        if df.loc[i, "label"] == df.loc[j, "label"]:
            continue

        title_a = df.loc[i, "normalised_title"]
        title_b = df.loc[j, "normalised_title"]

        similarity = SequenceMatcher(
            None,
            title_a,
            title_b
        ).ratio()

        if similarity >= SIMILARITY_THRESHOLD:

            matches.append({
                "similarity":
                    round(similarity, 3),

                "title_1":
                    df.loc[i, "title"],

                "label_1":
                    df.loc[i, "label"],

                "url_1":
                    df.loc[i, "source_url"],

                "title_2":
                    df.loc[j, "title"],

                "label_2":
                    df.loc[j, "label"],

                "url_2":
                    df.loc[j, "source_url"]
            })


# --------------------------------------------------
# Save review file
# --------------------------------------------------

review_df = pd.DataFrame(matches)

if len(review_df) > 0:

    review_df = review_df.sort_values(
        "similarity",
        ascending=False
    )

    review_df.to_csv(
        OUTPUT,
        index=False
    )

else:

    # Still create the file for reproducibility
    review_df.to_csv(
        OUTPUT,
        index=False
    )


# --------------------------------------------------
# Results
# --------------------------------------------------

print("=" * 70)
print("CROSS-CLASS OVERLAP CHECK COMPLETE")
print("=" * 70)

print(
    f"Potential cross-class title pairs: "
    f"{len(review_df)}"
)

print(
    f"Similarity threshold: "
    f"{SIMILARITY_THRESHOLD}"
)


if len(review_df) > 0:

    print("\nPairs requiring manual review:\n")

    for _, row in review_df.iterrows():

        print("-" * 70)

        print(
            f"Similarity: {row['similarity']}"
        )

        print(
            f"[{row['label_1']}] "
            f"{row['title_1']}"
        )

        print(
            f"[{row['label_2']}] "
            f"{row['title_2']}"
        )


print("\nReview file:")
print(OUTPUT)

print(
    "\nNo records have been deleted "
    "or relabelled."
)

print("=" * 70)