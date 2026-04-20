# backend/app/services/llm_integrator.py
import os
import pathlib
import base64
from openai import OpenAI
from app.core.config import settings

# Получаем ключ из настроек (он должен быть загружен из переменных окружения)
api_key = settings.GEMINI_API_KEY
if not api_key:
    raise ValueError("GEMINI_API_KEY is not set in environment")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.vsegpt.ru/v1"
)

def generate_diagnostic_report(context: dict) -> str:
    vehicle = context.get("vehicle", {})
    user_desc = context.get("user_description", "")
    obd = context.get("obd")
    video = context.get("video_analysis")
    audio_path = context.get("audio_path")

    prompt_parts = [
        "Ты — опытный автомеханик-диагност. Проанализируй предоставленную аудиозапись работы автомобиля и дополнительные данные.",
        f"Автомобиль: {vehicle.get('make', '')} {vehicle.get('model', '')} {vehicle.get('year', '')}",
    ]

    if user_desc:
        prompt_parts.append(f"Описание неисправности от владельца: {user_desc}")

    if obd and obd.get("code"):
        prompt_parts.append(f"Код ошибки OBD-II: {obd['code']} – {obd.get('description', '')}")

    if video:
        smoke = "обнаружен" if video.get("smoke_detected") else "не обнаружен"
        leak = "обнаружена" if video.get("leak_detected") else "не обнаружена"
        prompt_parts.append(f"Результат видеоанализа: дым – {smoke}, течь – {leak}.")

    prompt_parts.append(
        "На основе этих данных и, главное, аудиозаписи, определи наиболее вероятную неисправность. "
        "Опиши, какие характерные звуки слышны на записи (стук, свист, скрежет и т.д.) и на что они указывают. "
        "Дай рекомендации по дальнейшей диагностике и ремонту. "
        "Ответ должен быть подробным, но понятным автовладельцу, на русском языке."
    )
    full_text_prompt = "\n".join(prompt_parts)

    messages = [{"role": "user", "content": full_text_prompt}]

    try:
        if audio_path and os.path.exists(audio_path):
            filepath = pathlib.Path(audio_path)
            with open(filepath, "rb") as f:
                audio_base64 = base64.b64encode(f.read()).decode("utf-8")
            audio_content = {
                "type": "audio",
                "audio": {
                    "data": audio_base64,
                    "format": filepath.suffix.lower().replace(".", "")
                }
            }
            messages.append({"role": "user", "content": [audio_content]})
    except Exception as e:
        print(f"Ошибка при загрузке аудио: {e}")

    try:
        model_id = "google/gemini-2.5-flash-lite"
        response = client.chat.completions.create(
            model=model_id,
            messages=messages,
            temperature=0.3,
            max_tokens=2000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Не удалось сгенерировать отчёт с помощью VseGPT: {str(e)}"