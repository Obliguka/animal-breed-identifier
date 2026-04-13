import time
import json
import os
import requests
from agent import SimpleAgent

API_URL = "http://localhost:8001/predict"
PHOTOS_DIR = "photo"

def normalize(text):
    if not text:
        return ""
    return " ".join(str(text).lower().strip().split())

def evaluate():
    from test_photos_suite import photo_hashtag_tests, text_only_tests
    
    agent = SimpleAgent()
    
    complex_results = []
    
    for test in photo_hashtag_tests:
        image_path = os.path.join(PHOTOS_DIR, test["file"])
        
        if not os.path.exists(image_path):
            print(f"[{test['id']}] Файл не найден: {test['file']}")
            continue

        start = time.time()
        with open(image_path, 'rb') as f:
            response = requests.post(API_URL, files={'file': f})
        latency1 = time.time() - start
        
        if response.status_code != 200:
            print(f"[{test['id']}] Ошибка API: {response.status_code}")
            continue
        
        breed_from_photo = response.json().get("breed", "")
        animal_from_photo = response.json().get("animal", "")

        start = time.time()
        agent_response = agent.think_and_act_with_context(
            test["query"], 
            known_breed=breed_from_photo,
            known_animal=animal_from_photo
        )
        latency2 = time.time() - start
        
        response_str = str(agent_response).lower()
        expected = normalize(test["expected_breed"])
        
        is_correct = expected in response_str
        
        complex_results.append({
            "id": test["id"],
            "file": test["file"],
            "expected_breed": test["expected_breed"],
            "detected_breed": breed_from_photo,
            "hashtags_response": str(agent_response),
            "correct": is_correct,
            "latency_breed": round(latency1, 3),
            "latency_hashtags": round(latency2, 3),
        })
        
        status = "+" if is_correct else "-"
        print(f"[{test['id']}] {status} {test['file']} -> порода: {breed_from_photo} -> хештеги: {str(agent_response)[:50]}... ({latency1+latency2:.3f} сек)")
    
    
    text_results = []
    
    for query in text_only_tests:
        start = time.time()
        response = agent.think_and_act(query["input"])
        latency = time.time() - start
        
        response_str = str(response)
        
        if "total_requests" in response_str:
            tool_called = "get_user_stats"
            tool_correct = (query.get("expected_tool") == tool_called)
        elif "Я не понял" in response_str or "передан оператору" in response_str:
            tool_called = "hitl"
            tool_correct = query.get("expected_hitl", False)
        else:
            tool_called = "unknown"
            tool_correct = False
        
        text_results.append({
            "id": query["id"],
            "input": query["input"],
            "expected": "hitl" if query.get("expected_hitl") else query.get("expected_tool"),
            "called": tool_called,
            "correct": tool_correct,
            "latency": round(latency, 3),
        })
        
        status = "+" if tool_correct else "-"
        print(f"[{query['id']}] {status} {query['input'][:40]} -> {tool_called} ({latency:.3f} сек)")

    
    """total_complex = len(complex_results)
    correct_complex = sum(1 for r in complex_results if r["correct"])
    total_text = len(text_results)
    correct_text = sum(1 for r in text_results if r["correct"])
    all_latencies = [r.get("latency_breed", 0) + r.get("latency_hashtags", 0) for r in complex_results] + [r["latency"] for r in text_results]
    avg_latency = sum(all_latencies) / len(all_latencies) if all_latencies else 0
    tool_selection_results = [r for r in text_results if r["expected"] != "hitl"]
    tool_correct = sum(1 for r in tool_selection_results if r["correct"])
    tool_total = len(tool_selection_results)
    hitl_results = [r for r in text_results if r["expected"] == "hitl"]
    hitl_correct = sum(1 for r in hitl_results if r["correct"])
    hitl_total = len(hitl_results)  """

    total_complex = len(complex_results)
    correct_complex = sum(1 for r in complex_results if r["correct"])
    total_text = len(text_results)
    correct_text = sum(1 for r in text_results if r["correct"])
    all_latencies = [r.get("latency_breed", 0) + r.get("latency_hashtags", 0) for r in complex_results] + [r["latency"] for r in text_results]
    avg_latency = sum(all_latencies) / len(all_latencies) if all_latencies else 0
    
    tool_selection_results = [r for r in text_results if r["expected"] != "hitl"]
    tool_correct = sum(1 for r in tool_selection_results if r["correct"])
    tool_total = len(tool_selection_results)
    
    hitl_results = [r for r in text_results if r["expected"] == "hitl"]
    hitl_correct = sum(1 for r in hitl_results if r["correct"])
    hitl_total = len(hitl_results)

    print("РЕЗУЛЬТАТЫ ОЦЕНКИ АГЕНТА")
    print(f"1. Точность определения породы (фото + хештеги): {correct_complex}/{total_complex} ({correct_complex/total_complex*100:.1f}%)")

    if tool_total > 0:
        print(f"2. Точность выбора инструмента (статистика): {tool_correct}/{tool_total} ({tool_correct/tool_total*100:.1f}%)")
    else:
        print("2. Точность выбора инструмента (статистика): нет данных")
    
    if hitl_total > 0:
        print(f"3. Human-in-the-Loop (неизвестные запросы): {hitl_correct}/{hitl_total} ({hitl_correct/hitl_total*100:.1f}%)")
    else:
        print("3. Human-in-the-Loop (неизвестные запросы): нет данных")
    
    print(f"4. Среднее время ответа: {avg_latency:.3f} сек")
    

if __name__ == "__main__":
    os.makedirs("test_results", exist_ok=True)
    evaluate()