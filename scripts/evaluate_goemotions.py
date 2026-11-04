
from pathlib import Path
import sys
import time

import numpy as np
import pyarrow.ipc as ipc
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import f1_score
from sklearn.preprocessing import MultiLabelBinarizer

# Locate project folders
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "original_code"))

from libmultilabel.linear.linear import train_1vsrest, predict_values

# Original paper configuration
SEED = 1337
OPTIONS = "-s 2 -B 1 -e 0.0001 -q"

np.random.seed(SEED)


def load_arrow(split):
    path = (
        ROOT
        / "data"
        / "external"
        / "goemotions"
        / "dataset"
        / split
        / "data-00000-of-00001.arrow"
    )

    with path.open("rb") as file:
        table = ipc.open_stream(file).read_all()

    texts = table["text"].to_pylist()
    labels = table["labels"].to_pylist()

    return texts, labels


def main():
    start = time.perf_counter()

    print("Loading GoEmotions...")
    train_texts, train_labels = load_arrow("train")
    test_texts, test_labels = load_arrow("test")

    print(f"Training records: {len(train_texts)}")
    print(f"Testing records: {len(test_texts)}")

    # Check label IDs and ensure all 28 categories are represented.
    all_labels = sorted(
        set(label for row in train_labels + test_labels for label in row)
    )
    print(f"Number of labels: {len(all_labels)}")

    print("Generating TF-IDF features...")
    vectorizer = TfidfVectorizer()
    x_train = vectorizer.fit_transform(train_texts)
    x_test = vectorizer.transform(test_texts)

    # Multilabel representation used by the original implementation.
    binarizer = MultiLabelBinarizer(
        classes=all_labels,
        sparse_output=True,
    )

    y_train = binarizer.fit_transform(train_labels)
    y_test = binarizer.transform(test_labels)

    print("Training original LIBLINEAR classifier...")
    model = train_1vsrest(y_train, x_train, OPTIONS)

    print("Evaluating multilabel predictions...")
    scores = np.asarray(predict_values(model, x_test))

    # Original paper's multilabel prediction threshold.
    predictions = (scores > 0).astype(int)

    micro_f1 = f1_score(
        y_test, predictions, average="micro", zero_division=0
    ) * 100

    macro_f1 = f1_score(
        y_test, predictions, average="macro", zero_division=0
    ) * 100

    elapsed = time.perf_counter() - start

    results = (
        "Dataset: GoEmotions\n"
        f"Training records: {len(train_texts)}\n"
        f"Testing records: {len(test_texts)}\n"
        f"Number of labels: {len(all_labels)}\n"
        "Model: TF-IDF + LIBLINEAR one-vs-rest SVM\n"
        f"LIBLINEAR options: {OPTIONS}\n"
        "Prediction rule: decision score > 0 (multilabel)\n"
        f"Micro-F1: {micro_f1:.4f}\n"
        f"Macro-F1: {macro_f1:.4f}\n"
        f"Elapsed time (seconds): {elapsed:.2f}\n"
        "Validation split: not used\n"
    )

    print("\n" + results)

    output_path = ROOT / "results" / "goemotions_evaluation.txt"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(results, encoding="utf-8")

    print(f"Results saved to: {output_path}")


if __name__ == "__main__":
    main()
