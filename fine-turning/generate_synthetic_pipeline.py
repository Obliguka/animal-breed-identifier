
import json
import random
import re
from collections import Counter, defaultdict

random.seed(42)
INPUT_FILE = "training_data.json"
OUTPUT_FILE = "synthetic_dataset.json"
REPORT_FILE = "synthetic_report.txt"

TOTAL_TARGET = 150  # запас после фильтрации

# Породы
DOG_BREEDS = [
    "husky", "labrador", "german shepherd", "corgi", "dachshund",
    "bulldog", "samoyed", "beagle", "shiba inu", "rottweiler"
]
CAT_BREEDS = [
    "maine coon", "siamese", "persian", "sphynx", "british shorthair",
    "scottish fold", "ragdoll", "siberian", "russian blue", "bengal"
]
ALL_BREEDS = DOG_BREEDS + CAT_BREEDS


TARGET = {
    "animal": {"dog": 0.5, "cat": 0.5},
    "quality": {"clean": 0.7, "noisy": 0.3},
    "length": {"short": 0.4, "medium": 0.4, "long": 0.2},
}

# Синонимы признаков (для вариативности)
SYNONYMS = {
    "pointed ears": ["erect ears", "upright ears", "straight ears", "standing ears", "perky ears"],
    "floppy ears": ["drooping ears", "pendulous ears", "hanging ears", "long ears", "soft ears"],
    "short coat": ["short fur", "smooth coat", "close-lying coat", "low-maintenance coat", "fine coat"],
    "fluffy coat": ["fluffy fur", "thick coat", "plush coat", "dense coat", "plushy fur"],
    "long coat": ["long fur", "flowing coat", "silky coat", "lengthy coat", "luxurious coat"],
    "bushy tail": ["fluffy tail", "thick tail", "plumed tail", "full tail", "feathery tail"],
    "curled tail": ["curved tail", "spiral tail", "coiled tail", "curling tail", "ring tail"],
    "muscular build": ["athletic build", "powerful build", "strong body", "robust physique", "sturdy frame"],
    "wolf-like face": ["fox-like face", "pointed face", "triangular face", "angular face", "tapered face"],
    "large eyes": ["big eyes", "expressive eyes", "wide eyes", "prominent eyes", "striking eyes"],
    "blue eyes": ["pale eyes", "icy eyes", "bright blue eyes", "glacial eyes"],
    "wrinkled skin": ["loose skin", "folded skin", "wrinkly face", "creased skin", "puckered skin"],
    "thick double coat": ["heavy double coat", "dense undercoat", "insulating coat", "weather-resistant coat"],
    "short legs": ["stubby legs", "tiny legs", "low-set legs", "short limbs"],
    "long legs": ["tall legs", "lengthy limbs", "extended legs", "long limbs"],
    "white muzzle": ["pale muzzle", "light snout", "white snout region", "light-colored muzzle"],
    "black and tan": ["dark and tan", "brown and black", "rich black and rust", "ebony and tan"],
    "curled tail over back": ["tail curved upward", "upturned tail", "tail curling over the spine", "raised curved tail"],
    "pushed-in nose": ["flat nose", "short snout", "brachycephalic face", "squashed nose"],
    "tricolor coat": ["three-tone coat", "tri-colored fur pattern", "patchy coat", "multi-colored coat"],
}

# Шумовые паттерны (правдоподобные ошибки распознавания)
NOISE_PATTERNS = [
    "There might also be some {wrong_breed} traits visible.",
    "The ears slightly resemble those of a {wrong_breed}.",
    "However, the coat texture is similar to a {wrong_breed}.",
    "Some features are also seen in {wrong_breed}s.",
    "A {wrong_breed} owner might mistake it at first glance.",
    "The overall shape is somewhat reminiscent of a {wrong_breed}.",
    "Without a DNA test, a {wrong_breed} cross cannot be ruled out.",
]


def load_data(path: str) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"[1] Загружено исходных примеров: {len(data)}")
    return data


def get_animal(breed: str) -> str:
    return "dog" if breed in DOG_BREEDS else "cat"


def replace_synonyms(text: str) -> str:
    result = text
    for phrase, synonyms in SYNONYMS.items():
        if phrase in result.lower() and random.random() < 0.5:
            replacement = random.choice(synonyms)
            pattern = re.compile(re.escape(phrase), re.IGNORECASE)
            result = pattern.sub(replacement, result, count=1)
    return result


def shuffle_sentences(text: str) -> str:
    sentences = re.split(r'(?<=[.!?])\s+', text)
    if len(sentences) > 1:
        random.shuffle(sentences)
    return " ".join(sentences)


def split_sentences(text: str) -> list[str]:
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if len(s.strip().split()) >= 3]


