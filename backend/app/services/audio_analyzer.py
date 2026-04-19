# backend/app/services/audio_analyzer.py
import librosa
import numpy as np
import random
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def analyze_audio(audio_path: str) -> dict:
    """
    Анализирует аудиофайл, возвращает словарь вероятностей для различных классов звуков.
    В реальном проекте здесь должна быть модель классификации.
    """
    try:
        # Загружаем аудио (первые 30 секунд для ускорения)
        y, sr = librosa.load(audio_path, sr=None, duration=30.0)
        if len(y) == 0:
            raise ValueError("Аудиофайл пуст или поврежден")

        # Вычисляем признаки (пример: mfcc)
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        avg_mfcc = np.mean(mfccs, axis=1)

        # Здесь может быть вызов модели, сейчас заглушка
        issues = ["knocking", "whistling", "grinding", "normal"]
        probs = {issue: round(random.random(), 2) for issue in issues}
        total = sum(probs.values())
        for k in probs:
            probs[k] = round(probs[k] / total, 2)

        logger.info(f"Audio analysis completed for {audio_path}")
        return probs

    except Exception as e:
        logger.error(f"Audio analysis failed for {audio_path}: {str(e)}")
        # Возвращаем пустой результат, но задача не упадет
        return {"error": str(e), "knocking": 0.0, "whistling": 0.0, "grinding": 0.0, "normal": 1.0}