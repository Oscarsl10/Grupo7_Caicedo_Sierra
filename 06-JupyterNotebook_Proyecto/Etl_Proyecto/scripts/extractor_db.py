import requests
import pandas as pd
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

# Importar conexión a la BD
from scripts.database import engine

# Cargar variables de entorno
load_dotenv()

API_KEY = os.getenv("RAWG_API_KEY")
BASE_URL = os.getenv("BASE_URL")

# Directorios
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS_DIR = os.path.join(BASE_DIR, "logs")

os.makedirs(LOGS_DIR, exist_ok=True)

# Configuración de logs
logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.FileHandler(os.path.join(LOGS_DIR, "etl.log")),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

try:

    logger.info("Extrayendo datos de la API RAWG...")

    url = f"{BASE_URL}/games"

    params = {
        "key": API_KEY,
        "page_size": 40
    }

    response = requests.get(url, params=params)
    response.raise_for_status()

    data = response.json()

    results = data["results"]

    videojuegos = []

    for game in results:
        videojuegos.append({
            "nombre": game["name"],
            "fecha_lanzamiento": game["released"],
            "rating": game["rating"],
            "metacritic": game.get("metacritic")
        })

    # Crear DataFrame
    df = pd.DataFrame(videojuegos)

    logger.info(f"Se extrajeron {len(df)} videojuegos")

    # Agregar fecha de creación
    df["fecha_creacion"] = datetime.utcnow()

    logger.info("Guardando datos en PostgreSQL...")

    # Insertar en PostgreSQL
    df.to_sql(
        "videojuegos",
        engine,
        if_exists="append",
        index=False
    )

    logger.info("Datos guardados correctamente en PostgreSQL")

except Exception as e:
    logger.error(f"Error en extractor: {e}")