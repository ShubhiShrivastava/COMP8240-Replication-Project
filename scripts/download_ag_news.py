import os
import ssl
import certifi

# Fix Windows/Conda SSL certificate issue
old_create_default_context = ssl.create_default_context

ssl.create_default_context = lambda *args, **kwargs: old_create_default_context(
    cafile=certifi.where()
)

from datasets import load_dataset

print("Downloading AG News...")

dataset = load_dataset("ag_news")

output_dir = os.path.join(
    "data",
    "external",
    "ag_news",
    "dataset"
)

dataset.save_to_disk(output_dir)

# Save a small metadata file for future reference
metadata_path = os.path.join(
    "data",
    "external",
    "ag_news",
    "README.txt"
)

with open(metadata_path, "w", encoding="utf-8") as file:
    file.write("Dataset: AG News\n")
    file.write("Source: Hugging Face datasets - ag_news\n")
    file.write("Task: Multi-class news topic classification\n")
    file.write("Classes: World, Sports, Business, Sci/Tech\n")
    file.write(f"Training examples: {len(dataset['train'])}\n")
    file.write(f"Test examples: {len(dataset['test'])}\n")

print("\nAG News downloaded successfully.")
print(dataset)
print(f"\nSaved to: {output_dir}")
print(f"Training examples: {len(dataset['train'])}")
print(f"Test examples: {len(dataset['test'])}")
print("Labels:", dataset["train"].features["label"].names)