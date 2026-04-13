# Комплексные тесты: фото + запрос на хештеги

photo_hashtag_tests = [
    {"id": 1, "file": "husky1.jpg", "expected_breed": "husky", "query": "Сделай хештеги для Instagram"},
    {"id": 2, "file": "labrador1.jpg", "expected_breed": "labrador", "query": "Сгенерируй хештеги для TikTok"},
    {"id": 3, "file": "german_shepherd1.jpg", "expected_breed": "german shepherd", "query": "Нужны хештеги для поста"},
    {"id": 4, "file": "corgi1.jpg", "expected_breed": "corgi", "query": "Сделай хештеги для моего питомца"},
    {"id": 5, "file": "dachshund1.jpg", "expected_breed": "dachshund", "query": "Хештеги для Instagram"},
    {"id": 6, "file": "bulldog_1.jpg", "expected_breed": "bulldog", "query": "Сгенерируй хештеги"},
    {"id": 7, "file": "samoyed_1.jpg", "expected_breed": "samoyed", "query": "Сделай хештеги для TikTok"},
    {"id": 8, "file": "beagle_1.jpg", "expected_breed": "beagle", "query": "Нужны хештеги"},
    {"id": 9, "file": "shiba_inu_1.jpg", "expected_breed": "shiba inu", "query": "Хештеги для Instagram"},
    {"id": 10, "file": "rottweiler_1.jpg", "expected_breed": "rottweiler", "query": "Сделай хештеги"},
    {"id": 11, "file": "mainecoon1.jpg", "expected_breed": "maine coon", "query": "Сгенерируй хештеги для Instagram"},
    {"id": 12, "file": "siamese_1.jpg", "expected_breed": "siamese", "query": "Нужны хештеги для поста"},
    {"id": 13, "file": "persian_1.jpg", "expected_breed": "persian", "query": "Сделай хештеги для TikTok"},
    {"id": 14, "file": "sphynx1.jpg", "expected_breed": "sphynx", "query": "Хештеги для Instagram"},
    {"id": 15, "file": "british_shorthair1.jpg", "expected_breed": "british shorthair", "query": "Сгенерируй хештеги"},
    {"id": 16, "file": "scottish_fold_1.jpg", "expected_breed": "scottish fold", "query": "Сделай хештеги"},
    {"id": 17, "file": "ragdoll_1.jpg", "expected_breed": "ragdoll", "query": "Нужны хештеги для Instagram"},
    {"id": 18, "file": "siberian_cat1.jpg", "expected_breed": "siberian", "query": "Хештеги для TikTok"},
    {"id": 19, "file": "russian_blue_1.jpg", "expected_breed": "russian blue", "query": "Сделай хештеги для Instagram"},
    {"id": 20, "file": "bengal_1.jpg", "expected_breed": "bengal", "query": "Сгенерируй хештеги"},
]

# Отдельные тесты для проверки других сценариев
text_only_tests = [
    {"id": 101, "input": "Покажи мою статистику", "expected_tool": "get_user_stats"},
    {"id": 102, "input": "Сколько запросов я сделал?", "expected_tool": "get_user_stats"},
    {"id": 103, "input": "Как испечь пиццу?", "expected_tool": None, "expected_hitl": True},
]