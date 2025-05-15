import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

class APIConfig:
    # Basic Configurations
    API_VERSION = os.getenv('KEYBRIDGE_API_VERSION', "unknown")
    DEBUG = os.getenv('KEYBRIDGE_DEBUG', "False").lower() == "true"
    API_PORT = int(os.getenv('KEYBRIDGE_API_PORT', 5000))

    # Database Configurations
    POSTGRES_USERNAME = os.getenv('KEYBRIDGE_DB_USERNAME', "keybridge_db_user")
    POSTGRES_PASSWORD = os.getenv('KEYBRIDGE_DB_PASSWORD', "keybridge_db_password")
    POSTGRES_HOST = os.getenv('KEYBRIDGE_DB_HOST', "127.0.0.1")
    POSTGRES_PORT = int(os.getenv('KEYBRIDGE_DB_PORT', 5431))
    POSTGRES_DB_NAME = os.getenv('KEYBRIDGE_DB_NAME', "keybridge")

    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{POSTGRES_USERNAME}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT Configurations
    JWT_SECRET_KEY = os.getenv('KEYBRIDGE_JWT_SECRET_KEY', 'abc')
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=4)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=15)

    # Rate Limiting (e.g., 30 requests per minute, 5 per second)
    RATE_LIMITS = ["30 per minute", "5 per second"]

    # Other settings
    LOGGING_LEVEL = os.getenv('KEYBRIDGE_LOGGING_LEVEL', 'INFO')

class DevelopmentAPIConfig(APIConfig):
    DEBUG = True

class ProductionAPIConfig(APIConfig):
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False