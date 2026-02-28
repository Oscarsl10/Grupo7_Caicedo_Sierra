import requests
import pandas as pd
import os
import logging
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

API_KEY = os.getenv("RAWG_API_KEY")
BASE_URL = os.getenv("BASE_URL")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.FileHandler(os.path.join(LOGS_DIR, "etl.log")),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

try:
    url = f"{BASE_URL}/games"
    params = {
        "key": API_KEY,
        "page_size": 40
    }

    response = requests.get(url, params=params)
    response.raise_for_status()

    data = response.json()

    # Guardar JSON crudo
    json_path = os.path.join(DATA_DIR, "videojuegos.json")
    with open(json_path, "w", encoding="utf-8") as f:
        import json
        json.dump(data, f, indent=4, ensure_ascii=False)

    logger.info("JSON crudo guardado correctamente")

    # Normalizar datos importantes
    results = data["results"]

    videojuegos = []
    for game in results:
        videojuegos.append({
            "nombre": game["name"],
            "fecha_lanzamiento": game["released"],
            "rating": game["rating"],
            "metacritic": game.get("metacritic")
        })

    df = pd.DataFrame(videojuegos)

    clean_path = os.path.join(DATA_DIR, "videojuegos_clean.csv")
    df.to_csv(clean_path, index=False)

    logger.info("CSV limpio generado correctamente")

except Exception as e:
    logger.error(f"Error en extractor: {e}")