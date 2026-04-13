import requests
import pandas as pd
import os
import logging
import json
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

    videojuegos = []
    page = 1
    max_pages = 3  # Extraer hasta 3 páginas (120 juegos ≈ 100)

    while page <= max_pages:
        url = f"{BASE_URL}/games"
        params = {
            "key": API_KEY,
            "page": page,
            "page_size": 40
        }

        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        results = data["results"]

        if not results:
            break  # No más páginas

        for game in results:
            game_id = game["id"]
            
            # Obtener detalles adicionales del juego (developers, publishers)
            detail_url = f"{BASE_URL}/games/{game_id}"
            detail_params = {"key": API_KEY}
            
            try:
                detail_response = requests.get(detail_url, params=detail_params)
                detail_response.raise_for_status()
                game_detail = detail_response.json()
            except Exception as e:
                logger.warning(f"Error obteniendo detalles para juego {game_id}: {e}")
                game_detail = {}
            
            videojuegos.append({
                "nombre": game["name"],
                "fecha_lanzamiento": game["released"],
                "rating": game["rating"],
                "metacritic": game.get("metacritic"),
                "ratings_count": game.get("ratings_count"),
                "added": game.get("added"),
                "playtime": game.get("playtime"),
                "rating_top": game.get("rating_top"),
                "platforms": json.dumps([p["platform"]["name"] for p in game.get("platforms", [])]),
                "genres": json.dumps([g["name"] for g in game.get("genres", [])]),
                "esrb_rating": game.get("esrb_rating", {}).get("name") if game.get("esrb_rating") else None,
                "developers": json.dumps([d["name"] for d in game_detail.get("developers", [])]),
                "publishers": json.dumps([p["name"] for p in game_detail.get("publishers", [])])
            })

        logger.info(f"Página {page} procesada: {len(results)} juegos")
        page += 1

    # Crear DataFrame
    df = pd.DataFrame(videojuegos)

    logger.info(f"Se extrajeron {len(df)} videojuegos en total")

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