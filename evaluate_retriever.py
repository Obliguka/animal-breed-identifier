

import json
import os
from retriever import retriever

#метрики
def precision_at_k(relevant, retrieved, k=3):
    if not retrieved or k == 0:
        return 0.0
    retrieved_at_k = set(retrieved[:k])
    relevant_set = set(relevant)
    return len(retrieved_at_k & relevant_set) / k


def recall_at_k(relevant, retrieved, k=3):
    if not relevant:
        return 0.0
    retrieved_at_k = set(retrieved[:k])
    relevant_set = set(relevant)
    return len(retrieved_at_k & relevant_set) / len(relevant_set)


def mrr(relevant, retrieved):
    for i, breed in enumerate(retrieved, 1):
        if breed in relevant:
            return 1.0 / i
    return 0.0


def ndcg_at_k(relevant_scores, retrieved, k=3):
    if not retrieved or k == 0:
        return 0.0
    
    dcg = 0.0
    for i, breed in enumerate(retrieved[:k], 1):
        score = relevant_scores.get(breed, 0)
        dcg += score / (i + 1) 
    
    ideal_scores = sorted(relevant_scores.values(), reverse=True)[:k]
    idcg = 0.0
    for i, score in enumerate(ideal_scores, 1):
        idcg += score / (i + 1)
    
    return dcg / idcg if idcg > 0 else 0.0

#тестовые данные
def create_test_set():
    test_set = [
        {
            "id": 1,
            "query": "pointed ears, thick coat, wolf-like face, blue eyes",
            "animal_type": "dog",
            "relevant_breeds": ["husky"],
            "partially_relevant": ["alaskan malamute", "samoyed"],
            "source": "photo_husky"
        },
        {
            "id": 2,
            "query": "floppy ears, short dense coat, otter tail",
            "animal_type": "dog",
            "relevant_breeds": ["labrador"],
            "partially_relevant": ["golden retriever"],
            "source": "photo_labrador"
        },
        {
            "id": 3,
            "query": "pointed ears, black and tan coat, strong build",
            "animal_type": "dog",
            "relevant_breeds": ["german shepherd"],
            "partially_relevant": ["belgian malinois"],
            "source": "photo_german_shepherd"
        },
        {
            "id": 4,
            "query": "short legs, long body, pointed ears, fluffy coat",
            "animal_type": "dog",
            "relevant_breeds": ["corgi"],
            "partially_relevant": ["dachshund"],
            "source": "photo_corgi"
        },
        {
            "id": 5,
            "query": "very long body, short legs, floppy ears",
            "animal_type": "dog",
            "relevant_breeds": ["dachshund"],
            "partially_relevant": ["corgi"],
            "source": "photo_dachshund"
        },
        {
            "id": 6,
            "query": "wrinkled face, short legs, pushed-in nose",
            "animal_type": "dog",
            "relevant_breeds": ["bulldog"],
            "partially_relevant": ["pug"],
            "source": "photo_bulldog"
        },
        {
            "id": 7,
            "query": "sleek, pointed ears, black and tan coat",
            "animal_type": "dog",
            "relevant_breeds": ["doberman"],
            "partially_relevant": ["rottweiler"],
            "source": "photo_doberman"
        },
        {
            "id": 8,
            "query": "muscular, black with tan markings",
            "animal_type": "dog",
            "relevant_breeds": ["rottweiler"],
            "partially_relevant": ["doberman"],
            "source": "photo_rottweiler"
        },
        {
            "id": 9,
            "query": "white fluffy coat, smiling face, curled tail",
            "animal_type": "dog",
            "relevant_breeds": ["samoyed"],
            "partially_relevant": ["american eskimo"],
            "source": "photo_samoyed"
        },
        {
            "id": 10,
            "query": "floppy ears, short tricolor coat",
            "animal_type": "dog",
            "relevant_breeds": ["beagle"],
            "partially_relevant": ["basset hound"],
            "source": "photo_beagle"
        },
        {
            "id": 11,
            "query": "fox-like, pointed ears, curled tail",
            "animal_type": "dog",
            "relevant_breeds": ["shiba inu"],
            "partially_relevant": ["akita"],
            "source": "photo_shiba"
        },
        {
            "id": 12,
            "query": "large, wolf-like, thick coat, curled tail",
            "animal_type": "dog",
            "relevant_breeds": ["alaskan malamute"],
            "partially_relevant": ["husky"],
            "source": "photo_malamute"
        },
        
        {
            "id": 13,
            "query": "very large, long thick coat, tufted ears, bushy tail",
            "animal_type": "cat",
            "relevant_breeds": ["maine coon"],
            "partially_relevant": ["siberian"],
            "source": "photo_maine_coon"
        },
        {
            "id": 14,
            "query": "slender, short coat, pointed color pattern, blue eyes",
            "animal_type": "cat",
            "relevant_breeds": ["siamese"],
            "partially_relevant": ["tonkinese"],
            "source": "photo_siamese"
        },
        {
            "id": 15,
            "query": "flat face, very long fluffy coat",
            "animal_type": "cat",
            "relevant_breeds": ["persian"],
            "partially_relevant": ["exotic shorthair"],
            "source": "photo_persian"
        },
        {
            "id": 16,
            "query": "hairless, wrinkled skin, large ears",
            "animal_type": "cat",
            "relevant_breeds": ["sphynx"],
            "partially_relevant": ["donskoy"],
            "source": "photo_sphynx"
        },
        {
            "id": 17,
            "query": "round face, dense short coat, chunky build",
            "animal_type": "cat",
            "relevant_breeds": ["british shorthair"],
            "partially_relevant": ["chartreux"],
            "source": "photo_british"
        },
        {
            "id": 18,
            "query": "folded ears, round face",
            "animal_type": "cat",
            "relevant_breeds": ["scottish fold"],
            "partially_relevant": [],
            "source": "photo_scottish"
        },
        {
            "id": 19,
            "query": "large, blue eyes, semi-long coat, floppy when held",
            "animal_type": "cat",
            "relevant_breeds": ["ragdoll"],
            "partially_relevant": ["birman"],
            "source": "photo_ragdoll"
        },
        {
            "id": 20,
            "query": "large, thick triple coat, tufted ears",
            "animal_type": "cat",
            "relevant_breeds": ["siberian"],
            "partially_relevant": ["maine coon"],
            "source": "photo_siberian"
        },
        {
            "id": 21,
            "query": "short blue-gray coat, green eyes",
            "animal_type": "cat",
            "relevant_breeds": ["russian blue"],
            "partially_relevant": ["chartreux"],
            "source": "photo_russian_blue"
        },
        
        {
            "id": 22,
            "query": "pointed ears, thick coat, wolf-like face, brown eyes",
            "animal_type": "dog",
            "relevant_breeds": ["alaskan malamute"],
            "partially_relevant": ["husky"],
            "source": "edge_malamute_vs_husky"
        },
        {
            "id": 23,
            "query": "short legs, long body",
            "animal_type": "dog",
            "relevant_breeds": ["dachshund"],
            "partially_relevant": ["corgi"],
            "source": "edge_dachshund_vs_corgi"
        },
        {
            "id": 24,
            "query": "large, tufted ears, long coat",
            "animal_type": "cat",
            "relevant_breeds": ["maine coon"],
            "partially_relevant": ["siberian"],
            "source": "edge_maine_coon_vs_siberian"
        },
        
        {
            "id": 25,
            "query": "fluffy ginger cat with tufted ears, very large",
            "animal_type": "cat",
            "relevant_breeds": ["maine coon"],
            "partially_relevant": ["siberian"],
            "source": "text_maine_coon"
        },
        {
            "id": 26,
            "query": "white fluffy medium-sized dog with black eyes, looks like a fox",
            "animal_type": "dog",
            "relevant_breeds": ["samoyed"],
            "partially_relevant": ["american eskimo"],
            "source": "text_samoyed"
        },
        {
            "id": 27,
            "query": "small dog with long body and short legs",
            "animal_type": "dog",
            "relevant_breeds": ["dachshund"],
            "partially_relevant": ["corgi"],
            "source": "text_dachshund"
        },
        {
            "id": 28,
            "query": "hairless cat with wrinkled skin and big ears",
            "animal_type": "cat",
            "relevant_breeds": ["sphynx"],
            "partially_relevant": [],
            "source": "text_sphynx"
        },
        {
            "id": 29,
            "query": "dog with black and tan color, pointy ears, short coat",
            "animal_type": "dog",
            "relevant_breeds": ["doberman"],
            "partially_relevant": ["rottweiler"],
            "source": "text_doberman"
        }
    ]
    
    return test_set

