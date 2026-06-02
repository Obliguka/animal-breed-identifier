# Fine-tuning классификатора пород

Эксперимент: можно ли дообучить небольшую языковую модель (ELECTRA, BERT)
определять породу по текстовому описанию признаков животного.

## Мотивация

LLaVA 7B хорошо описывает фото, но путает похожие породы.
Идея: заменить второй вызов LLaVA на лёгкую fine-tuned модель (14-110M параметров).

## Пайплайн данных
20 фото → LLaVA (get-description.py) → 20 описаний
→ generate_synthetic_pipeline.py
→ синонимы (pointed ears → erect ears)
→ кроссовер предложений между примерами одной породы
→ шумовые паттерны (правдоподобные ошибки)
→ 126 синтетических примеров (clean/noisy, short/medium/long)
→ training_data.json + synthetic_dataset.json

## Модели (LoRA)

| Модель | Параметры | Размер адаптера | Время обучения |
|--------|-----------|----------------|----------------|
| distilbert-base-uncased | 66M | 5 MB | 13 с |
| google/electra-small-discriminator | 14M | 3 MB | 16 с |
| bert-base-uncased | 110M | 5 MB | 53 с |

LoRA: rank=8, alpha=16, dropout=0.1, target_modules=["query", "value"]

## Результаты

Train_loss стабильно снижался у всех моделей (~3.0 → ~2.9).
Валидационная accuracy = 0% из-за малого размера выборки (4 примера).

**Вывод:** fine-tuning на 20 оригинальных примерах недостаточен.
126 синтетических — всё ещё мало. Для продакшена нужно 500+ примеров на породу.

## Запуск

```bash
# 1. Сгенерировать описания из фото
python get-description.py

# 2. Аугментация
python generate_synthetic_pipeline.py

# 3. Обучение
python finetune_electra.py # ELECTRA
python finetune_bert.py # BERT
python finetune_breed_classifier.py # DistilBERT

Сохранённые адаптеры: electra-lora-final/, bert-lora-final/, lora-model-final/