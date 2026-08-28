import os
import ssl
import certifi

# Fix Windows/Conda SSL certificate issue
old_create_default_context = ssl.create_default_context

ssl.create_default_context = lambda *args, **kwargs: old_create_default_context(
    cafile=certifi.where()
)

from datasets import load_dataset

print("Downloading TREC...")

dataset = load_dataset(
    "trec",
    "default",
    trust_remote_code=True
)

output_dir = os.path.join(
    "data",
    "external",
    "trec",
    "dataset"
)

dataset.save_to_disk(output_dir)

# TREC provides both coarse and fine-grained labels
coarse_labels = dataset["train"].features["coarse_label"].names
fine_labels = dataset["train"].features["fine_label"].names

metadata_path = os.path.join(
    "data",
    "external",
    "trec",
    "README.txt"
)

with open(metadata_path, "w", encoding="utf-8") as file:
    file.write("Dataset: TREC Question Classification\n")
    file.write("Source: Hugging Face datasets - trec\n")
    file.write("Configuration: default\n")
    file.write("Task: Question classification\n")
    file.write(f"Training examples: {len(dataset['train'])}\n")
    file.write(f"Test examples: {len(dataset['test'])}\n")
    file.write(f"Coarse labels: {len(coarse_labels)}\n")
    file.write(f"Fine labels: {len(fine_labels)}\n")
    file.write("Coarse label names: " + ", ".join(coarse_labels) + "\n")

print("\nTREC downloaded successfully.")
print(dataset)

print(f"\nSaved to: {output_dir}")
print(f"Training examples: {len(dataset['train'])}")
print(f"Test examples: {len(dataset['test'])}")

print(f"\nNumber of coarse labels: {len(coarse_labels)}")
print("Coarse labels:", coarse_labels)

print(f"\nNumber of fine labels: {len(fine_labels)}")

print("\nExample:")
print(dataset["train"][0])