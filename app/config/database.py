from fastapi.concurrency import run_in_threadpool
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from app.config.logger import get_logger
from .settings import settings

logger = get_logger("database.py")

engine = create_engine(
    settings.sqlalchemy_database_uri,
    echo=True,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def init_db():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✅ PostgreSQL connected successfully")
    except Exception as e:
        logger.error(f"❌ PostgreSQL connection failed: {e}")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



async def save_instance(instance, db: Session):
    def commit_sync():
        db.add(instance)
        db.commit()
        db.refresh(instance)
    await run_in_threadpool(commit_sync)


