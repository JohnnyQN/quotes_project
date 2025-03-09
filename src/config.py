import os

class Config:
    """Base configuration class"""
    SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key_here")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 5,
        "max_overflow": 10,
        "pool_timeout": 30
    }
    SESSION_TYPE = "filesystem"
    SESSION_PERMANENT = False  
    SESSION_USE_SIGNER = True
    SESSION_COOKIE_HTTPONLY = True
    DEBUG = False

class DevelopmentConfig(Config):
    """Configuration for development"""
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///dev.db")
    DEBUG = True

class ProductionConfig(Config):
    """Configuration for production"""
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql:///prod.db")
    DEBUG = False

config_options = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig
}
