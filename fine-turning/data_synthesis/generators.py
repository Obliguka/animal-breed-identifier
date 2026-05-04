import random
from collections import defaultdict

from data_synthesis.config import (
    DOG_BREEDS, CAT_BREEDS, ALL_BREEDS, TARGET, NOISE_PATTERNS, TOTAL_TARGET,
)
from data_synthesis.text_utils import (
    replace_synonyms, shuffle_sentences, split_sentences, extract_breed_features,
)


def get_animal(breed: str) -> str:
    return "dog" if breed in DOG_BREEDS else "cat"


def crossover_sentences(breed_examples: list[dict], breed: str) -> str:
    all_sentences = []
    for ex in breed_examples:
        all_sentences.extend(extract_breed_features(ex["text"]))

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


def _compute_target_counts(total: int) -> dict:
    counts = {}
    for dim, props in TARGET.items():
        counts[dim] = {}
        for category, prop in props.items():
            counts[dim][category] = round(total * prop)
    for dim, props in TARGET.items():
        actual = sum(counts[dim].values())
        if actual < total:
            largest = max(props, key=props.get)
            counts[dim][largest] += total - actual
    return counts


def _assign_quality_and_length() -> list[tuple[str, str]]:
    counts = _compute_target_counts(TOTAL_TARGET)
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

    assignments = _assign_quality_and_length()

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
        available_breeds = [
            b for b in ALL_BREEDS
            if breed_targets[b] > breed_counts[b] and len(breed_examples[b]) > 0
        ]
        if not available_breeds:
            available_breeds = [b for b in ALL_BREEDS if len(breed_examples[b]) > 0]
        if not available_breeds:
            break

        chosen_breed = random.choice(available_breeds)
        source = random.choice(breed_examples[chosen_breed])

        generator = GENERATORS.get((quality, length), make_medium)

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

    print(f"  Сгенерировано: {len(dataset)}")
    return dataset
