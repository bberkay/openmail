import os
import json

from consts import APP_NAME

APP_DIR = os.path.join(os.path.expanduser("~"), "." + APP_NAME)
LOG_DIR = os.path.join(APP_DIR, "logs")
CONFIG_DIR = os.path.join(APP_DIR, "config")
UVICORN_INFO_FILE_PATH = os.path.join(APP_DIR, "uvicorn.info")
UVICORN_LOG_FILE_PATH = os.path.join(LOG_DIR, "uvicorn.log")
PREFERENCES_FILE_PATH = os.path.join(CONFIG_DIR, "preferences.json")

class FileSystem:
    def init(self) -> None:
        self._create_dirs()
        self._create_log_file()
        self._create_preferences_file()

    @property
    def app_dir(self) -> str:
        return APP_DIR

    @property
    def log_dir(self) -> str:
        return LOG_DIR

    @property
    def config_dir(self) -> str:
        return CONFIG_DIR

    @property
    def uvicorn_info_file_path(self) -> str:
        return UVICORN_INFO_FILE_PATH

    @property
    def uvicorn_log_file_path(self) -> str:
        return UVICORN_LOG_FILE_PATH

    @property
    def preferences_file_path(self) -> str:
        return PREFERENCES_FILE_PATH

    def _create_dirs(self) -> None:
        if not os.path.exists(APP_DIR):
            os.makedirs(APP_DIR, exist_ok=True)

        for directory in [CONFIG_DIR, LOG_DIR]:
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)

    def _create_preferences_file(self) -> None:
        with open(PREFERENCES_FILE_PATH, "w", encoding="utf-8") as preferences_file:
            json.dump({}, preferences_file)

    def _create_log_file(self) -> None:
        if not os.path.exists(UVICORN_LOG_FILE_PATH):
            with open(UVICORN_LOG_FILE_PATH, "w", encoding="utf-8") as uvicorn_log_file:
                uvicorn_log_file.write("")

    def create_uvicorn_info_file(self, host: str, port: str, pid: str) -> None:
        with open(UVICORN_INFO_FILE_PATH, "w", encoding="utf-8") as uvicorn_info_file:
            uvicorn_info_file.write(f"URL=http://{host}:{port}\n")
            uvicorn_info_file.write(f"PID={pid}")

    def get_preferences(self) -> dict:
        if os.path.exists(PREFERENCES_FILE_PATH):
            with open(PREFERENCES_FILE_PATH, "r", encoding="utf-8") as preferences_file:
                return json.load(preferences_file)
        else:
            raise FileNotFoundError
