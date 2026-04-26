import requests
import os
import json
import ast

API_URL = "http://localhost:8001/predict"
PHOTOS_DIR = "../pet_hashtag_agent/photo"

DESCRIPTION_PROMPT = """Describe this animal's physical features in one short sentence.
Focus on: ears (floppy/pointed/tufted), coat (color/length/texture), body size, tail.
Do NOT guess the breed. Just describe what you see.
Example: "Pointed ears, thick gray and white coat, bushy tail, blue eyes."
"""

def get_raw_response(image_path):
    with open(image_path, 'rb') as f:
        files = {'file': f}
        try:
            resp = requests.post(API_URL, files=files, data={'prompt': DESCRIPTION_PROMPT})
        except Exception:
            resp = requests.post(API_URL, files=files)
    if resp.status_code != 200:
        return None
    result = resp.json()
    return result.get("response") or result.get("description") or result.get("raw_response") or str(result)

def extract_description(raw):
    """Извлекает чистое описание из ответа (пытается достать 'reasoning')."""
    if not raw:
        return ""
    raw = raw.strip()
    if raw.startswith("{") and "'reasoning'" in raw:
        try:
            parsed = ast.literal_eval(raw)
            return parsed.get("reasoning", "").strip()
        except:
            pass
    return raw

def main():
    photos = [
        ("husky1.jpg", "husky"),
        ("labrador1.jpg", "labrador"),
        ("german_shepherd1.jpg", "german shepherd"),
        ("corgi1.jpg", "corgi"),
        ("dachshund1.jpg", "dachshund"),
        ("bulldog_1.jpg", "bulldog"),
        ("samoyed_1.jpg", "samoyed"),
        ("beagle_1.jpg", "beagle"),
        ("shiba_inu_1.jpg", "shiba inu"),
        ("rottweiler_1.jpg", "rottweiler"),
        ("mainecoon1.jpg", "maine coon"),
        ("siamese_1.jpg", "siamese"),
        ("persian_1.jpg", "persian"),
        ("sphynx1.jpg", "sphynx"),
        ("british_shorthair1.jpg", "british shorthair"),
        ("scottish_fold_1.jpg", "scottish fold"),
        ("ragdoll_1.jpg", "ragdoll"),
        ("siberian_cat1.jpg", "siberian"),
        ("russian_blue_1.jpg", "russian blue"),
        ("bengal_1.jpg", "bengal"),
    ]

    training_data = []


    for photo, correct_breed in photos:
        image_path = os.path.join(PHOTOS_DIR, photo)
        if not os.path.exists(image_path):
            print(f"[{photo}] Файл не найден, пропускаем")
            continue

        print(f"Обработка {photo}...")
        raw = get_raw_response(image_path)
        if not raw:
            print(f" Не удалось получить ответ")
            continue

        description = extract_description(raw)
        if len(description) < 10:
            description = raw  # запасной вариант

        training_data.append({
            "text": description,
            "breed": correct_breed
        })
        print(f"{description[:100]}...")

    # Сохраняем датасет для fine-tuning
    with open("training_data.json", "w", encoding="utf-8") as f:
        json.dump(training_data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()