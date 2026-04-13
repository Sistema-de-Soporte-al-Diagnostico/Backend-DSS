from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel, EmailStr, Field


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: Dict[str, str]


class UserRegister(BaseModel):
    email: EmailStr
    nombre: str = Field(min_length=2, max_length=80)
    password: str = Field(min_length=6, max_length=128)
    rol: str = Field(default="vet")


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)

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


class HistorialItem(BaseModel):
    id: int
    paciente_id: int
    fecha: datetime
    resultado_enfermedad: str
    probabilidad_IA: float
    paciente_nombre: str


class HistorialResponse(BaseModel):
    total: int
    page: int
    size: int
    items: list[HistorialItem]


class PrediccionDetalleResponse(BaseModel):
    id: int
    paciente_id: int
    fecha: datetime
    resultado_enfermedad: str
    probabilidad_IA: float
    variables_clinicas: Dict[str, float]
    paciente: Dict[str, Optional[str | int]]


class CompatPrediccionHistorialItem(BaseModel):
    id: str
    patient: Dict[str, Optional[str | int]]
    variablesClinicas: Dict[str, float]
    result: Dict[str, float | str]
    createdAt: datetime
