import os
import ssl
import certifi

# Fix Windows/Conda SSL certificate issue
old_create_default_context = ssl.create_default_context

ssl.create_default_context = lambda *args, **kwargs: old_create_default_context(
    cafile=certifi.where()
)

from datasets import load_dataset

print("Downloading GoEmotions (simplified)...")

dataset = load_dataset("go_emotions", "simplified")

output_dir = os.path.join(
    "data",
    "external",
    "goemotions",
    "dataset"
)

dataset.save_to_disk(output_dir)

# Get label information
label_names = dataset["train"].features["labels"].feature.names

metadata_path = os.path.join(
    "data",
    "external",
    "goemotions",
    "README.txt"
)

with open(metadata_path, "w", encoding="utf-8") as file:
    file.write("Dataset: GoEmotions\n")
    file.write("Source: Hugging Face datasets - go_emotions\n")
    file.write("Configuration: simplified\n")
    file.write("Task: Multi-label emotion classification\n")
    file.write(f"Training examples: {len(dataset['train'])}\n")
    file.write(f"Validation examples: {len(dataset['validation'])}\n")
    file.write(f"Test examples: {len(dataset['test'])}\n")
    file.write(f"Number of labels: {len(label_names)}\n")
    file.write("Labels: " + ", ".join(label_names) + "\n")

print("\nGoEmotions downloaded successfully.")
print(dataset)

print(f"\nSaved to: {output_dir}")
print(f"Training examples: {len(dataset['train'])}")
print(f"Validation examples: {len(dataset['validation'])}")
print(f"Test examples: {len(dataset['test'])}")
print(f"Number of labels: {len(label_names)}")

print("\nLabels:")
print(label_names)

print("\nExample:")
print(dataset["train"][0])