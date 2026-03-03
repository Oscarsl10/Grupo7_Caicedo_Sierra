from scripts.database import SessionLocal
from scripts.models import Ciudad, RegistroClima, MetricasETL
import pandas as pd
from datetime import datetime
import time


def cargar_csv_a_bd():
    db = SessionLocal()

    inicio = time.time()

    registros_extraidos = 0
    registros_guardados = 0
    registros_fallidos = 0

    try:
        # Leer CSV
        df = pd.read_csv("data/clima.csv")
        registros_extraidos = len(df)

        for _, row in df.iterrows():
            try:
                # Buscar o crear ciudad
                ciudad = db.query(Ciudad).filter_by(nombre=row["ciudad"]).first()

                if not ciudad:
                    ciudad = Ciudad(nombre=row["ciudad"])
                    db.add(ciudad)
                    db.commit()
                    db.refresh(ciudad)

                # Insertar registro clima
                registro = RegistroClima(
                    ciudad_id=ciudad.id,
                    temperatura=row["temperatura"],
                    sensacion_termica=row["sensacion_termica"],
                    humedad=row["humedad"],
                    velocidad_viento=row["velocidad_viento"],
                    descripcion=row["descripcion"],
                    fecha_extraccion=datetime.now()
                )

                db.add(registro)
                registros_guardados += 1

            except Exception:
                registros_fallidos += 1

        db.commit()
        estado = "SUCCESS"

    except Exception as e:
        print("❌ Error general:", e)
        estado = "FAILED"

    # Calcular duración
    fin = time.time()
    duracion = fin - inicio

    # Guardar métricas ETL
    metrica = MetricasETL(
        estado=estado,
        registros_extraidos=registros_extraidos,
        registros_guardados=registros_guardados,
        registros_fallidos=registros_fallidos,
        tiempo_ejecucion_segundos=duracion
    )

    db.add(metrica)
    db.commit()
    db.close()

    print("✅ Datos cargados en PostgreSQL correctamente")
    print("📊 Métricas ETL registradas correctamente")


if __name__ == "__main__":
    cargar_csv_a_bd()