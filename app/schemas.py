from pydantic import BaseModel
from typing import Dict

class PacienteCreate(BaseModel):
    nombre: str
    especie: str
    raza: str
    edad: int
    propietario_id: int

class PrediccionCreate(BaseModel):
    paciente_id: int
    # En nuestro modelo Dummy pedimos 6 variables exactas (ej: especie, edad, temperatura, fc, vomito, diarrea)
    variables_clinicas: Dict[str, float] 
