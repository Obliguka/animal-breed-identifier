#!/usr/bin/env python3

import json
import random
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from data_synthesis.config import DEFAULT_INPUT, DEFAULT_OUTPUT, DEFAULT_REPORT, TARGET
from data_synthesis.generators import generate_dataset
from data_synthesis.filters import process_data, filter_by_quality, remove_duplicates, ensure_minimum_count
from data_synthesis.report import coverage_report

random.seed(42)


def load_data(path: str) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"[1] Загружено: {len(data)}")
    return data


def save_results(dataset: list[dict], output_path: str, report_path: str):
    final = [{"text": d["text"], "breed": d["breed"]} for d in dataset]

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final, f, indent=2, ensure_ascii=False)

    report = coverage_report(dataset, TARGET)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(report)


def main():

    data = load_data(DEFAULT_INPUT)
    dataset = generate_dataset(data)
    dataset = process_data(dataset)
    dataset = filter_by_quality(dataset)
    dataset = remove_duplicates(dataset)
    dataset = ensure_minimum_count(dataset, data, min_count=100)
    save_results(dataset, DEFAULT_OUTPUT, DEFAULT_REPORT)


if __name__ == "__main__":
    main()
