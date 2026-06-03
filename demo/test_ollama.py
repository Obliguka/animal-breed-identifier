import requests

prompt = "a fluffy white dog with a curled tail and smiling face. What breed is this? Answer in JSON: {'animal': 'dog', 'breed': 'name'}"

r = requests.post("http://localhost:11434/api/generate", json={
    "model": "tinyllama",
    "prompt": prompt,
    "stream": False,
}, timeout=60)

print(f"STATUS: {r.status_code}")
data = r.json()
print("RESPONSE:", data.get("response", ""))
