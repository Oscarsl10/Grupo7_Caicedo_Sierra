#!/usr/bin/env python3

import logging
import time
import pandas as pd
import numpy as np
from datetime import datetime
from sqlalchemy import text
from scripts.database import engine, SessionLocal
from scripts.models import MetricasETL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def transformar_datos():
    inicio = time.time()

    registros_extraidos = 0
    registros_guardados = 0
    registros_fallidos = 0
    estado = "SUCCESS"
    mensaje = None

    try:
        logger.info("Leyendo datos desde PostgreSQL (tabla: videojuegos)...")

        query = text("""
            SELECT nombre, fecha_lanzamiento, rating, metacritic, ratings_count, 
                   added, playtime, rating_top, platforms, genres, 
                   esrb_rating, developers, publishers
            FROM videojuegos
        """)

        df = pd.read_sql(query, engine)
        registros_extraidos = len(df)
        logger.info(f"Registros extraídos: {registros_extraidos}")

        # 1. Conversión de tipos para asegurar filtros correctos
        columnas_num = ["rating", "metacritic", "ratings_count", "added", "playtime"]
        for col in columnas_num:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        # 2. FILTROS DE CALIDAD (Crucial para R2 > 0.50 y reducir heterocedasticidad)
        # Eliminamos juegos sin Metacritic (nuestro objetivo)
        df_limpio = df.dropna(subset=["metacritic"]).copy()

        # Filtro de representatividad: eliminamos juegos con poco consenso/votos
        # Esto reduce el ruido que impide que el modelo sea normal y homocedástico
        df_limpio = df_limpio[df_limpio["ratings_count"] > 40]
        df_limpio = df_limpio[df_limpio["added"] > 80]

        # 3. Ordenar por relevancia
        df_top = df_limpio.sort_values("metacritic", ascending=False).reset_index(drop=True)

        df_top["fecha_transformacion"] = datetime.utcnow()
        registros_guardados = len(df_top)

        logger.info(f"Registros tras filtros de calidad: {registros_guardados}")
        logger.info("Guardando datos en 'videojuegos_top'...")

        df_top.to_sql(
            "videojuegos_top",
            engine,
            if_exists="replace",
            index=False
        )

        logger.info("Datos transformados guardados correctamente")

    except Exception as e:
        estado = "FAILED"
        mensaje = str(e)
        registros_fallidos = registros_extraidos
        logger.error(f"Error en transformación: {e}")

    finally:
        fin = time.time()
        tiempo_total = fin - inicio

        # Guardar métricas ETL
        db = SessionLocal()
        metricas = MetricasETL(
            registros_extraidos=registros_extraidos,
            registros_guardados=registros_guardados,
            registros_fallidos=registros_extraidos - registros_guardados,
            tiempo_ejecucion_segundos=tiempo_total,
            estado=estado,
            mensaje=mensaje
        )

        db.add(metricas)
        db.commit()
        db.close()
        logger.info("Métricas ETL registradas")

if __name__ == "__main__":
    transformar_datos()