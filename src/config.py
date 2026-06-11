"""
設定模組 - 管理應用程式設定
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 專案根目錄
BASE_DIR = Path(__file__).parent.parent

class Config:
    """基礎設定"""
    
    # TWSE API 設定
    TWSE_BASE_URL = os.getenv("TWSE_BASE_URL", "https://www.twse.com.tw/")
    TWSE_API_TIMEOUT = int(os.getenv("TWSE_API_TIMEOUT", "30"))
    TWSE_MAX_RETRIES = int(os.getenv("TWSE_MAX_RETRIES", "3"))
    
    # 資料庫設定
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./twse_data.db")
    
    # 快取設定
    CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() == "true"
    CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))
    CACHE_TYPE = os.getenv("CACHE_TYPE", "memory")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # 日誌設定
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "logs/twse.log")
    
    # API 頻率限制
    API_RATE_LIMIT = int(os.getenv("API_RATE_LIMIT", "100"))
    API_RATE_LIMIT_PERIOD = int(os.getenv("API_RATE_LIMIT_PERIOD", "60"))


class DevelopmentConfig(Config):
    """開發環境設定"""
    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    """測試環境設定"""
    DEBUG = True
    TESTING = True
    DATABASE_URL = "sqlite:///:memory:"


class ProductionConfig(Config):
    """生產環境設定"""
    DEBUG = False
    TESTING = False


def get_config(env: str = None) -> Config:
    """
    根據環境取得設定物件
    
    Args:
        env: 環境名稱 (development, testing, production)
        
    Returns:
        Config 物件
    """
    if env is None:
        env = os.getenv("ENV", "development")
    
    config_map = {
        "development": DevelopmentConfig,
        "testing": TestingConfig,
        "production": ProductionConfig,
    }
    
    return config_map.get(env, DevelopmentConfig)()


# 預設設定
config = get_config()
