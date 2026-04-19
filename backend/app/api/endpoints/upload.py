# backend/app/api/endpoints/upload.py
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.diagnostic import DiagnosticSession
from app.tasks.background_tasks import process_video_task, process_audio_task
from app.core.config import settings
import os
import uuid

router = APIRouter()

@router.post("/video/{session_id}")
async def upload_video(
    session_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    session = db.query(DiagnosticSession).filter(DiagnosticSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    ext = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, filename)
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    session.video_path = file_path
    db.commit()

    process_video_task.delay(session_id, file_path)
    return {"message": "Video uploaded, processing started"}

@router.post("/audio/{session_id}")
async def upload_audio(
    session_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    session = db.query(DiagnosticSession).filter(DiagnosticSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Получаем расширение файла и создаём уникальное имя
    ext = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, filename)
    
    # Убеждаемся, что папка существует
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    # Сохраняем файл на диск
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    # Сохраняем путь к файлу в базе данных
    session.audio_path = file_path
    db.commit()

    # Запускаем фоновую обработку аудио (пока заглушка)
    process_audio_task.delay(session_id, file_path)
    
    return {"message": "Audio uploaded, processing started"}