import os
from pathlib import Path


class Config:
    BASE_DIR = Path(__file__).parent.parent
    
    LOG_PATH = Path(os.environ.get("LOCALAPPDATA", "")) / "Blizzard" / "Hearthstone" / "Logs" / "Power.log"
    
    API_HOST = "127.0.0.1"
    API_PORT = 8000
    
    DATA_DIR = BASE_DIR / "data"
    DECKS_DIR = DATA_DIR / "decks"
    
    # Kimi AI 配置
    KIMI_API_KEY = "sk-kimi-3dMYfcl0DkDrLP0OzEknEIXQaxAReOxtR0SI5cUD2ZdWgqNFDAmGupTmL79f9c08"
    
    # AI 功能开关
    ENABLE_AI = True
    
    @classmethod
    def ensure_dirs(cls):
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)
        cls.DECKS_DIR.mkdir(parents=True, exist_ok=True)
