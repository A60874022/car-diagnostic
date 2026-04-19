from pydantic import BaseModel
from typing import Optional

class ManualVehicleData(BaseModel):
    plate_number: Optional[str] = None
    make: str
    model: str
    year: int
    description: Optional[str] = None

class OBDCodeRequest(BaseModel):
    code: str

class SessionResponse(BaseModel):
    session_id: str

class StatusResponse(BaseModel):
    session_id: str
    video_processed: bool
    audio_processed: bool
    has_obd: bool
    has_vehicle: bool

class DiagnosticReportResponse(BaseModel):
    report: str