import os, json
from consts import APP_NAME

class FileSystem:
    def __init__(self):
        self.APP_DIR = os.path.join(os.path.expanduser("~"), "." + APP_NAME)
        self.LOG_DIR = os.path.join(self.APP_DIR, "logs")
        self.CONFIG_DIR = os.path.join(self.APP_DIR, "config")
        self.UVICORN_INFO_FILE_PATH = os.path.join(self.APP_DIR, "uvicorn.info")
        self.UVICORN_LOG_FILE_PATH = os.path.join(self.LOG_DIR, "uvicorn.log")
        self.PREFERENCES_FILE_PATH = os.path.join(self.CONFIG_DIR, "preferences.json")

    def init(self) -> None:
        self.__create_dirs()
        self.__create_log_file()
        self.__create_preferences_file()

    def __create_dirs(self) -> None:
        if not os.path.exists(self.APP_DIR):
            os.makedirs(self.APP_DIR, exist_ok=True)

        for directory in [self.CONFIG_DIR, self.LOG_DIR]:
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)

    def __create_preferences_file(self) -> None:
        with open(self.PREFERENCES_FILE_PATH, "w") as preferences_file:
            json.dump({}, preferences_file)

    def __create_log_file(self) -> None:
        if not os.path.exists(self.UVICORN_LOG_FILE_PATH):
            with open(self.UVICORN_LOG_FILE_PATH, "w") as uvicorn_log_file:
                uvicorn_log_file.write("")

    def create_uvicorn_info_file(self, host: str, port: str, pid: str) -> None:
        with open(self.UVICORN_INFO_FILE_PATH, "w") as uvicorn_info_file:
            uvicorn_info_file.write(f"URL=http://{host}:{port}\n")
            uvicorn_info_file.write(f"PID={pid}")

    def get_preferences(self) -> dict:
        if os.path.exists(self.PREFERENCES_FILE_PATH):
            with open(self.PREFERENCES_FILE_PATH, "r") as preferences_file:
                return json.load(preferences_file)
        else:
            raise Exception("Preferences file not found")
