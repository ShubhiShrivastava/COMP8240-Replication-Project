import os
import ssl
import certifi

# Fix Windows/Conda SSL certificate issue
# This must run BEFORE importing Hugging Face datasets
old_create_default_context = ssl.create_default_context

ssl.create_default_context = lambda *args, **kwargs: old_create_default_context(
    cafile=certifi.where()
)

from datasets import load_from_disk

datasets_to_check = {
    "AG News": "data/external/ag_news/dataset",
    "BANKING77": "data/external/banking77/dataset",
    "GoEmotions": "data/external/goemotions/dataset",
    "IMDb": "data/external/imdb/dataset",
    "TREC": "data/external/trec/dataset",
}

print("=" * 60)
print("COMP8240 External Dataset Verification")
print("=" * 60)

all_ok = True

for name, path in datasets_to_check.items():
    print(f"\nChecking {name}...")

    if not os.path.exists(path):
        print(f"ERROR: Dataset folder not found: {path}")
        all_ok = False
        continue

    try:
        dataset = load_from_disk(path)

        print("Status: OK")
        print("Splits:", list(dataset.keys()))

        for split in dataset.keys():
            print(f"  {split}: {len(dataset[split]):,} examples")

    except Exception as error:
        print(f"ERROR: {error}")
        all_ok = False

print("\n" + "=" * 60)

if all_ok:
    print("SUCCESS: All 5 external datasets loaded correctly.")
else:
    print("WARNING: One or more datasets failed verification.")

print("=" * 60)