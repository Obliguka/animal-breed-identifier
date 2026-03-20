import requests
import json

with open("test_data/test_queries.json", "r", encoding="utf-8") as f:
    tests = json.load(f)


results = []

for test in tests:
    if test['type'] == 'image':
        with open(f"test_data/{test['file']}", 'rb') as f:
            response = requests.post(
                "http://localhost:8000/predict",
                files={'file': f}
            )
    else:
        response = requests.post(
            "http://localhost:8000/predict/text",
            json={"description": test['query']}
        )
    
    results.append({
        "запрос": test['query'] if test['type'] == 'text' else test['file'],
        "результат": response.json()
    })

with open("test_results/summary_table.txt", "w", encoding="utf-8") as f:
    f.write(f"{'ЗАПРОС':<50} РЕЗУЛЬТАТ\n")
    f.write("-"*90 + "\n")
    for item in results:
        f.write(f"{str(item['запрос']):<50} {item['результат']}\n")
