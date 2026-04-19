# backend/app/api/endpoints/diagnostic.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.diagnostic import DiagnosticSession
from app.services.llm_integrator import generate_diagnostic_report
from app.schemas.requests_responses import DiagnosticReportResponse

router = APIRouter()

@router.post("/generate/{session_id}", response_model=DiagnosticReportResponse)
def generate_report(session_id: str, db: Session = Depends(get_db)):
    session = db.query(DiagnosticSession).filter(DiagnosticSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    context = {
        "vehicle": {
            "make": session.car_make,
            "model": session.car_model,
            "year": session.car_year,
        },
        "user_description": session.user_description,
        "obd": {
            "code": session.obd_code,
            "description": session.obd_description
        } if session.obd_code else None,
        "video_analysis": session.video_analysis_result,
        "audio_path": session.audio_path,  # ← Вот здесь мы передаём путь к аудио
    }

    report = generate_diagnostic_report(context)
    session.final_report = report
    db.commit()

    return DiagnosticReportResponse(report=report)