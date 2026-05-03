import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import logging

from sqlalchemy import select
from scripts.database import engine
from scripts.models import VideojuegoTop

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

    logger.info("Leyendo datos desde la base de datos (tabla videojuegos_top)...")

    query = select(
        VideojuegoTop.nombre,
        VideojuegoTop.fecha_lanzamiento,
        VideojuegoTop.rating,
        VideojuegoTop.metacritic,
        VideojuegoTop.ratings_count,
        VideojuegoTop.added,
        VideojuegoTop.playtime
    )

    df = pd.read_sql(query, engine)

    if df.empty:
        raise ValueError("La tabla videojuegos_top no contiene datos")

    logger.info(f"Se cargaron {len(df)} registros")

    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    df["metacritic"] = pd.to_numeric(df["metacritic"], errors="coerce")
    df["ratings_count"] = pd.to_numeric(df["ratings_count"], errors="coerce")
    df["added"] = pd.to_numeric(df["added"], errors="coerce")
    df["playtime"] = pd.to_numeric(df["playtime"], errors="coerce")
    df["rating_scaled"] = df["rating"] * 20

    fig, axes = plt.subplots(3, 2, figsize=(20, 15))
    fig.suptitle('Análisis de Videojuegos (Top 20)', fontsize=18, fontweight='bold')

    # Rating
    axes[0, 0].bar(df["nombre"], df["rating"])
    axes[0, 0].set_title("Rating (0-5)")
    axes[0, 0].tick_params(axis="x", rotation=90)

    # Metacritic
    axes[0, 1].bar(df["nombre"], df["metacritic"])
    axes[0, 1].set_title("Metacritic (0-100)")
    axes[0, 1].tick_params(axis="x", rotation=90)

    # Ratings Count
    axes[1, 0].bar(df["nombre"], df["ratings_count"])
    axes[1, 0].set_title("Ratings Count")
    axes[1, 0].tick_params(axis="x", rotation=90)

    # Added
    axes[1, 1].bar(df["nombre"], df["added"])
    axes[1, 1].set_title("Added Count")
    axes[1, 1].tick_params(axis="x", rotation=90)

    # Playtime
    axes[2, 0].bar(df["nombre"], df["playtime"])
    axes[2, 0].set_title("Playtime (hours)")
    axes[2, 0].tick_params(axis="x", rotation=90)

    # Fecha lanzamiento
    axes[2, 1].scatter(df["nombre"], pd.to_datetime(df["fecha_lanzamiento"]))
    axes[2, 1].set_title("Fecha de lanzamiento")
    axes[2, 1].tick_params(axis="x", rotation=90)

    plt.tight_layout()

    output_graph = os.path.join(DATA_DIR, "videojuegos_analysis_top20_scaled.png")

    plt.savefig(output_graph, dpi=400, bbox_inches="tight")
    plt.show()

    logger.info(f"Gráficas guardadas en: {output_graph}")

except Exception as e:
    logger.error(f"Error en visualizador: {e}")