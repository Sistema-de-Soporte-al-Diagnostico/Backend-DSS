from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Paciente(Base):
    __tablename__ = "pacientes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False)
    especie = Column(String(50), nullable=False)  # ej. perro, gato
    raza = Column(String(50))
    edad = Column(Integer)
    propietario_id = Column(Integer, index=True, nullable=False)

    # Relación uno-a-muchos con las predicciones
    predicciones = relationship("Prediccion", back_populates="paciente", cascade="all, delete-orphan")

class Prediccion(Base):
    __tablename__ = "predicciones"

    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("pacientes.id"), nullable=False, index=True)
    fecha = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # JSONB para almacenar los síntomas variables de forma estructurada e indexable (PostgreSQL)
    variables_clinicas = Column(JSONB, nullable=False) 
    
    resultado_enfermedad = Column(String(100), nullable=False)
    probabilidad_IA = Column(Float, nullable=False)

    # Relación inversa con paciente
    paciente = relationship("Paciente", back_populates="predicciones")
