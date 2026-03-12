#!/usr/bin/env python3
import os
import requests
import time
from datetime import datetime
from dotenv import load_dotenv
import logging

from scripts.database import SessionLocal
from scripts.models import Ciudad, RegistroClima, MetricasETL

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/etl.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class WeatherstackExtractor:

    def __init__(self):

        self.api_key = os.getenv('API_KEY')
        self.base_url = os.getenv('WEATHERSTACK_BASE_URL')

        ciudades_env = os.getenv('CIUDADES')

        if not ciudades_env:
            raise ValueError("CIUDADES no configuradas en .env")

        self.ciudades = ciudades_env.split(',')

        if not self.api_key:
            raise ValueError("API_KEY no configurada en .env")

    # ---------------------------------------
    # EXTRACT
    # ---------------------------------------

    def extraer_clima(self, ciudad):

        try:

            url = f"{self.base_url}/current"

            params = {
                'access_key': self.api_key,
                'query': ciudad.strip()
            }

            response = requests.get(url, params=params, timeout=10)

            response.raise_for_status()

            data = response.json()

            if 'error' in data:
                logger.error(f"Error API para {ciudad}: {data['error']['info']}")
                return None

            logger.info(f"Datos extraídos para {ciudad}")

            return data

        except Exception as e:

            logger.error(f"Error extrayendo datos para {ciudad}: {str(e)}")

            return None

    # ---------------------------------------
    # TRANSFORM
    # ---------------------------------------

    def procesar_respuesta(self, response_data):

        try:

            current = response_data.get('current', {})
            location = response_data.get('location', {})

            lat = location.get('lat')
            lon = location.get('lon')

            datos = {

                'ciudad': location.get('name'),
                'pais': location.get('country'),
                'latitud': float(lat) if lat else None,
                'longitud': float(lon) if lon else None,

                'temperatura': current.get('temperature'),
                'sensacion_termica': current.get('feelslike'),
                'humedad': current.get('humidity'),
                'velocidad_viento': current.get('wind_speed'),
                'descripcion': current.get('weather_descriptions', ['N/A'])[0],
                'codigo_tiempo': current.get('weather_code'),

                'fecha_extraccion': datetime.now()

            }

            return datos

        except Exception as e:

            logger.error(f"Error procesando respuesta: {str(e)}")

            return None

    # ---------------------------------------
    # EXTRACT LOOP
    # ---------------------------------------

    def ejecutar_extraccion(self):

        datos_extraidos = []

        logger.info(f"Iniciando extracción para {len(self.ciudades)} ciudades")

        for ciudad in self.ciudades:

            response = self.extraer_clima(ciudad)

            if response:

                datos_procesados = self.procesar_respuesta(response)

                if datos_procesados:
                    datos_extraidos.append(datos_procesados)

            # Esperar para evitar límite de la API
            time.sleep(2)

        return datos_extraidos

    # ---------------------------------------
    # LOAD (POSTGRESQL)
    # ---------------------------------------

    def guardar_en_db(self, datos):

        db = SessionLocal()

        registros_guardados = 0

        try:

            for dato in datos:

                ciudad = db.query(Ciudad).filter_by(nombre=dato["ciudad"]).first()

                if not ciudad:

                    ciudad = Ciudad(
                        nombre=dato["ciudad"],
                        pais=dato["pais"],
                        latitud=dato["latitud"],
                        longitud=dato["longitud"]
                    )

                    db.add(ciudad)
                    db.commit()
                    db.refresh(ciudad)

                registro = RegistroClima(

                    ciudad_id=ciudad.id,

                    temperatura=dato["temperatura"],
                    sensacion_termica=dato["sensacion_termica"],
                    humedad=dato["humedad"],
                    velocidad_viento=dato["velocidad_viento"],
                    descripcion=dato["descripcion"],
                    codigo_tiempo=dato["codigo_tiempo"],

                    fecha_extraccion=dato["fecha_extraccion"]

                )

                db.add(registro)

                registros_guardados += 1

            db.commit()

            logger.info(f"{registros_guardados} registros guardados en PostgreSQL")

            return registros_guardados

        except Exception as e:

            db.rollback()

            logger.error(f"Error guardando datos: {str(e)}")

            return 0

        finally:

            db.close()


# ---------------------------------------
# EJECUCIÓN ETL
# ---------------------------------------

if __name__ == "__main__":

    try:

        inicio = datetime.now()

        extractor = WeatherstackExtractor()

        datos = extractor.ejecutar_extraccion()

        registros_guardados = extractor.guardar_en_db(datos)

        fin = datetime.now()

        duracion = (fin - inicio).total_seconds()

        db = SessionLocal()

        metricas = MetricasETL(

            registros_extraidos=len(datos),
            registros_guardados=registros_guardados,
            registros_fallidos=len(datos) - registros_guardados,
            tiempo_ejecucion_segundos=duracion,
            estado="SUCCESS",
            mensaje="ETL ejecutado correctamente"

        )

        db.add(metricas)

        db.commit()

        db.close()

        print("\n================================")
        print("ETL FINALIZADO")
        print("================================")
        print(f"Ciudades procesadas: {len(datos)}")
        print(f"Registros guardados: {registros_guardados}")
        print(f"Duración: {duracion} segundos")
        print("================================\n")

    except Exception as e:

        logger.error(f"Error en ETL: {str(e)}")