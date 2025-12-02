from contextlib import asynccontextmanager
from app.config.database import init_db
from app.core.redis_utils.otp_handler.config import otp_client
from app.config.logger import get_logger

logger = get_logger("lifespan")


@asynccontextmanager
async def lifespan(app):
    """Startup & shutdown lifecycle management."""

    # Redis Check
    try:
        await otp_client.ping()
        logger.info("✅ Redis connected successfully")
    except Exception as e:
        logger.error(f"❌ Redis connection failed: {e}")

    # DB Check (sync)
    init_db()

    yield

    otp_client.close()
    logger.info("🛑 Application shutting down...")
