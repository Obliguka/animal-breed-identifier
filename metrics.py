import time
import json
from datetime import datetime
import os

class MetricsCollector:
    def __init__(self, log_file="metrics.log"):
        self.log_file = log_file
    
    def log_request(self, endpoint, status, latency_ms, error=None, metadata=None):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "endpoint": endpoint,
            "status": status,
            "latency_ms": round(latency_ms, 2),
            "error": error,
            "metadata": metadata or {}
        }
        
        # Запись в файл
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def get_stats(self):
        if not os.path.exists(self.log_file):
            return {"error": "Нет данных"}
        
        latencies = []
        errors = 0
        total = 0
        
        with open(self.log_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    latencies.append(entry["latency_ms"])
                    total += 1
                    if entry["error"]:
                        errors += 1
                except:
                    continue
        
        if not latencies:
            return {"error": "Нет данных"}
        
        return {
            "total_requests": total,
            "avg_latency_ms": sum(latencies) / len(latencies),
            "p95_latency_ms": sorted(latencies)[int(len(latencies)*0.95)],
            "error_rate": (errors / total * 100) if total > 0 else 0,
            "success_rate": ((total - errors) / total * 100) if total > 0 else 0
        }

metrics = MetricsCollector()