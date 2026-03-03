from scripts.database import engine
from scripts.models import Base

print("Creando tablas...")
Base.metadata.create_all(bind=engine)
print("Tablas creadas correctamente.")