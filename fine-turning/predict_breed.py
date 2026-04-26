import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from peft import PeftModel
import json

with open("training_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)
breeds = sorted(set(item["breed"] for item in data))
num_labels = len(breeds)
id2label = {i: breed for i, breed in enumerate(breeds)}
label2id = {breed: i for i, breed in enumerate(breeds)}

model_name = "distilbert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(model_name)
base_model = AutoModelForSequenceClassification.from_pretrained(
    model_name,
    num_labels=num_labels,
    id2label=id2label,
    label2id=label2id
)

model = PeftModel.from_pretrained(base_model, "./lora-model-final")
model.eval()

def predict_breed(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=128, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        pred_id = torch.argmax(logits, dim=-1).item()
    return id2label[pred_id]

test_text = data[0]["text"]
pred = predict_breed(test_text)
print("Тест на первом примере из датасета")
print(f"Текст: {test_text[:200]}...")
print(f"Предсказанная порода: {pred}")
print(f"Истинная порода: {data[0]['breed']}")


new_description = "A medium-sized dog with pointed ears, a thick black and tan coat, and a confident stance."
new_pred = predict_breed(new_description)
print(" Тест на новом описании ")
print(f"Текст: {new_description}")
print(f"Предсказанная порода: {new_pred}")