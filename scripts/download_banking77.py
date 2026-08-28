import os
import ssl
import certifi

# Fix Windows/Conda SSL certificate issue
old_create_default_context = ssl.create_default_context

ssl.create_default_context = lambda *args, **kwargs: old_create_default_context(
    cafile=certifi.where()
)

from datasets import load_dataset

print("Downloading BANKING77...")

dataset = load_dataset("banking77", "default")

output_dir = os.path.join(
    "data",
    "external",
    "banking77",
    "dataset"
)

dataset.save_to_disk(output_dir)

metadata_path = os.path.join(
    "data",
    "external",
    "banking77",
    "README.txt"
)

with open(metadata_path, "w", encoding="utf-8") as file:
    file.write("Dataset: BANKING77\n")
    file.write("Source: Hugging Face datasets - banking77\n")
    file.write("Task: Multi-class banking intent classification\n")
    file.write(f"Training examples: {len(dataset['train'])}\n")
    file.write(f"Test examples: {len(dataset['test'])}\n")
    file.write(f"Number of labels: {len(dataset['train'].features['label'].names)}\n")

print("\nBANKING77 downloaded successfully.")
print(dataset)
print(f"\nSaved to: {output_dir}")
print(f"Training examples: {len(dataset['train'])}")
print(f"Test examples: {len(dataset['test'])}")
print(f"Number of labels: {len(dataset['train'].features['label'].names)}")
print("First 10 labels:")
print(dataset["train"].features["label"].names[:10])