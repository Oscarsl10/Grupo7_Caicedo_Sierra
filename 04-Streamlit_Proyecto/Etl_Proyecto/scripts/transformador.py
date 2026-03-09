#!/usr/bin/env python3

import logging
import time
import pandas as pd
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

        logger.info("Leyendo datos desde PostgreSQL...")

        query = text("""
            SELECT nombre, fecha_lanzamiento, rating, metacritic
            FROM videojuegos
        """)

        df = pd.read_sql(query, engine)

        registros_extraidos = len(df)

        logger.info(f"Registros extraídos: {registros_extraidos}")

        # Transformación: Top 20 juegos por rating
        df_top = df.nlargest(20, "rating")

        df_top["fecha_transformacion"] = datetime.utcnow()

        registros_guardados = len(df_top)

        logger.info("Guardando datos transformados...")

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
            registros_fallidos=registros_fallidos,
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