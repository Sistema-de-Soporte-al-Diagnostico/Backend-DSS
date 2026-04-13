from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    nombre = Column(String(80), nullable=False)
    password_hash = Column(String(255), nullable=False)
    rol = Column(String(20), nullable=False, default="vet")
    creado_en = Column(DateTime, default=datetime.utcnow, nullable=False)

    pacientes = relationship("Paciente", back_populates="usuario")
    predicciones = relationship("Prediccion", back_populates="usuario")

class Paciente(Base):
    __tablename__ = "pacientes"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    nombre = Column(String(50), nullable=False)
    especie = Column(String(50), nullable=False)  # ej. perro, gato
    raza = Column(String(50))
    edad = Column(Integer)
    propietario_id = Column(Integer, index=True, nullable=False)

    usuario = relationship("Usuario", back_populates="pacientes")
    # Relación uno-a-muchos con las predicciones
    predicciones = relationship("Prediccion", back_populates="paciente", cascade="all, delete-orphan")

class Prediccion(Base):
    __tablename__ = "predicciones"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    paciente_id = Column(Integer, ForeignKey("pacientes.id"), nullable=False, index=True)
    fecha = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # JSONB para almacenar los síntomas variables de forma estructurada e indexable (PostgreSQL)
    variables_clinicas = Column(JSONB, nullable=False) 
    
    resultado_enfermedad = Column(String(100), nullable=False)
    probabilidad_IA = Column(Float, nullable=False)

    usuario = relationship("Usuario", back_populates="predicciones")
    # Relación inversa con paciente
    paciente = relationship("Paciente", back_populates="predicciones")
