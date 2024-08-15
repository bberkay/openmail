import os

from cryptography.fernet import Fernet

class FileSystem:
    def __init__(self):
        self.HOME_DIR = os.path.expanduser("~")
        self.APP_DIR = os.path.join(self.HOME_DIR, ".openmail")
        self.SECRETS_DIR = os.path.join(self.APP_DIR, "secrets")
        self.DB_DIR = os.path.join(self.APP_DIR, "database")
        self.LOG_DIR = os.path.join(self.APP_DIR, "logs")
        self.UVICORN_INFO_FILE_PATH = os.path.join(self.APP_DIR, "uvicorn.info")
        self.UVICORN_LOG_FILE_PATH = os.path.join(self.LOG_DIR, "uvicorn.log")
        self.UVICORN_DB_FILE_PATH = os.path.join(self.DB_DIR, "uvicorn.db")
        self.PRAGMA_KEY_FILE_PATH = os.path.join(self.SECRETS_DIR, "pragma.key")
        self.CIPHER_KEY_FILE_PATH = os.path.join(self.SECRETS_DIR, "cipher.key")

    def __create_dirs(self) -> None:
        for directory in [self.APP_DIR, self.SECRETS_DIR, self.DB_DIR, self.LOG_DIR]:
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)

    def __create_key_files(self) -> None:
        for key_file in [self.PRAGMA_KEY_FILE_PATH, self.CIPHER_KEY_FILE_PATH]:
            if not os.path.exists(key_file):
                with open(key_file, "wb") as key_file:
                    key_file.write(Fernet.generate_key())

    def get_pragma_key(self) -> bytes:
        with open(self.PRAGMA_KEY_FILE_PATH, "rb") as key_file:
            return key_file.read()

    def get_cipher_key(self) -> bytes:
        with open(self.CIPHER_KEY_FILE_PATH, "rb") as key_file:
            return key_file.read()

    def create_uvicorn_info_file(self, host: str, port: str, pid: str) -> None:
        with open(self.UVICORN_INFO_FILE_PATH, "w") as uvicorn_info_file:
            uvicorn_info_file.write(f"URL=http://{host}:{port}\n")
            uvicorn_info_file.write(f"PID={pid}")

    def init(self) -> None:
        self.__create_dirs()
        self.__create_key_files()
