import os
import ssl
import certifi

old_create_default_context = ssl.create_default_context

ssl.create_default_context = lambda *args, **kwargs: old_create_default_context(
    cafile=certifi.where()
)

from datasets import load_dataset

output_dir = os.path.join("original_code", "data_linear", "unfair_tos")
os.makedirs(output_dir, exist_ok=True)

train_data = load_dataset(
    "coastalcph/lex_glue",
    "unfair_tos",
    split="train",
    trust_remote_code=True
)

validation_data = load_dataset(
    "coastalcph/lex_glue",
    "unfair_tos",
    split="validation",
    trust_remote_code=True
)

test_data = load_dataset(
    "coastalcph/lex_glue",
    "unfair_tos",
    split="test",
    trust_remote_code=True
)

def save_split(dataset, file_path):
    with open(file_path, "w", encoding="utf-8") as file:
        for example in dataset:
            text = " ".join(example["text"].split())
            labels = " ".join(map(str, example["labels"]))

            file.write(f"{labels}\t{text}\n")

combined_train = list(train_data) + list(validation_data)

save_split(
    combined_train,
    os.path.join(output_dir, "train.txt")
)

save_split(
    test_data,
    os.path.join(output_dir, "test.txt")
)

print("UNFAIR-ToS data prepared successfully.")
print(f"Training examples: {len(combined_train)}")
print(f"Test examples: {len(test_data)}")
print(f"Files saved to: {output_dir}")