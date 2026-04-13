from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict

from app.api.auth import router as auth_router
from app.api.pacientes import router as pacientes_router
from app.api.predicciones import router as predicciones_router
from app.db.database import engine
from app.db import models

# Crea las tablas en PostgreSQL si aún no existen
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API de Soporte al Diagnóstico Veterinario",
    description="Backend para el Sistema SIS-IA-VET",
    version="1.0.0"
)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", response_model=Dict[str, str], tags=["Estado"])
async def health_check() -> Dict[str, str]:
    return {"status": "activo", "message": "El servidor está en funcionamiento"}

app.include_router(auth_router)
app.include_router(pacientes_router)
app.include_router(predicciones_router)