def evaluate_retriever():

    test_set = create_test_set()
    
    results = {
        "precision@3": [],
        "recall@3": [],
        "mrr": [],
        "ndcg@3": []
    }
    
    
    # Прогоняем каждый тест
    for test in test_set:
        query = test["query"]
        animal_type = test.get("animal_type")
        
        # Получаем результат от ретривера
        retrieved = retriever.retrieve(query, animal_type, top_k=3)
        retrieved_names = [b["name"] for b in retrieved]
        
        relevant_scores = {}
        for breed in test.get("relevant_breeds", []):
            relevant_scores[breed] = 2
        for breed in test.get("partially_relevant", []):
            relevant_scores[breed] = 1
        
        # Расчёт метрик
        p_at_3 = precision_at_k(test["relevant_breeds"], retrieved_names, k=3)
        r_at_3 = recall_at_k(test["relevant_breeds"], retrieved_names, k=3)
        mrr_score = mrr(test["relevant_breeds"], retrieved_names)
        ndcg_score = ndcg_at_k(relevant_scores, retrieved_names, k=3)
        
        results["precision@3"].append(p_at_3)
        results["recall@3"].append(r_at_3)
        results["mrr"].append(mrr_score)
        results["ndcg@3"].append(ndcg_score)
        
    
  
    avg_precision = sum(results["precision@3"]) / len(results["precision@3"])
    avg_recall = sum(results["recall@3"]) / len(results["recall@3"])
    avg_mrr = sum(results["mrr"]) / len(results["mrr"])
    avg_ndcg = sum(results["ndcg@3"]) / len(results["ndcg@3"])
    

    
    # Сохраняем результаты в файл
    output = {
        "test_set_size": len(test_set),
        "metrics": {
            "precision@3": round(avg_precision * 100, 1),
            "recall@3": round(avg_recall * 100, 1),
            "mrr": round(avg_mrr, 3),
            "ndcg@3": round(avg_ndcg, 3)
        },
        "individual_results": [
            {
                "id": test["id"],
                "source": test["source"],
                "precision@3": round(results["precision@3"][i] * 100, 1),
                "recall@3": round(results["recall@3"][i] * 100, 1),
                "mrr": round(results["mrr"][i], 3),
                "ndcg@3": round(results["ndcg@3"][i], 3)
            }
            for i, test in enumerate(test_set)
        ]
    }
    
    with open("test_results/retriever_evaluation.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    
    return output

if __name__ == "__main__":
    os.makedirs("test_results", exist_ok=True)
    evaluate_retriever()