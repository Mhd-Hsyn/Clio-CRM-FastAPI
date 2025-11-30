from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from alembic import context
from urllib.parse import quote_plus

from app.config.settings import settings
from app.core.models.base import BaseModel
from app.auth.models import UserModel, UserWhitelistTokenModel  # only for metadata import

# Alembic Config object
config = context.config
fileConfig(config.config_file_name)

# SQLAlchemy metadata
target_metadata = BaseModel.metadata

# Build sync URL for Alembic autogenerate
sync_db_url = f"postgresql://{settings.db_user}:{quote_plus(settings.db_password)}@{settings.db_host}:{settings.db_port}/{settings.db_name}"

def run_migrations_offline():
    context.configure(
        url=sync_db_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = create_engine(sync_db_url, poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
