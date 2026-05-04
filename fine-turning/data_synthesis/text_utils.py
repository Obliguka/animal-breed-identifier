import random
import re


def replace_synonyms(text: str) -> str:
    from data_synthesis.config import SYNONYMS

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


def extract_breed_features(text: str) -> list[str]:
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


def text_similarity(a: str, b: str) -> float:
    words_a = set(a.lower().split())
    words_b = set(b.lower().split())
    if not words_a or not words_b:
        return 0.0
    intersection = words_a & words_b
    union = words_a | words_b
    return len(intersection) / len(union)
