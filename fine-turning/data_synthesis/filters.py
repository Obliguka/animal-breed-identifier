import random

from data_synthesis.config import ALL_BREEDS
from data_synthesis.text_utils import clean_text, normalize_breeds, text_similarity
from data_synthesis.generators import make_medium


def process_data(dataset: list[dict]) -> list[dict]:

    for item in dataset:
        item["text"] = clean_text(item["text"])

    dataset = normalize_breeds(dataset)
    print(f"{len(dataset)}")
    return dataset


def filter_by_quality(dataset: list[dict]) -> list[dict]:
    removed = []
    filtered = []

    for item in dataset:
        text = item["text"]
        breed = item["breed"]
        reasons = []

        word_count = len(text.split())
        if word_count < 5:
            reasons.append(f"короткий ({word_count} слов)")

        if text.rstrip().endswith("...") and word_count < 10:
            reasons.append("обрыв текста")

        if breed not in ALL_BREEDS and breed.lower() not in ALL_BREEDS:
            reasons.append(f"неизвестная порода: {breed}")

        for existing in filtered:
            sim = text_similarity(text, existing["text"])
            if sim > 0.90:
                reasons.append(f"дубликат ({sim:.0%})")
                break

        if "(copy)" in text:
            reasons.append("артефакт (copy)")

        if reasons:
            removed.append((item, reasons))
        else:
            filtered.append(item)

    print(f"[5] Фильтрация: -{len(removed)} = {len(filtered)}")

    if removed:
        for item, reasons in removed[:3]:
            preview = item["text"][:60]
            print(f"      \"{preview}...\" -> {', '.join(reasons)}")

    return filtered


def remove_duplicates(dataset: list[dict]) -> list[dict]:
    unique = []
    for item in dataset:
        is_dup = False
        for existing in unique:
            sim = text_similarity(item["text"], existing["text"])
            if sim > 0.90 and item["breed"].strip().lower() == existing["breed"].strip().lower():
                is_dup = True
                break
        if not is_dup:
            unique.append(item)

    dups = len(dataset) - len(unique)
    if dups:
        print(f"    Ещё дубликатов: {dups}")
    return unique


def ensure_minimum_count(dataset: list[dict], data: list[dict], min_count: int = 100) -> list[dict]:
    if len(dataset) >= min_count:
        return dataset

    extra_needed = min_count - len(dataset)
    extra = random.sample(data, min(extra_needed, len(data)))

    for ex in extra:
        new_text = make_medium(ex["text"], ex["breed"])
        dataset.append({
            "text": new_text,
            "breed": ex["breed"],
            "animal": "dog" if ex["breed"] in [
                "husky", "labrador", "german shepherd", "corgi", "dachshund",
                "bulldog", "samoyed", "beagle", "shiba inu", "rottweiler",
            ] else "cat",
            "quality": "clean",
            "length": "medium",
        })

    dataset = remove_duplicates(dataset)
    return dataset
