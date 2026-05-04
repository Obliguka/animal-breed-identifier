from collections import Counter

from data_synthesis.config import DOG_BREEDS, CAT_BREEDS, ALL_BREEDS, TARGET


def coverage_report(dataset: list[dict], target: dict | None = None) -> str:
    if target is None:
        target = TARGET

    lines = []
    lines.append("COVERAGE REPORT")
    lines.append(f"Всего: {len(dataset)}")
    lines.append("")

    animal_counts = Counter(d["animal"] for d in dataset)
    lines.append("--- animal ---")
    for animal in ["dog", "cat"]:
        actual = animal_counts.get(animal, 0)
        expected_pct = target["animal"].get(animal, 0)
        expected = round(len(dataset) * expected_pct)
        status = "OK" if abs(actual - expected) / max(expected, 1) < 0.15 else "ОТКЛОНЕНИЕ"
        lines.append(f"  {animal:20s}: {actual:3d} (~{expected}, {expected_pct*100:.0f}%) [{status}]")
    lines.append("")

    quality_counts = Counter(d["quality"] for d in dataset)
    lines.append("--- quality ---")
    for q in ["clean", "noisy"]:
        actual = quality_counts.get(q, 0)
        expected_pct = target["quality"].get(q, 0)
        expected = round(len(dataset) * expected_pct)
        status = "OK" if abs(actual - expected) / max(expected, 1) < 0.20 else "ОТКЛОНЕНИЕ"
        lines.append(f"  {q:20s}: {actual:3d} (~{expected}, {expected_pct*100:.0f}%) [{status}]")
    lines.append("")

    length_counts = Counter(d["length"] for d in dataset)
    lines.append("--- length ---")
    for l in ["short", "medium", "long"]:
        actual = length_counts.get(l, 0)
        expected_pct = target["length"].get(l, 0)
        expected = round(len(dataset) * expected_pct)
        status = "OK" if abs(actual - expected) / max(expected, 1) < 0.25 else "ОТКЛОНЕНИЕ"
        lines.append(f"  {l:20s}: {actual:3d} (~{expected}, {expected_pct*100:.0f}%) [{status}]")
    lines.append("")

    breed_counts = Counter(d["breed"] for d in dataset)
    lines.append("--- breed ---")
    dog_total = sum(breed_counts[b] for b in DOG_BREEDS)
    cat_total = sum(breed_counts[b] for b in CAT_BREEDS)
    target_per_dog = max(round(dog_total / len(DOG_BREEDS)), 1)
    target_per_cat = max(round(cat_total / len(CAT_BREEDS)), 1)

    for breed in ALL_BREEDS:
        actual = breed_counts.get(breed, 0)
        exp = target_per_dog if breed in DOG_BREEDS else target_per_cat
        status = "OK" if abs(actual - exp) / max(exp, 1) < 0.4 else "МАЛО"
        lines.append(f"  {breed:25s}: {actual:3d} (~{exp}) [{status}]")
    lines.append("")

    n_covered = sum(1 for b in ALL_BREEDS if breed_counts.get(b, 0) > 0)
    lines.append(f"Пород: {n_covered}/{len(ALL_BREEDS)}")

    return "\n".join(lines)