def extract_breed_features(text: str, breed: str) -> list[str]:
    sentences = split_sentences(text)
    feature_keywords = [
        "ear", "coat", "fur", "tail", "face", "eye", "body", "build",
        "leg", "snout", "muzzle", "nose", "color", "pattern", "size",
    ]
    scored = []
    for s in sentences:
        score = sum(1 for kw in feature_keywords if kw in s.lower())
        scored.append((score, s))
    scored.sort(reverse=True)
    return [s for _, s in scored]


def crossover_sentences(breed_examples: list[dict], breed: str) -> str:
    
    all_sentences = []
    for ex in breed_examples:
        all_sentences.extend(extract_breed_features(ex["text"], breed))

    if len(all_sentences) < 2:
        if breed_examples:
            return breed_examples[0]["text"]
        return f"A typical example of a {breed} breed."

    n_sentences = min(random.randint(2, 4), len(all_sentences))
    chosen = random.sample(all_sentences, n_sentences)

    connectors = [
        " Additionally,", " Moreover,", " Also,",
        " Furthermore,", " In addition,", "",
    ]
    result_parts = [chosen[0]]
    for s in chosen[1:]:
        connector = random.choice(connectors)
        first_word = s.split()[0] if s.split() else ""
        if connector and first_word:
            result_parts.append(connector + " " + first_word.lower() + s[len(first_word):])
        else:
            result_parts.append(" " + s)

    return "".join(result_parts)


def make_short(text: str, breed: str) -> str:
    sentences = split_sentences(text)
    if len(sentences) <= 1:
        short = text
    else:
        n = random.randint(1, min(2, len(sentences)))
        short = " ".join(random.sample(sentences, n))
    if len(short) > 130:
        short = short[:short.rfind(" ", 0, 120)] + "."
    return short


def make_medium(text: str, breed: str) -> str:
    result = replace_synonyms(text)
    result = shuffle_sentences(result)
    return result


def make_long(text: str, breed: str) -> str:
    extras = [
        f" The {breed} breed is known for its distinctive appearance and temperament.",
        f" This particular specimen appears to be a fine example of the {breed} breed.",
        f" The photo quality is good enough to see the characteristic {breed} features clearly.",
        f" These traits collectively point to the {breed} breed without much ambiguity.",
        f" Overall, the {breed} is a popular breed with these unmistakable features.",
    ]
    result = make_medium(text, breed)
    return result + random.choice(extras)


def make_noisy(text: str, breed: str) -> str:
    same_animal = DOG_BREEDS if breed in DOG_BREEDS else CAT_BREEDS
    wrong_choices = [b for b in same_animal if b != breed]
    wrong_breed = random.choice(wrong_choices)

    pattern = random.choice(NOISE_PATTERNS)
    noise = pattern.format(wrong_breed=wrong_breed)

    result = make_medium(text, breed)
    return result + " " + noise


GENERATORS = {
    ("clean", "short"): make_short,
    ("clean", "medium"): make_medium,
    ("clean", "long"): make_long,
    ("noisy", "medium"): make_noisy,
}


def compute_target_counts(total: int) -> dict:
    counts = {}
    for dim, props in TARGET.items():
        counts[dim] = {}
        for category, prop in props.items():
            counts[dim][category] = round(total * prop)

    for dim, props in TARGET.items():
        actual = sum(counts[dim].values())
        if actual < total:
            # Добавляем недостающее к самой большой категории
            largest = max(props, key=props.get)
            counts[dim][largest] += total - actual

    return counts


def assign_quality_and_length() -> list[tuple[str, str]]:
    counts = compute_target_counts(TOTAL_TARGET)
    assignments = []

    qualities = (["clean"] * counts["quality"]["clean"] +
                 ["noisy"] * counts["quality"]["noisy"])

    for q in qualities:
        if q == "noisy":
            assignments.append((q, "medium"))
        else:
            r = random.random()
            if r < TARGET["length"]["short"]:
                assignments.append((q, "short"))
            elif r < TARGET["length"]["short"] + TARGET["length"]["medium"]:
                assignments.append((q, "medium"))
            else:
                assignments.append((q, "long"))

    random.shuffle(assignments)
    return assignments


