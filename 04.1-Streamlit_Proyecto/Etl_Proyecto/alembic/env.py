import os
import sys
from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool
from alembic import context

# Cargar variables de entorno
load_dotenv()

# Permitir importar módulos del proyecto
sys.path.insert(0, '.')

# Importar configuración de base de datos
from scripts.database import DATABASE_URL, Base

# IMPORTAR MODELOS PARA QUE ALEMBIC LOS DETECTE
from scripts.models import Videojuego

# Configuración de Alembic
config = context.config

# Establecer URL de la base de datos
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Metadata de los modelos
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Ejecuta migraciones en modo offline"""
    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Ejecuta migraciones en modo online"""

    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:

        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()