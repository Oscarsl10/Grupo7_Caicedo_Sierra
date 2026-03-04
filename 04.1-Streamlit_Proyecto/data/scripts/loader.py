import pandas as pd
import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

# ==========================
# CARGAR VARIABLES DE ENTORNO
# ==========================

load_dotenv()


def _normalize_database_url(raw_url: str) -> str:
    if raw_url is None:
        return None
    url = raw_url
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)

    # Añadir sslmode=require para conexiones remotas si no está presente
    if "localhost" not in url and "127.0.0.1" not in url and "sslmode" not in url:
        if "?" in url:
            url = url + "&sslmode=require"
        else:
            url = url + "?sslmode=require"
    return url


def _get_database_url():
    # Priorizar variable de entorno DATABASE_URL
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        return _normalize_database_url(db_url)

    # Fallback: construir desde variables individuales (útil en local)
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "1234")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "tienda")
    return _normalize_database_url(f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# ==========================
# RUTAS
# ==========================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

os.makedirs(LOGS_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.FileHandler(os.path.join(LOGS_DIR, "etl.log")),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    try:
        # Debug: mostrar qué DATABASE_URL se está usando
        db_url = _get_database_url()
        logger.info(f"📌 DATABASE_URL resuelto a: {db_url[:50]}..." if db_url else "❌ DATABASE_URL no configurado")
        
        # Leer CSV limpio
        input_path = os.path.join(DATA_DIR, "videojuegos_clean.csv")
        df = pd.read_csv(input_path)
        logger.info(f"📄 CSV cargado: {len(df)} filas")

        # Crear conexión
        if not db_url:
            logger.error("DATABASE_URL no está configurada")
            return

        engine = create_engine(db_url)

        # Cargar datos a PostgreSQL
        df.to_sql(
            name="videojuegos",
            con=engine,
            if_exists="replace",  # cambia a "append" si no quieres borrar
            index=False
        )

        logger.info("Datos cargados correctamente en PostgreSQL 🚀")

    except SQLAlchemyError as e:
        logger.error(f"Error en loader (SQLAlchemy): {e}")
    except Exception as e:
        logger.error(f"Error en loader: {e}")

if __name__ == "__main__":
    main()