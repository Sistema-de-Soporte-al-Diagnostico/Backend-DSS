import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Cargar las variables de entorno desde un archivo .env si existe
load_dotenv()

# URL de conexión a PostgreSQL
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://usuario:password@localhost:5432/vet_db"
)

# Configuración del engine de SQLAlchemy
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Sesión local para interactuar con la DB
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Clase base que nuestros modelos ORM van a heredar
Base = declarative_base()

# Función de dependencia para obtener la DB en nuestros endpoints de FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
