import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
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
    input_path = os.path.join(DATA_DIR, "videojuegos_transformed.csv")
    df = pd.read_csv(input_path)

    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    df["metacritic"] = pd.to_numeric(df["metacritic"], errors="coerce")
    df["rating_scaled"] = df["rating"] * 20

    fig, axes = plt.subplots(2, 2, figsize=(20, 12))
    fig.suptitle('Análisis de Videojuegos (Top 20)', fontsize=18, fontweight='bold')

    axes[0, 0].bar(df["nombre"], df["rating"])
    axes[0, 0].set_title("Rating (0-5)")
    axes[0, 0].tick_params(axis="x", rotation=90)

    axes[0, 1].bar(df["nombre"], df["metacritic"])
    axes[0, 1].set_title("Metacritic (0-100)")
    axes[0, 1].tick_params(axis="x", rotation=90)

    axes[1, 0].scatter(df["nombre"], pd.to_datetime(df["fecha_lanzamiento"]))
    axes[1, 0].set_title("Fecha de lanzamiento")
    axes[1, 0].tick_params(axis="x", rotation=90)

    x = np.arange(len(df))
    width = 0.35
    axes[1, 1].bar(x - width/2, df["rating_scaled"], width, label="Rating (0-100)")
    axes[1, 1].bar(x + width/2, df["metacritic"], width, label="Metacritic")
    axes[1, 1].set_xticks(x)
    axes[1, 1].set_xticklabels(df["nombre"], rotation=90)
    axes[1, 1].legend()

    plt.tight_layout()
    output_graph = os.path.join(DATA_DIR, "videojuegos_analysis_top20_scaled.png")
    plt.savefig(output_graph, dpi=400, bbox_inches="tight")
    plt.show()

    logger.info(f"Gráficas guardadas en: {output_graph}")

except Exception as e:
    logger.error(f"Error en visualizador: {e}")