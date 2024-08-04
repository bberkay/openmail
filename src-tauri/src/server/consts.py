import os

APP_NAME = "OpenMail"
HOME_DIR = os.path.expanduser("~")
APP_DIR = os.path.join(HOME_DIR, ".openmail")
SECRETS_DIR = os.path.join(APP_DIR, "secrets")
DB_DIR = os.path.join(APP_DIR, "database")
LOG_DIR = os.path.join(APP_DIR, "logs")
UVICORN_PID_FILE_PATH = os.path.join(APP_DIR, "uvicorn.pid")
UVICORN_URL_FILE_PATH = os.path.join(APP_DIR, "uvicorn.server")
UVICORN_LOG_FILE_PATH = os.path.join(LOG_DIR, "uvicorn.log")
UVICORN_DB_FILE_PATH = os.path.join(DB_DIR, "uvicorn.db")
PRAGMA_KEY_FILE_PATH = os.path.join(SECRETS_DIR, "pragma.key")
CIPHER_KEY_FILE_PATH = os.path.join(SECRETS_DIR, "cipher.key")
