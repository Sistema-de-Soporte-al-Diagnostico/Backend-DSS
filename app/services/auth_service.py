from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.db import models
from app.schemas import UserLogin, UserRegister


def register_user(payload: UserRegister, db: Session):
    exists = db.query(models.Usuario).filter(models.Usuario.email == payload.email).first()
    if exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El correo ya está registrado",
        )

    user = models.Usuario(
        email=payload.email,
        nombre=payload.nombre,
        password_hash=hash_password(payload.password),
        rol=payload.rol,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return issue_token_for_user(user)


def login_user(payload: UserLogin, db: Session):
    user = db.query(models.Usuario).filter(models.Usuario.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
        )
    return issue_token_for_user(user)


def issue_token_for_user(user: models.Usuario):
    token = create_access_token(
        subject=str(user.id),
        extra_claims={"email": user.email, "role": user.rol},
    )
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "name": user.nombre,
            "email": user.email,
            "role": user.rol,
        },
    }
