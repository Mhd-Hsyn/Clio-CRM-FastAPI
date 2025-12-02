import os
from typing import Optional
from pydantic_settings import BaseSettings
from urllib.parse import quote_plus


class Settings(BaseSettings):
    # MongoDB
    db_name: str
    db_user: str
    db_password: str
    db_host: str
    db_port: str

    # Security
    secret_key: str
    user_jwt_token_key: str
    admin_jwt_token_key: str
    debug: bool

    # Redis
    redis_host: str
    redis_port: int
    redis_password: str
    redis_otp_db: int
    redis_rate_limit_db: int

    # RabbitMQ
    rabbitmq_host: str
    rabbitmq_port: int
    rabbitmq_user: str
    rabbitmq_password: str
    rabbitmq_email_sending_queue: str
    rabbitmq_email_sending_exchange: str
    rabbitmq_email_sending_routing_key: str

    # Encryption
    otp_fernet_key: str

    BACKEND_API_BASE_URL: str = "https://ai-call-assistant-api.devssh.xyz"

    # Storage settings
    # STORAGE_BACKEND: str = "local"  # Default local storage
    STORAGE_BACKEND: str = "s3"  # Default local storage
    LOCAL_MEDIA_PATH: str = "media/"  # Default path

    # AWS S3 (optional)
    AWS_STORAGE_BUCKET_NAME: Optional[str] = None
    AWS_S3_REGION_NAME: Optional[str] = "us-east-1"  # Default region
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_CLOUDFRONT_DOMAIN: Optional[str] = None  # Optional CDN
    S3_BASE_PATH: Optional[str] = "ai-call-assistant-data"
    S3_ENDPOINT: Optional[str] = None

    class Config:
        env_file = ".env"

    @property
    def sqlalchemy_database_uri(self) -> str:
        password = quote_plus(self.db_password)
        # url= f"postgresql+asyncpg://{self.db_user}:{password}@{self.db_host}:{self.db_port}/{self.db_name}"
        url= f"postgresql+psycopg2://{self.db_user}:{password}@{self.db_host}:{self.db_port}/{self.db_name}"
        return url



# Initialize settings
settings = Settings()


# Media settings
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDIA_DIR = os.path.join(BASE_DIR, "..", "media")
MEDIA_URL = "/media/"

# Ensure the folder exists
os.makedirs(MEDIA_DIR, exist_ok=True)
