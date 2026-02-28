import pandas as pd
import os
import logging

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
    input_path = os.path.join(DATA_DIR, "videojuegos_clean.csv")
    df = pd.read_csv(input_path)

    logger.info("CSV cargado para transformación")

    df["fecha_lanzamiento"] = pd.to_datetime(df["fecha_lanzamiento"], errors="coerce")
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    df["metacritic"] = pd.to_numeric(df["metacritic"], errors="coerce")

    df_top = df.nlargest(20, "rating")

    output_path = os.path.join(DATA_DIR, "videojuegos_transformed.csv")
    df_top.to_csv(output_path, index=False)

    logger.info(f"CSV transformado guardado en: {output_path}")

except Exception as e:
    logger.error(f"Error en transformador: {e}")