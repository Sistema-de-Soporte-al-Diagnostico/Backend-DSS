from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user
from app.db import models
from app.db.database import get_db
from app.schemas import (
    CompatPrediccionHistorialItem,
    HistorialItem,
    HistorialResponse,
    PrediccionCreate,
    PrediccionDetalleResponse,
)
from app.services.ai_service import predecir_enfermedad

router = APIRouter(tags=["IA"])


@router.post("/predecir/")
def realizar_prediccion(
    prediccion: PrediccionCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    paciente = (
        db.query(models.Paciente)
        .filter(
            models.Paciente.id == prediccion.paciente_id,
            models.Paciente.usuario_id == current_user.id,
        )
        .first()
    )
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado en la BD")

    try:
        enfermedad, probabilidad = predecir_enfermedad(prediccion.variables_clinicas)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error al predecir: {str(exc)}") from exc

    nueva_prediccion = models.Prediccion(
        usuario_id=current_user.id,
        paciente_id=prediccion.paciente_id,
        variables_clinicas=prediccion.variables_clinicas,
        resultado_enfermedad=enfermedad,
        probabilidad_IA=probabilidad,
    )
    db.add(nueva_prediccion)
    db.commit()
    db.refresh(nueva_prediccion)

    return {
        "mensaje": "Predicción procesada y guardada",
        "prediccion_id": nueva_prediccion.id,
        "diagnostico": enfermedad,
        "probabilidad_porcentaje": round(probabilidad * 100, 2),
    }


@router.get("/predicciones/historial", response_model=HistorialResponse)
def obtener_historial(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    desde: datetime | None = Query(default=None),
    hasta: datetime | None = Query(default=None),
    diagnostico: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    query = (
        db.query(models.Prediccion)
        .options(joinedload(models.Prediccion.paciente))
        .filter(models.Prediccion.usuario_id == current_user.id)
    )

    if desde:
        query = query.filter(models.Prediccion.fecha >= desde)
    if hasta:
        query = query.filter(models.Prediccion.fecha <= hasta)
    if diagnostico:
        query = query.filter(models.Prediccion.resultado_enfermedad.ilike(f"%{diagnostico}%"))

    total = query.count()
    rows = (
        query.order_by(models.Prediccion.fecha.desc())
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )

    items = [
        HistorialItem(
            id=row.id,
            paciente_id=row.paciente_id,
            fecha=row.fecha,
            resultado_enfermedad=row.resultado_enfermedad,
            probabilidad_IA=row.probabilidad_IA,
            paciente_nombre=row.paciente.nombre,
        )
        for row in rows
    ]
    return HistorialResponse(total=total, page=page, size=size, items=items)


@router.get("/predicciones/{prediccion_id}", response_model=PrediccionDetalleResponse)
def obtener_detalle_prediccion(
    prediccion_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    pred = (
        db.query(models.Prediccion)
        .options(joinedload(models.Prediccion.paciente))
        .filter(
            models.Prediccion.id == prediccion_id,
            models.Prediccion.usuario_id == current_user.id,
        )
        .first()
    )
    if not pred:
        raise HTTPException(status_code=404, detail="Predicción no encontrada")

    return PrediccionDetalleResponse(
        id=pred.id,
        paciente_id=pred.paciente_id,
        fecha=pred.fecha,
        resultado_enfermedad=pred.resultado_enfermedad,
        probabilidad_IA=pred.probabilidad_IA,
        variables_clinicas=pred.variables_clinicas,
        paciente={
            "id": pred.paciente.id,
            "nombre": pred.paciente.nombre,
            "especie": pred.paciente.especie,
            "raza": pred.paciente.raza,
            "edad": pred.paciente.edad,
            "propietario_id": pred.paciente.propietario_id,
        },
    )


@router.get("/history", response_model=list[CompatPrediccionHistorialItem], tags=["Compat"])
def obtener_historial_compat(
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    rows = (
        db.query(models.Prediccion)
        .options(joinedload(models.Prediccion.paciente))
        .filter(models.Prediccion.usuario_id == current_user.id)
        .order_by(models.Prediccion.fecha.desc())
        .all()
    )

    return [
        CompatPrediccionHistorialItem(
            id=str(row.id),
            patient={
                "id": row.paciente.id,
                "name": row.paciente.nombre,
                "species": row.paciente.especie,
                "speciesLabel": row.paciente.especie,
                "breed": row.paciente.raza,
                "age": row.paciente.edad,
                "ownerId": row.paciente.propietario_id,
            },
            variablesClinicas=row.variables_clinicas,
            result={
                "predictionId": row.id,
                "prediction": row.resultado_enfermedad,
                "probability": row.probabilidad_IA,
                "riskLevel": "alto" if row.probabilidad_IA >= 0.75 else "medio" if row.probabilidad_IA >= 0.45 else "bajo",
            },
            createdAt=row.fecha,
        )
        for row in rows
    ]


@router.get("/predictions/{prediccion_id}", response_model=CompatPrediccionHistorialItem, tags=["Compat"])
def obtener_detalle_compat(
    prediccion_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    row = (
        db.query(models.Prediccion)
        .options(joinedload(models.Prediccion.paciente))
        .filter(
            models.Prediccion.id == prediccion_id,
            models.Prediccion.usuario_id == current_user.id,
        )
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Predicción no encontrada")

    return CompatPrediccionHistorialItem(
        id=str(row.id),
        patient={
            "id": row.paciente.id,
            "name": row.paciente.nombre,
            "species": row.paciente.especie,
            "speciesLabel": row.paciente.especie,
            "breed": row.paciente.raza,
            "age": row.paciente.edad,
            "ownerId": row.paciente.propietario_id,
        },
        variablesClinicas=row.variables_clinicas,
        result={
            "predictionId": row.id,
            "prediction": row.resultado_enfermedad,
            "probability": row.probabilidad_IA,
            "riskLevel": "alto" if row.probabilidad_IA >= 0.75 else "medio" if row.probabilidad_IA >= 0.45 else "bajo",
        },
        createdAt=row.fecha,
    )
