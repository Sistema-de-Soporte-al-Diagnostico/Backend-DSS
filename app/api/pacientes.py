from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db import models
from app.db.database import get_db
from app.schemas import PacienteCreate

router = APIRouter(tags=["Pacientes"])


@router.post("/pacientes/")
def crear_paciente(
    paciente: PacienteCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    nuevo_paciente = models.Paciente(
        usuario_id=current_user.id,
        nombre=paciente.nombre,
        especie=paciente.especie,
        raza=paciente.raza,
        edad=paciente.edad,
        propietario_id=paciente.propietario_id,
    )
    db.add(nuevo_paciente)
    db.commit()
    db.refresh(nuevo_paciente)
    return {"mensaje": "Paciente registrado exitosamente", "paciente_id": nuevo_paciente.id}
