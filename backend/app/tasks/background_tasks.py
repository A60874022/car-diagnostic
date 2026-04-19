# app/tasks/background_tasks.py
from celery import Celery
from app.core.config import settings
from app.services.video_processor import analyze_video
from app.services.audio_analyzer import analyze_audio
from app.models.diagnostic import DiagnosticSession
from app.models.database import SessionLocal

celery_app = Celery(
    "car_diagnostic",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

@celery_app.task
def process_video_task(session_id: str, video_path: str):
    result = analyze_video(video_path)
    db = SessionLocal()
    session = db.query(DiagnosticSession).filter(DiagnosticSession.id == session_id).first()
    if session:
        session.video_analysis_result = result
        session.video_processed = True
        db.commit()
    db.close()

@celery_app.task
def process_audio_task(session_id: str, audio_path: str):
    result = analyze_audio(audio_path)
    db = SessionLocal()
    session = db.query(DiagnosticSession).filter(DiagnosticSession.id == session_id).first()
    if session:
        session.audio_analysis_result = result
        session.audio_processed = True
        db.commit()
    db.close()