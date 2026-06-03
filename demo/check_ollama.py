import requests
url = "http://host.docker.internal:11434/api/tags"
try:
    r = requests.get(url, timeout=5)
    print(f"STATUS: {r.status_code}")
    data = r.json()
    for m in data.get("models", []):
        print(f"  MODEL: {m.get('name', '?')}")
except Exception as e:
    print(f"ERROR: {e}")
