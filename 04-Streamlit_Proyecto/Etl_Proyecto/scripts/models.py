#!/usr/bin/env python3

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Date, DateTime
from scripts.database import Base


class Videojuego(Base):
    """Tabla con datos crudos obtenidos de la API"""
    __tablename__ = "videojuegos"

    id = Column(Integer, primary_key=True, autoincrement=True)

    nombre = Column(String(200), nullable=False, index=True)

    fecha_lanzamiento = Column(Date, nullable=True)

    rating = Column(Float, nullable=True)

    metacritic = Column(Float, nullable=True)

    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Videojuego(nombre='{self.nombre}', rating={self.rating})>"


class VideojuegoTop(Base):
    """Tabla transformada con los mejores videojuegos"""
    __tablename__ = "videojuegos_top"

    id = Column(Integer, primary_key=True, autoincrement=True)

    nombre = Column(String(200), nullable=False)

    fecha_lanzamiento = Column(Date, nullable=True)

    rating = Column(Float, nullable=True)

    metacritic = Column(Float, nullable=True)

    fecha_transformacion = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<VideojuegoTop(nombre='{self.nombre}', rating={self.rating})>"


class MetricasETL(Base):
    """Modelo para registrar métricas de cada ejecución del ETL"""
    __tablename__ = "metricas_etl"

    id = Column(Integer, primary_key=True, autoincrement=True)

    fecha_ejecucion = Column(DateTime, default=datetime.utcnow, index=True)

    registros_extraidos = Column(Integer, nullable=False)

    registros_guardados = Column(Integer, nullable=False)

    registros_fallidos = Column(Integer, default=0)

    tiempo_ejecucion_segundos = Column(Float, nullable=False)

    estado = Column(String(50), nullable=False)  # SUCCESS, PARTIAL, FAILED

    mensaje = Column(String(500), nullable=True)

    def __repr__(self):
        return f"<MetricasETL(estado='{self.estado}', registros={self.registros_guardados})>"