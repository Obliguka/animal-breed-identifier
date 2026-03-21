import requests
import json
import os
import time
from datetime import datetime

class APITester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.results = []
    
    def normalize(self, text):
        if not text:
            return ""
        return " ".join(str(text).lower().strip().split())
    
    def is_match(self, expected, predicted):
        if not expected or not predicted:
            return False
        exp = self.normalize(expected)
        pred = self.normalize(predicted)
        return exp in pred or pred in exp
    
    
    def test_image(self, image_path, expected=None):
        try:
            with open(image_path, 'rb') as f:
                files = {'file': (os.path.basename(image_path), f, 'image/jpeg')}
                start_time = time.time()
                response = requests.post(f"{self.base_url}/predict", files=files)
                latency = time.time() - start_time
                
                return {
                    'success': response.status_code == 200,
                    'status_code': response.status_code,
                    'response': response.json() if response.status_code == 200 else response.text,
                    'latency': round(latency, 3),
                    'expected': expected
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'expected': expected
            }
    
    def test_text(self, query, expected=None):
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/predict/text",
                json={"description": query}
            )
            latency = time.time() - start_time
            
            return {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'response': response.json() if response.status_code == 200 else response.text,
                'latency': round(latency, 3),
                'query': query,
                'expected': expected
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'query': query,
                'expected': expected
            }
    
    def run_tests(self, test_file="test_data/test_queries.json"):
        with open(test_file, 'r', encoding='utf-8') as f:
            tests = json.load(f)
        
        for i, test in enumerate(tests, 1):
            print(f" Тест {i}/{len(tests)}: ", end="")
            
            if test['type'] == 'image':
                image_path = os.path.join("test_data", test['file'])
                result = self.test_image(image_path, {
                    'animal': test.get('expected_animal'),
                    'breed': test.get('expected_breed')
                })
                result['query_raw'] = test['file']
                
            elif test['type'] == 'text':
                result = self.test_text(test['query'], {
                    'animal': test.get('expected_animal'),
                    'breed': test.get('expected_breed')
                })
                result['query_raw'] = test['query']
            
            result['test_id'] = test['id']
            result['test_type'] = test['type']
            result['timestamp'] = datetime.now().isoformat()
            self.results.append(result)
            
            status = "OK" if result['success'] else "FALSE"
            print(f"{status} ({result.get('latency', 'N/A')} сек)")
        
        self.save_results()
        return self.results
    
    def save_results(self, filename="test_results/results_15.txt"):
        os.makedirs("test_results", exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"{'ID':<5} {'Тип':<6} {'Запрос':<50} {'Ожидаемый вид':<18} {'Ожидаемая порода':<22} "
                    f"{'Результат (animal)':<18} {'Результат (breed)':<20} {'Успех':<6} "
                    f"{'Время (сек)':<10} {'Совп. вида':<10} {'Совп. породы':<12}\n")
            f.write("-" * 200 + "\n")
            
            for r in self.results:
                response_data = r.get('response', {})
                if isinstance(response_data, dict):
                    result_animal = response_data.get('animal', '')
                    result_breed = response_data.get('breed', '')
                else:
                    result_animal = ''
                    result_breed = ''
                
                expected = r.get('expected', {})
                query_display = r.get('query_raw', '')
                if len(str(query_display)) > 48:
                    query_display = str(query_display)[:45] + "..."
                
                animal_match = self.is_match(expected.get('animal', ''), result_animal)
                breed_match = self.is_match(expected.get('breed', ''), result_breed)
                
                f.write(f"{r.get('test_id', ''):<5} "
                        f"{r.get('test_type', ''):<6} "
                        f"{str(query_display):<50} "
                        f"{expected.get('animal', ''):<18} "
                        f"{expected.get('breed', ''):<22} "
                        f"{result_animal:<18} "
                        f"{result_breed:<20} "
                        f"{'OK' if r['success'] else 'FALSE':<6} "
                        f"{r.get('latency', ''):<10} "
                        f"{'OK' if animal_match else 'FALSE':<10} "
                        f"{'OK' if breed_match else 'FALSE':<12}\n")
        
        print(f"\n Результаты сохранены в {filename}")
        

if __name__ == "__main__":
    os.makedirs("test_data", exist_ok=True)
    os.makedirs("test_results", exist_ok=True)
    
    tester = APITester()
    results = tester.run_tests()