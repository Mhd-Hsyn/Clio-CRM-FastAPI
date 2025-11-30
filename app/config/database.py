from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.core.models.base import BaseModel
from app.config.logger import get_logger
from .settings import settings

logger = get_logger("database.py")

# Create async engine
engine = create_async_engine(settings.sqlalchemy_database_uri, echo=True)

# Create async session factory
async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

async def init_db():
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))  # Wrap string in text()
        logger.info("✅ PostgreSQL connected successfully")
    except Exception as e:
        logger.error(f"❌ PostgreSQL connection failed: {e}")


def get_db():
    db = async_session()
    try:
        yield db
    finally:
        db.close()
