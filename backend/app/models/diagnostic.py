from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, Boolean
from sqlalchemy.sql import func
from app.models.database import Base
import uuid

class DiagnosticSession(Base):
    __tablename__ = "diagnostic_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    plate_number = Column(String(20), nullable=True)
    car_make = Column(String(50), nullable=True)
    car_model = Column(String(50), nullable=True)
    car_year = Column(Integer, nullable=True)
    manual_input = Column(Boolean, default=False)

    user_description = Column(Text, nullable=True)   # ← обязательно

    obd_code = Column(String(10), nullable=True)
    obd_description = Column(Text, nullable=True)

    video_analysis_result = Column(JSON, nullable=True)
    audio_analysis_result = Column(JSON, nullable=True)
    final_report = Column(Text, nullable=True)

    video_processed = Column(Boolean, default=False)
    audio_processed = Column(Boolean, default=False)

    video_path = Column(String(255), nullable=True)
    audio_path = Column(String(255), nullable=True)