def generate_dataset(data: list[dict]) -> list[dict]:
    print("\n[2] Запуск генерации...")
    print(f"    Цель: {TOTAL_TARGET} примеров")

    assignments = assign_quality_and_length()

    breed_examples = defaultdict(list)
    for ex in data:
        if ex["breed"] in ALL_BREEDS:
            breed_examples[ex["breed"]].append(ex)

    dog_breed_target = int(TARGET["animal"]["dog"] * TOTAL_TARGET)
    cat_breed_target = TOTAL_TARGET - dog_breed_target
    per_dog_breed = dog_breed_target // len(DOG_BREEDS)
    per_cat_breed = cat_breed_target // len(CAT_BREEDS)

    remainder_dog = dog_breed_target - per_dog_breed * len(DOG_BREEDS)
    remainder_cat = cat_breed_target - per_cat_breed * len(CAT_BREEDS)

    breed_targets = {}
    for b in DOG_BREEDS:
        breed_targets[b] = per_dog_breed
    for b in CAT_BREEDS:
        breed_targets[b] = per_cat_breed

    for b in random.sample(DOG_BREEDS, remainder_dog):
        breed_targets[b] += 1
    for b in random.sample(CAT_BREEDS, remainder_cat):
        breed_targets[b] += 1

    dataset = []
    breed_counts = defaultdict(int)

    for quality, length in assignments:
        available_breeds = [b for b in ALL_BREEDS
                            if breed_targets[b] > breed_counts[b]
                            and len(breed_examples[b]) > 0]
        if not available_breeds:
            available_breeds = [b for b in ALL_BREEDS if len(breed_examples[b]) > 0]
        if not available_breeds:
            break

        chosen_breed = random.choice(available_breeds)
        source = random.choice(breed_examples[chosen_breed])

        generator = GENERATORS.get((quality, length))
        if generator is None:
            generator = make_medium

        if generator in (make_medium, make_noisy) and len(breed_examples[chosen_breed]) >= 2 and random.random() < 0.3:
            generated_text = crossover_sentences(breed_examples[chosen_breed], chosen_breed)
            generated_text = replace_synonyms(generated_text)
        else:
            generated_text = generator(source["text"], chosen_breed)

        dataset.append({
            "text": generated_text,
            "breed": chosen_breed,
            "animal": get_animal(chosen_breed),
            "quality": quality,
            "length": length,
        })
        breed_counts[chosen_breed] += 1

    print(f"    Сгенерировано: {len(dataset)} примеров")
    return dataset


def coverage_report(dataset: list[dict], target: dict) -> str:
    """Формирует отчёт о покрытии."""
    lines = []
    lines.append("=" * 60)
    lines.append("ОТЧЁТ ОБ ОХВАТЕ ИЗМЕРЕНИЙ (COVERAGE REPORT)")
    lines.append("=" * 60)
    lines.append(f"Всего примеров: {len(dataset)}")
    lines.append("")

    animal_counts = Counter(d["animal"] for d in dataset)
    lines.append("--- По типу животного (animal) ---")
    for animal in ["dog", "cat"]:
        actual = animal_counts.get(animal, 0)
        expected_pct = target["animal"].get(animal, 0)
        expected = round(len(dataset) * expected_pct)
        status = "OK" if abs(actual - expected) / max(expected, 1) < 0.15 else "ОТКЛОНЕНИЕ"
        lines.append(f"  {animal:20s}: {actual:3d} (ожидалось ~{expected}, {expected_pct*100:.0f}%) [{status}]")
    lines.append("")

    quality_counts = Counter(d["quality"] for d in dataset)
    lines.append("--- По качеству (quality) ---")
    for q in ["clean", "noisy"]:
        actual = quality_counts.get(q, 0)
        expected_pct = target["quality"].get(q, 0)
        expected = round(len(dataset) * expected_pct)
        status = "OK" if abs(actual - expected) / max(expected, 1) < 0.20 else "ОТКЛОНЕНИЕ"
        lines.append(f"  {q:20s}: {actual:3d} (ожидалось ~{expected}, {expected_pct*100:.0f}%) [{status}]")
    lines.append("")

    length_counts = Counter(d["length"] for d in dataset)
    lines.append("--- По длине (length) ---")
    for l in ["short", "medium", "long"]:
        actual = length_counts.get(l, 0)
        expected_pct = target["length"].get(l, 0)
        expected = round(len(dataset) * expected_pct)
        status = "OK" if abs(actual - expected) / max(expected, 1) < 0.25 else "ОТКЛОНЕНИЕ"
        lines.append(f"  {l:20s}: {actual:3d} (ожидалось ~{expected}, {expected_pct*100:.0f}%) [{status}]")
    lines.append("")

    breed_counts = Counter(d["breed"] for d in dataset)
    lines.append("--- По породам (breed) ---")
    dog_total = sum(breed_counts[b] for b in DOG_BREEDS)
    cat_total = sum(breed_counts[b] for b in CAT_BREEDS)
    target_per_breed_dog = max(round(dog_total / len(DOG_BREEDS)), 1)
    target_per_breed_cat = max(round(cat_total / len(CAT_BREEDS)), 1)

    for breed in ALL_BREEDS:
        actual = breed_counts.get(breed, 0)
        exp = target_per_breed_dog if breed in DOG_BREEDS else target_per_breed_cat
        status = "OK" if abs(actual - exp) / max(exp, 1) < 0.4 else "МАЛО"
        lines.append(f"  {breed:25s}: {actual:3d} (в среднем ~{exp}) [{status}]")
    lines.append("")

    # 5. Сводка
    n_breeds_covered = sum(1 for b in ALL_BREEDS if breed_counts.get(b, 0) > 0)
    lines.append(f"Пород покрыто: {n_breeds_covered} из {len(ALL_BREEDS)}")
    if n_breeds_covered == len(ALL_BREEDS):
        lines.append("  -> ВСЕ ПОРОДЫ ПРЕДСТАВЛЕНЫ")
    else:
        missing = [b for b in ALL_BREEDS if breed_counts.get(b, 0) == 0]
        lines.append(f"  -> Отсутствуют: {', '.join(missing)}")

    lines.append("=" * 60)
    return "\n".join(lines)

