import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# obtener ruta del proyecto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ruta completa de la base de datos
DB_PATH = os.path.join(BASE_DIR, "weather_etl.db")

DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()