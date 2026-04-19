# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api.endpoints import vehicle, upload, obd, diagnostic
from app.models.database import Base, engine
import os

Base.metadata.create_all(bind=engine)

app = FastAPI(title="CarDiag AI", version="0.3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(vehicle.router, prefix="/api/vehicle", tags=["vehicle"])
app.include_router(upload.router, prefix="/api/upload", tags=["upload"])
app.include_router(obd.router, prefix="/api/obd", tags=["obd"])
app.include_router(diagnostic.router, prefix="/api/diagnostic", tags=["diagnostic"])

static_dir = "/static" if os.path.exists("/static") else "../static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def read_index():
    index_path = os.path.join(static_dir, "index.html")
    return FileResponse(index_path)