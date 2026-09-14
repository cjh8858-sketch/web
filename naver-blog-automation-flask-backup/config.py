import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / ".env")

class Config:
    """Default configuration"""
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev_secret_key")
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    FLASK_PORT = int(os.getenv("FLASK_PORT", 5000))
    FLASK_HOST = os.getenv("FLASK_HOST", "127.0.0.1")

    DB_PATH = BASE_DIR / "data" / "app.db"
    DATA_DIR = BASE_DIR / "data"
    LOGS_DIR = BASE_DIR / "logs"
    SESSION_STATE_PATH = DATA_DIR / "naver_session.json"
    IMAGES_DIR = DATA_DIR / "images"

    CLAUDE_CLI_TIMEOUT_SEC = int(os.getenv("CLAUDE_CLI_TIMEOUT_SEC", 180))
    PLAYWRIGHT_LAUNCH_TIMEOUT = int(os.getenv("PLAYWRIGHT_LAUNCH_TIMEOUT", 30000))
    NAVER_LOGIN_TIMEOUT_SEC = int(os.getenv("NAVER_LOGIN_TIMEOUT_SEC", 300))
    IMAGE_DOWNLOAD_TIMEOUT_SEC = int(os.getenv("IMAGE_DOWNLOAD_TIMEOUT_SEC", 30))

    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    @staticmethod
    def ensure_dirs():
        """Create required directories if not exist"""
        for dir_path in [Config.DATA_DIR, Config.LOGS_DIR, Config.IMAGES_DIR]:
            dir_path.mkdir(parents=True, exist_ok=True)
