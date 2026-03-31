from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Dict

from app.db.database import get_db, engine
from app.db import models
from app.schemas import PacienteCreate, PrediccionCreate
from app.services.ai_service import predecir_enfermedad

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

@app.post("/pacientes/", tags=["Pacientes"])
def crear_paciente(paciente: PacienteCreate, db: Session = Depends(get_db)):
    nuevo_paciente = models.Paciente(
        nombre=paciente.nombre,
        especie=paciente.especie,
        raza=paciente.raza,
        edad=paciente.edad,
        propietario_id=paciente.propietario_id
    )
    db.add(nuevo_paciente)
    db.commit()
    db.refresh(nuevo_paciente)
    return {"mensaje": "Paciente registrado exitosamente", "paciente_id": nuevo_paciente.id}

@app.post("/predecir/", tags=["IA"])
def realizar_prediccion(prediccion: PrediccionCreate, db: Session = Depends(get_db)):
    # 1. Validar si el paciente existe
    paciente = db.query(models.Paciente).filter(models.Paciente.id == prediccion.paciente_id).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado en la BD")
    
    # 2. Consultar al servicio de Inteligencia Artificial
    try:
        enfermedad, probabilidad = predecir_enfermedad(prediccion.variables_clinicas)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al predecir: {str(e)}")
        
    # 3. Guardar el registro de la interacción en PostgreSQL
    nueva_prediccion = models.Prediccion(
        paciente_id=prediccion.paciente_id,
        variables_clinicas=prediccion.variables_clinicas,
        resultado_enfermedad=enfermedad,
        probabilidad_IA=probabilidad
    )
    db.add(nueva_prediccion)
    db.commit()
    db.refresh(nueva_prediccion)
    
    return {
        "mensaje": "Predicción procesada y guardada",
        "prediccion_id": nueva_prediccion.id,
        "diagnostico": enfermedad,
        "probabilidad_porcentaje": round(probabilidad * 100, 2)
    }
