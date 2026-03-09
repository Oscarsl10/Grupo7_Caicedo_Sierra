#!/usr/bin/env python3

import pandas as pd
import logging
from sqlalchemy import text
from scripts.database import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def total_videojuegos():
    """Cantidad total de videojuegos"""
    query = text("""
        SELECT COUNT(*) AS total
        FROM videojuegos
    """)

    df = pd.read_sql(query, engine)
    print("\nTotal de videojuegos:")
    print(df)


def promedio_rating():
    """Promedio de rating"""
    query = text("""
        SELECT AVG(rating) AS promedio_rating
        FROM videojuegos
    """)

    df = pd.read_sql(query, engine)
    print("\nPromedio de rating:")
    print(df)


def top_rating():
    """Top 10 videojuegos mejor valorados"""
    query = text("""
        SELECT nombre, rating
        FROM videojuegos
        ORDER BY rating DESC
        LIMIT 10
    """)

    df = pd.read_sql(query, engine)
    print("\nTop 10 videojuegos por rating:")
    print(df)


def top_metacritic():
    """Top 10 videojuegos por Metacritic"""
    query = text("""
        SELECT nombre, metacritic
        FROM videojuegos
        WHERE metacritic IS NOT NULL
        ORDER BY metacritic DESC
        LIMIT 10
    """)

    df = pd.read_sql(query, engine)
    print("\nTop 10 videojuegos por Metacritic:")
    print(df)


def juegos_por_anio():
    """Cantidad de juegos por año"""
    query = text("""
        SELECT
            EXTRACT(YEAR FROM fecha_lanzamiento) AS anio,
            COUNT(*) AS total
        FROM videojuegos
        GROUP BY anio
        ORDER BY anio
    """)

    df = pd.read_sql(query, engine)
    print("\nVideojuegos por año:")
    print(df)


if __name__ == "__main__":

    logger.info("Ejecutando consultas de análisis...")

    total_videojuegos()
    promedio_rating()
    top_rating()
    top_metacritic()
    juegos_por_anio()

    logger.info("Consultas completadas")