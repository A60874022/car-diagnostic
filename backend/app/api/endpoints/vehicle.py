from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.diagnostic import DiagnosticSession
from app.schemas.requests_responses import ManualVehicleData, SessionResponse

router = APIRouter()

@router.post("/manual", response_model=SessionResponse)
def manual_input(data: ManualVehicleData, db: Session = Depends(get_db)):
    session = DiagnosticSession(
        plate_number=data.plate_number,
        car_make=data.make,
        car_model=data.model,
        car_year=data.year,
        user_description=data.description,
        manual_input=True
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return SessionResponse(session_id=session.id)