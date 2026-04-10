from pydantic import BaseModel
from typing import List
import random

class PetInput(BaseModel):
    description: str

class PetOutput(BaseModel):
    animal: str
    breed: str
    confidence: float

class HashtagInput(BaseModel):
    animal: str
    breed: str
    platform: str

class HashtagOutput(BaseModel):
    hashtags: List[str]
    count: int

class StatsInput(BaseModel):
    user_id: str

class StatsOutput(BaseModel):
    total_requests: int
    favorite_breed: str

def identify_pet(data: PetInput) -> PetOutput:
    if "cat" in data.description.lower():
        return PetOutput(animal="cat", breed="maine coon", confidence=0.95)
    return PetOutput(animal="dog", breed="labrador", confidence=0.90)

def generate_hashtags(data: HashtagInput) -> HashtagOutput:
    hashtags = [f"#{data.breed.replace(' ', '')}", f"#{data.animal}", f"#{data.platform}"]
    if data.platform == "instagram":
        hashtags.append("#petlovers")
    else:
        hashtags.append("#fyp")
    return HashtagOutput(hashtags=hashtags, count=len(hashtags))

def get_user_stats(data: StatsInput) -> StatsOutput:
    return StatsOutput(total_requests=random.randint(10, 100), favorite_breed="persian cat")