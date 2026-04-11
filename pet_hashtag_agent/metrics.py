# metrics.py
# Метрики для оценки агента

def tool_selection_accuracy(results):
    correct = sum(1 for r in results if r["tool_correct"])
    return (correct / len(results)) * 100

def breed_identification_accuracy(results):
    breed_results = [r for r in results if r["expected_tool"] == "identify_pet" and not r["hitl"]]
    if not breed_results:
        return 0
    correct = sum(1 for r in breed_results if r["breed_correct"])
    return (correct / len(breed_results)) * 100

def hitl_rate(results):
    hitl_count = sum(1 for r in results if r["hitl"])
    return (hitl_count / len(results)) * 100

def avg_response_time(results):
    times = [r["latency"] for r in results]
    return sum(times) / len(times)

def all_metrics(results):
    return {
        "tool_selection_accuracy": round(tool_selection_accuracy(results), 1),
        "breed_identification_accuracy": round(breed_identification_accuracy(results), 1),
        "hitl_rate": round(hitl_rate(results), 1),
        "avg_response_time_sec": round(avg_response_time(results), 3)
    }