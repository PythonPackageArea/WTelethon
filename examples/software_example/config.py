import os
from pathlib import Path

# Базовые пути
CONTEXT_DIR_PATH = Path("examples", "data")
SESSIONS_DIR_PATH = CONTEXT_DIR_PATH / "sessions"
PROXIES_FILE_PATH = CONTEXT_DIR_PATH / "proxies.txt"

# Пути для сессий
ALIVE_DIR_PATH = SESSIONS_DIR_PATH / "alive"
WRONG_FORMAT_DIR_PATH = SESSIONS_DIR_PATH / "wrong"
DEAD_DIR_PATH = SESSIONS_DIR_PATH / "dead"

# Настройки прокси
PROXY_TYPE = os.getenv("PROXY_TYPE", "http")

# Telegram API настройки
API_ID = int(os.getenv("API_ID", "12345"))
API_HASH = os.getenv("API_HASH", "your_api_hash_here")

# Настройки работы
CONNECTION_RETRIES = int(os.getenv("CONNECTION_RETRIES", "0"))
SLEEP_INTERVAL = int(os.getenv("SLEEP_INTERVAL", "1"))