def clean_text(text: str) -> str:
    text = re.sub(r'\s*\(copy\)', '', text)
    text = re.sub(r'\s*\(copy\)', '', text)

    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'\.{2,}', '.', text)

    if text and text[0].islower():
        text = text[0].upper() + text[1:]

    return text


def normalize_breeds(dataset: list[dict]) -> list[dict]:
    for item in dataset:
        item["breed"] = item["breed"].strip().lower()
    return dataset


def process_data(dataset: list[dict]) -> list[dict]:
    print(f"\n[4] Обработка данных...")
    print(f"    До обработки: {len(dataset)}")

    for item in dataset:
        item["text"] = clean_text(item["text"])

    dataset = normalize_breeds(dataset)

    print(f"    После обработки: {len(dataset)}")
    return dataset


def text_similarity(a: str, b: str) -> float:
    words_a = set(a.lower().split())
    words_b = set(b.lower().split())
    if not words_a or not words_b:
        return 0.0
    intersection = words_a & words_b
    union = words_a | words_b
    return len(intersection) / len(union)


def filter_by_quality(dataset: list[dict]) -> list[dict]:
    removed = []
    filtered = []

    for item in dataset:
        text = item["text"]
        breed = item["breed"]
        reasons = []

        word_count = len(text.split())
        if word_count < 5:
            reasons.append(f"слишком короткий ({word_count} слов)")

        if text.rstrip().endswith("...") and word_count < 10:
            reasons.append("обрыв текста")

        if breed not in ALL_BREEDS and breed.lower() not in ALL_BREEDS:
            reasons.append(f"неизвестная порода: {breed}")

        for existing in filtered:
            sim = text_similarity(text, existing["text"])
            if sim > 0.90:
                reasons.append(f"дубликат (сходство {sim:.0%})")
                break

        if "(copy)" in text:
            reasons.append("артефакт (copy)")

        if reasons:
            removed.append((item, reasons))
        else:
            filtered.append(item)

    print(f"\n[5] Фильтрация низкого качества...")
    print(f"    Удалено: {len(removed)} записей")
    print(f"    Осталось: {len(filtered)}")

    if removed:
        print("\n    Примеры удалённых записей:")
        for item, reasons in removed[:5]:
            preview = item["text"][:60]
            print(f"      - \"{preview}...\" -> {', '.join(reasons)}")

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
    duplicates = len(dataset) - len(unique)
    if duplicates:
        print(f"    Дополнительно удалено дубликатов (fuzzy+breed): {duplicates}")
    return unique


def save_results(dataset: list[dict], output_path: str, report_path: str):
    final = [{"text": d["text"], "breed": d["breed"]} for d in dataset]

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final, f, indent=2, ensure_ascii=False)
    print(f"\n[6] Сохранено: {output_path} ({len(final)} примеров)")

    report = coverage_report(dataset, TARGET)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"    Отчёт: {report_path}")
    print()
    print(report)


def main():
    print("=" * 60)
    print("ПАЙПЛАЙН ГЕНЕРАЦИИ СИНТЕТИЧЕСКОГО НАБОРА ДАННЫХ")
    print("=" * 60)

    data = load_data(INPUT_FILE)
    dataset = generate_dataset(data)
    dataset = process_data(dataset)
    dataset = filter_by_quality(dataset)
    dataset = remove_duplicates(dataset)

    if len(dataset) < 100:
        print(f"\n    После фильтрации осталось {len(dataset)}, нужно >= 100.")
        print(f"    Добираем до 100...")
        extra_needed = 100 - len(dataset)
        extra = random.sample(data, min(extra_needed, len(data)))
        for ex in extra:
            new_text = make_medium(ex["text"], ex["breed"])
            dataset.append({
                "text": new_text,
                "breed": ex["breed"],
                "animal": get_animal(ex["breed"]),
                "quality": "clean",
                "length": "medium",
            })
        dataset = remove_duplicates(dataset)
        print(f"    Итоговое количество: {len(dataset)}")

    save_results(dataset, OUTPUT_FILE, REPORT_FILE)

    print("\nГОТОВО")


if __name__ == "__main__":
    main()
