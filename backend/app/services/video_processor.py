# backend/app/services/video_processor.py
import random

def analyze_video(video_path: str) -> dict:
    # В реальности: извлечение кадров, прогон через YOLO, классификация.
    return {
        "smoke_detected": random.choice([True, False]),
        "smoke_confidence": round(random.uniform(0.5, 0.99), 2),
        "leak_detected": random.choice([True, False]),
        "leak_confidence": round(random.uniform(0.5, 0.99), 2),
        "damage_detected": random.choice([True, False]),
        "damage_areas": ["front_bumper", "rear_door"] if random.random() > 0.5 else []
    }