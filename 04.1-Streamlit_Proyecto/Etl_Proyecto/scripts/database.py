import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Cargar .env
load_dotenv()

# Obtener DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL no está configurado en el .env")

# Crear engine
engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True  # evita errores cuando la conexión se duerme
)

# Sesiones
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base para modelos
Base = declarative_base()