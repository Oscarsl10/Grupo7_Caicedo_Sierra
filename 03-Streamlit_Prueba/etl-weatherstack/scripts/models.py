from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class Ciudad(Base):
    __tablename__ = "ciudades"

    id = Column(Integer, primary_key=True)
    nombre = Column(String, unique=True)

    registros = relationship("RegistroClima", back_populates="ciudad")


class RegistroClima(Base):
    __tablename__ = "registros_clima"

    id = Column(Integer, primary_key=True)
    ciudad_id = Column(Integer, ForeignKey("ciudades.id"))

    temperatura = Column(Float)
    sensacion_termica = Column(Float)
    humedad = Column(Integer)
    velocidad_viento = Column(Float)
    descripcion = Column(String)
    fecha_extraccion = Column(DateTime, default=datetime.utcnow)

    ciudad = relationship("Ciudad", back_populates="registros")


class MetricasETL(Base):
    __tablename__ = "metricas_etl"

    id = Column(Integer, primary_key=True)
    fecha_ejecucion = Column(DateTime, default=datetime.utcnow)
