# backend/app/api/endpoints/upload.py
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.diagnostic import DiagnosticSession
from app.services.video_processor import analyze_video
from app.services.audio_analyzer import analyze_audio
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

    # Синхронный анализ вместо Celery
    try:
        result = analyze_video(file_path)
        session.video_analysis_result = result
        session.video_processed = True
        db.commit()
    except Exception as e:
        print(f"Video analysis error: {e}")

    return {"message": "Video uploaded and processed"}

@router.post("/audio/{session_id}")
async def upload_audio(
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

    session.audio_path = file_path
    db.commit()

    # Синхронный анализ вместо Celery
    try:
        result = analyze_audio(file_path)
        session.audio_analysis_result = result
        session.audio_processed = True
        db.commit()
    except Exception as e:
        print(f"Audio analysis error: {e}")

    return {"message": "Audio uploaded and processed"}