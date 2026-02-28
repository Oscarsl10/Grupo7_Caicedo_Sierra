from scripts.database import SessionLocal
from scripts.models import Ciudad, RegistroClima
import pandas as pd
from datetime import datetime

def cargar_csv_a_bd():
    db = SessionLocal()

    # Leer el CSV que genera el extractor
    df = pd.read_csv("data/clima.csv")

    for _, row in df.iterrows():

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

    db.commit()
    db.close()

    print("✅ Datos cargados en PostgreSQL correctamente")

if __name__ == "__main__":
    cargar_csv_a_bd()
