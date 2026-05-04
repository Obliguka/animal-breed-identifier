TOTAL_TARGET = 150

DOG_BREEDS = [
    "husky", "labrador", "german shepherd", "corgi", "dachshund",
    "bulldog", "samoyed", "beagle", "shiba inu", "rottweiler",
]

CAT_BREEDS = [
    "maine coon", "siamese", "persian", "sphynx", "british shorthair",
    "scottish fold", "ragdoll", "siberian", "russian blue", "bengal",
]

ALL_BREEDS = DOG_BREEDS + CAT_BREEDS

TARGET = {
    "animal": {"dog": 0.5, "cat": 0.5},
    "quality": {"clean": 0.7, "noisy": 0.3},
    "length": {"short": 0.4, "medium": 0.4, "long": 0.2},
}

SYNONYMS = {
    "pointed ears": ["erect ears", "upright ears", "straight ears", "standing ears", "perky ears"],
    "floppy ears": ["drooping ears", "pendulous ears", "hanging ears", "long ears", "soft ears"],
    "short coat": ["short fur", "smooth coat", "close-lying coat", "low-maintenance coat", "fine coat"],
    "fluffy coat": ["fluffy fur", "thick coat", "plush coat", "dense coat", "plushy fur"],
    "long coat": ["long fur", "flowing coat", "silky coat", "lengthy coat", "luxurious coat"],
    "bushy tail": ["fluffy tail", "thick tail", "plumed tail", "full tail", "feathery tail"],
    "curled tail": ["curved tail", "spiral tail", "coiled tail", "curling tail", "ring tail"],
    "muscular build": ["athletic build", "powerful build", "strong body", "robust physique", "sturdy frame"],
    "wolf-like face": ["fox-like face", "pointed face", "triangular face", "angular face", "tapered face"],
    "large eyes": ["big eyes", "expressive eyes", "wide eyes", "prominent eyes", "striking eyes"],
    "blue eyes": ["pale eyes", "icy eyes", "bright blue eyes", "glacial eyes"],
    "wrinkled skin": ["loose skin", "folded skin", "wrinkly face", "creased skin", "puckered skin"],
    "thick double coat": ["heavy double coat", "dense undercoat", "insulating coat", "weather-resistant coat"],
    "short legs": ["stubby legs", "tiny legs", "low-set legs", "short limbs"],
    "long legs": ["tall legs", "lengthy limbs", "extended legs", "long limbs"],
    "white muzzle": ["pale muzzle", "light snout", "white snout region", "light-colored muzzle"],
    "black and tan": ["dark and tan", "brown and black", "rich black and rust", "ebony and tan"],
    "curled tail over back": ["tail curved upward", "upturned tail", "tail curling over the spine", "raised curved tail"],
    "pushed-in nose": ["flat nose", "short snout", "brachycephalic face", "squashed nose"],
    "tricolor coat": ["three-tone coat", "tri-colored fur pattern", "patchy coat", "multi-colored coat"],
}

NOISE_PATTERNS = [
    "There might also be some {wrong_breed} traits visible.",
    "The ears slightly resemble those of a {wrong_breed}.",
    "However, the coat texture is similar to a {wrong_breed}.",
    "Some features are also seen in {wrong_breed}s.",
    "A {wrong_breed} owner might mistake it at first glance.",
    "The overall shape is somewhat reminiscent of a {wrong_breed}.",
    "Without a DNA test, a {wrong_breed} cross cannot be ruled out.",
]

DEFAULT_INPUT = "training_data.json"
DEFAULT_OUTPUT = "data_synthesis/synthetic_dataset.json"
DEFAULT_REPORT = "data_synthesis/synthetic_report.txt"
