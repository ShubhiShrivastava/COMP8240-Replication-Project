
from pathlib import Path
import sys
import time

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import f1_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MultiLabelBinarizer

# Locate project folders
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "original_code"))

from libmultilabel.linear.linear import train_1vsrest, predict_values

# Original paper configuration
SEED = 1337
OPTIONS = "-s 2 -B 1 -e 0.0001 -q"

np.random.seed(SEED)


def main():
    start = time.perf_counter()

    # Load the final constructed dataset
    data_path = (
        ROOT
        / "data"
        / "constructed"
        / "australian_gov_media"
        / "australian_gov_media_final.csv"
    )

    print("Loading Australian Government Media Releases...")
    df = pd.read_csv(data_path)

    # Check required columns
    required = {"text", "label"}
    if not required.issubset(df.columns):
        raise ValueError("Dataset must contain text and label columns.")

    if df[["text", "label"]].isna().any().any():
        raise ValueError("Missing text or label values detected.")

    print(f"Total records: {len(df)}")
    print(f"Number of categories: {df['label'].nunique()}")

    # Reproducible stratified 80/20 split
    train_df, test_df = train_test_split(
        df,
        test_size=0.20,
        random_state=SEED,
        stratify=df["label"],
    )

    print(f"Training records: {len(train_df)}")
    print(f"Testing records: {len(test_df)}")

    # Save split assignments for reproducibility
    split_df = df[["source_url", "label"]].copy()
    split_df["split"] = "train"
    split_df.loc[test_df.index, "split"] = "test"

    split_path = ROOT / "results" / "australian_gov_split.csv"
    split_path.parent.mkdir(parents=True, exist_ok=True)
    split_df.to_csv(split_path, index=False)

    # Use original default TF-IDF settings
    print("Generating TF-IDF features...")
    vectorizer = TfidfVectorizer()

    x_train = vectorizer.fit_transform(
        train_df["text"].astype(str)
    )
    x_test = vectorizer.transform(
        test_df["text"].astype(str)
    )

    # Original one-vs-rest label representation
    classes = sorted(train_df["label"].unique())

    binarizer = MultiLabelBinarizer(
        classes=classes,
        sparse_output=True,
    )

    y_train = binarizer.fit_transform(
        [[label] for label in train_df["label"]]
    )

    print("Training original LIBLINEAR classifier...")
    model = train_1vsrest(y_train, x_train, OPTIONS)

    print("Evaluating...")
    scores = np.asarray(predict_values(model, x_test))

    # Single-label classification: choose highest score
    predicted_labels = binarizer.classes_[
        np.argmax(scores, axis=1)
    ]

    true_labels = test_df["label"].to_numpy()

    micro_f1 = f1_score(
        true_labels,
        predicted_labels,
        average="micro",
    ) * 100

    macro_f1 = f1_score(
        true_labels,
        predicted_labels,
        average="macro",
    ) * 100

    elapsed = time.perf_counter() - start

    report = classification_report(
        true_labels,
        predicted_labels,
        labels=classes,
        zero_division=0,
    )

    results = (
        "Dataset: Australian Government Media Releases\n"
        f"Total records: {len(df)}\n"
        f"Training records: {len(train_df)}\n"
        f"Testing records: {len(test_df)}\n"
        f"Number of categories: {len(classes)}\n"
        "Split: stratified 80/20\n"
        f"Random seed: {SEED}\n"
        "Model: TF-IDF + LIBLINEAR one-vs-rest SVM\n"
        f"LIBLINEAR options: {OPTIONS}\n"
        "Prediction rule: highest decision score (single-label)\n"
        f"Micro-F1: {micro_f1:.4f}\n"
        f"Macro-F1: {macro_f1:.4f}\n"
        f"Elapsed time (seconds): {elapsed:.2f}\n"
        "\nPer-class classification report:\n"
        f"{report}\n"
    )

    print("\n" + results)

    output_path = (
        ROOT / "results" / "australian_gov_evaluation.txt"
    )
    output_path.write_text(results, encoding="utf-8")

    print(f"Results saved to: {output_path}")
    print(f"Split saved to: {split_path}")


if __name__ == "__main__":
    main()
