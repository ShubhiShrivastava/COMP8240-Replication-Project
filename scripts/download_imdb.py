import os
import ssl
import certifi

# Fix Windows/Conda SSL certificate issue
old_create_default_context = ssl.create_default_context

ssl.create_default_context = lambda *args, **kwargs: old_create_default_context(
    cafile=certifi.where()
)

from datasets import load_dataset

print("Downloading IMDb...")

dataset = load_dataset("imdb")

output_dir = os.path.join(
    "data",
    "external",
    "imdb",
    "dataset"
)

dataset.save_to_disk(output_dir)

label_names = dataset["train"].features["label"].names

metadata_path = os.path.join(
    "data",
    "external",
    "imdb",
    "README.txt"
)

with open(metadata_path, "w", encoding="utf-8") as file:
    file.write("Dataset: IMDb\n")
    file.write("Source: Hugging Face datasets - imdb\n")
    file.write("Task: Binary sentiment classification\n")
    file.write(f"Training examples: {len(dataset['train'])}\n")
    file.write(f"Test examples: {len(dataset['test'])}\n")
    file.write(f"Number of labels: {len(label_names)}\n")
    file.write("Labels: " + ", ".join(label_names) + "\n")

print("\nIMDb downloaded successfully.")
print(dataset)

print(f"\nSaved to: {output_dir}")
print(f"Training examples: {len(dataset['train'])}")
print(f"Test examples: {len(dataset['test'])}")
print(f"Number of labels: {len(label_names)}")
print("Labels:", label_names)

print("\nExample:")
print(dataset["train"][0])