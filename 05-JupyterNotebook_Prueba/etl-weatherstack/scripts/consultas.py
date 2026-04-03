#!/usr/bin/env python3

from scripts.database import SessionLocal
from scripts.models import Ciudad, RegistroClima, MetricasETL

from sqlalchemy import func


def temperatura_promedio_por_ciudad(db):
    print("\n🌡 TEMPERATURA PROMEDIO POR CIUDAD")

    resultados = (
        db.query(
            Ciudad.nombre,
            func.avg(RegistroClima.temperatura).label("temp_promedio")
        )
        .join(RegistroClima)
        .group_by(Ciudad.nombre)
        .all()
    )

    for ciudad, temp in resultados:
        print(f"{ciudad}: {round(temp,2)} °C")


def ciudad_mas_humeda(db):
    print("\n💧 CIUDAD CON MAYOR HUMEDAD")

    resultado = (
        db.query(
            Ciudad.nombre,
            func.max(RegistroClima.humedad)
        )
        .join(RegistroClima)
        .group_by(Ciudad.nombre)
        .order_by(func.max(RegistroClima.humedad).desc())
        .first()
    )

    if resultado:
        print(f"{resultado[0]} con humedad de {resultado[1]}%")


def ciudad_mas_viento(db):
    print("\n🌬 CIUDAD CON MAYOR VELOCIDAD DE VIENTO")

    resultado = (
        db.query(
            Ciudad.nombre,
            func.max(RegistroClima.velocidad_viento)
        )
        .join(RegistroClima)
        .group_by(Ciudad.nombre)
        .order_by(func.max(RegistroClima.velocidad_viento).desc())
        .first()
    )

    if resultado:
        print(f"{resultado[0]} con viento de {resultado[1]} km/h")


def ultimas_ejecuciones_etl(db):
    print("\n📊 ÚLTIMAS EJECUCIONES DEL ETL")

    resultados = (
        db.query(MetricasETL)
        .order_by(MetricasETL.fecha_ejecucion.desc())
        .limit(5)
        .all()
    )

    for r in resultados:
        print(
            f"Fecha: {r.fecha_ejecucion} | "
            f"Extraídos: {r.registros_extraidos} | "
            f"Guardados: {r.registros_guardados} | "
            f"Estado: {r.estado}"
        )


if __name__ == "__main__":

    db = SessionLocal()

    try:

        temperatura_promedio_por_ciudad(db)

        ciudad_mas_humeda(db)

        ciudad_mas_viento(db)

        ultimas_ejecuciones_etl(db)

    finally:

        db.close()