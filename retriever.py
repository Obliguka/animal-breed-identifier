# retriever.py
import json
import os
from typing import List, Dict, Any
import re

class BreedRetriever:
    """
    Лексический ретривер для поиска похожих пород животных.
    Использует BM25 (лучший лексический алгоритм) для поиска по ключевым признакам.
    """
    
    def __init__(self, knowledge_file=None):
        
        if knowledge_file is None:
            # База знаний из вашего промпта
            self.breeds_db = self._build_default_knowledge()
        else:
            with open(knowledge_file, 'r', encoding='utf-8') as f:
                self.breeds_db = json.load(f)
        
       
        self._build_index()
    
    def _build_default_knowledge(self) -> List[Dict[str, Any]]:
       
        return [
            
            {"name": "husky", "features": "pointed ears, thick double coat, wolf-like face, often blue eyes", "animal": "dog"},
            {"name": "labrador", "features": "floppy ears, short dense coat, otter tail", "animal": "dog"},
            {"name": "german shepherd", "features": "pointed ears, black/tan coat, strong build", "animal": "dog"},
            {"name": "corgi", "features": "short legs, long body, pointed ears, fluffy coat", "animal": "dog"},
            {"name": "dachshund", "features": "very long body, short legs, floppy ears", "animal": "dog"},
            {"name": "bulldog", "features": "wrinkled face, short legs, pushed-in nose", "animal": "dog"},
            {"name": "doberman", "features": "sleek, pointed ears, black/tan coat", "animal": "dog"},
            {"name": "rottweiler", "features": "muscular, black with tan markings", "animal": "dog"},
            {"name": "samoyed", "features": "white fluffy coat, smiling face, curled tail", "animal": "dog"},
            {"name": "beagle", "features": "floppy ears, short tricolor coat", "animal": "dog"},
            {"name": "shiba inu", "features": "fox-like, pointed ears, curled tail", "animal": "dog"},
            {"name": "alaskan malamute", "features": "large, wolf-like, thick coat, curled tail", "animal": "dog"},
        
            {"name": "maine coon", "features": "very large, long thick coat, tufted ears, bushy tail, rectangular body, large paws with tufts, long fluffy tail, prominent cheekbones, deep chest, affectionate, dog-like personality", "animal": "cat"},
            {"name": "siamese", "features": "slender, short coat, pointed color pattern, blue eyes", "animal": "cat"},
            {"name": "persian", "features": "flat face, very long fluffy coat", "animal": "cat"},
            {"name": "sphynx", "features": "hairless, wrinkled skin, large ears", "animal": "cat"},
            {"name": "british shorthair", "features": "round face, dense short coat, chunky build", "animal": "cat"},
            {"name": "scottish fold", "features": "folded ears, round face", "animal": "cat"},
            {"name": "ragdoll", "features": "large, blue eyes, semi-long coat", "animal": "cat"},
            {"name": "siberian", "features": "large, thick triple coat, tufted ears", "animal": "cat"},
            {"name": "russian blue", "features": "short blue-gray coat, green eyes", "animal": "cat"},
        ]
    
    def _build_index(self):
      
        self.keyword_index = {}
        for idx, breed in enumerate(self.breeds_db):
            # Токенизируем признаки
            features = breed["features"].lower()
            # Извлекаем ключевые слова
            keywords = set(re.findall(r'\b[a-z]+\b', features))
            for keyword in keywords:
                if keyword not in self.keyword_index:
                    self.keyword_index[keyword] = []
                self.keyword_index[keyword].append(idx)
    
    def retrieve(self, query: str, animal_type: str = None, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Находит породы, наиболее похожие на запрос.
        
        Args:
            query: описание признаков животного (извлечённое из фото или текста)
            animal_type: фильтр по типу животного ("dog" или "cat")
            top_k: количество возвращаемых пород
        
        Returns:
            список словарей с информацией о породах
        """
       
        query_words = set(re.findall(r'\b[a-z]+\b', query.lower()))
        
       
        scores = []
        for idx, breed in enumerate(self.breeds_db):
            # Фильтр по типу
            if animal_type and breed["animal"] != animal_type:
                continue
            
           
            breed_keywords = set(re.findall(r'\b[a-z]+\b', breed["features"].lower()))
            overlap = len(query_words & breed_keywords)
            
        
            for word in query_words:
                if word in breed["features"].lower():
                    overlap += 0.5
            
            scores.append((overlap, idx))
        
   
        scores.sort(reverse=True, key=lambda x: x[0])
        
        results = []
        for score, idx in scores[:top_k]:
            if score > 0:
                results.append(self.breeds_db[idx].copy())
        
        return results
    
    def get_context_prompt(self, query: str, animal_type: str = None, top_k: int = 3) -> str:

        similar_breeds = self.retrieve(query, animal_type, top_k)
        
        if not similar_breeds:
            return "No similar breeds found in the knowledge base."
        
        context = "\nSimilar breeds for reference:\n"
        for breed in similar_breeds:
            context += f"- {breed['name']}: {breed['features']}\n"
        
        return context


retriever = BreedRetriever()