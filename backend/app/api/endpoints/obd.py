# backend/app/api/endpoints/obd.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.diagnostic import DiagnosticSession
from app.schemas.requests_responses import OBDCodeRequest
from app.services.obd_decoder import decode_obd

router = APIRouter()

@router.post("/{session_id}")
def add_obd_code(session_id: str, data: OBDCodeRequest, db: Session = Depends(get_db)):
    session = db.query(DiagnosticSession).filter(DiagnosticSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    description = decode_obd(data.code)
    session.obd_code = data.code
    session.obd_description = description
    db.commit()
    return {"code": data.code, "description": description}