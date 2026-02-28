import pandas as pd
import os
import logging
from sqlalchemy import create_engine
from dotenv import load_dotenv

# ==========================
# CARGAR VARIABLES DE ENTORNO
# ==========================

load_dotenv()

DB_USER = "postgres"
DB_PASSWORD = "1234"
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "tienda"

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

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
        # Leer CSV limpio
        input_path = os.path.join(DATA_DIR, "videojuegos_clean.csv")
        df = pd.read_csv(input_path)

        # Crear conexión
        engine = create_engine(DATABASE_URL)

        # Cargar datos a PostgreSQL
        df.to_sql(
            name="videojuegos",
            con=engine,
            if_exists="replace",  # cambia a "append" si no quieres borrar
            index=False
        )

        logger.info("Datos cargados correctamente en PostgreSQL 🚀")

    except Exception as e:
        logger.error(f"Error en loader: {e}")

if __name__ == "__main__":
    main()