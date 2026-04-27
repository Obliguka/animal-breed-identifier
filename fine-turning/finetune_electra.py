import json
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer
from datasets import Dataset
from peft import LoraConfig, get_peft_model, TaskType

with open("training_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

texts = [item["text"] for item in data]
breeds = [item["breed"] for item in data]

unique_breeds = sorted(set(breeds))
label2id = {breed: i for i, breed in enumerate(unique_breeds)}
id2label = {i: breed for breed, i in label2id.items()}
labels = [label2id[breed] for breed in breeds]

dataset = Dataset.from_dict({"text": texts, "label": labels})
dataset = dataset.train_test_split(test_size=0.2, seed=42)
train_dataset = dataset["train"]
eval_dataset = dataset["test"]

# Модель: google/electra-small-discriminator
model_name = "google/electra-small-discriminator"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(
    model_name,
    num_labels=len(unique_breeds),
    id2label=id2label,
    label2id=label2id
)

def tokenize_function(examples):
    return tokenizer(examples["text"], padding="max_length", truncation=True, max_length=128)

tokenized_train = train_dataset.map(tokenize_function, batched=True)
tokenized_eval = eval_dataset.map(tokenize_function, batched=True)

# LoRA для ELECTRA (целевые модули: "query", "value")
lora_config = LoraConfig(
    r=8,
    lora_alpha=16,
    target_modules=["query", "value"],
    lora_dropout=0.1,
    bias="none",
    task_type=TaskType.SEQ_CLS,
)
model = get_peft_model(model, lora_config)

training_args = TrainingArguments(
    output_dir="./electra-lora-breeds",
    num_train_epochs=5,
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    eval_strategy="epoch",
    save_strategy="epoch",
    logging_steps=10,
    learning_rate=2e-4,
    load_best_model_at_end=True,
    metric_for_best_model="accuracy",
    report_to="none",
)

def compute_metrics(eval_pred):
    predictions, labels = eval_pred
    preds = predictions.argmax(axis=-1)
    acc = (preds == labels).astype(float).mean()
    return {"accuracy": acc}

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_train,
    eval_dataset=tokenized_eval,
    compute_metrics=compute_metrics,
)

trainer.train()

# Сохраняем адаптер для ELECTRA
model.save_pretrained("./electra-lora-final")
tokenizer.save_pretrained("./electra-lora-final")
print("Обучение ELECTRA завершено. Адаптер сохранён в ./electra-lora-final")