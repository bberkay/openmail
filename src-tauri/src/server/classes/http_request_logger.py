import sys
import json

import logging
from logging.handlers import RotatingFileHandler

from utils import make_size_human_readable
from consts import APP_NAME

from .file_system import FileSystem

MAX_RESPONSE_DATA_LENGTH = 256
MAX_BYTES_TO_LOG = 1 * 1024 * 1024 # 1 MB
MAX_BACKUP_COUNT = 5

# Data censoring
DATA_PREVIEW_LENGTH = 5
CENSOR_TRACE_LENGTH = 10

class HTTPRequestLogger(logging.Logger):
    def __init__(self):
        super().__init__(APP_NAME)
        self.name = APP_NAME

    def init(self):
        self.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        stream_handler = logging.StreamHandler(sys.stdout)
        file_handler = RotatingFileHandler(FileSystem().root["logs"]["uvicorn.log"].fullpath, maxBytes=MAX_BYTES_TO_LOG, backupCount=MAX_BACKUP_COUNT)
        stream_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        self.addHandler(stream_handler)
        self.addHandler(file_handler)

    def _censor_data(self, response_data: any) -> str:
        if not response_data:
            return ""
        if isinstance(response_data, dict):
            return {
                key: (json.dumps(data)[:DATA_PREVIEW_LENGTH] + "*" * CENSOR_TRACE_LENGTH if data else "")
                for key, data in response_data.items()
            }
        elif isinstance(response_data, list):
            return "[" + (str(response_data)[1:DATA_PREVIEW_LENGTH] + "*" * CENSOR_TRACE_LENGTH) + "]" if response_data[0] else "[]"
        elif isinstance(response_data, str):
            return response_data[:DATA_PREVIEW_LENGTH] + "*" + CENSOR_TRACE_LENGTH
        return "`response_data` was not censored properly."

    def _summarize_data(self, response_data: any) -> any:
        if isinstance(response_data, dict):
            return {key: self._summarize_data(value) for key, value in response_data.items()}
        elif isinstance(response_data, list):
            return self._summarize_data(str(response_data))
        elif isinstance(response_data, str) and len(response_data) >= MAX_RESPONSE_DATA_LENGTH:
            return response_data[:MAX_RESPONSE_DATA_LENGTH] + '...' + (']' if response_data.startswith('[') else '')
        return response_data

    def _load_data(self, response_body: bytes) -> any:
        try:
            return json.loads(response_body)
        except json.decoder.JSONDecodeError:
            return response_body.decode("utf-8")

    def request(self, request, response):
        try:
            response_data = self._load_data(response._body)
            if "data" in response_data.keys():
                response_data["data"] = self._censor_data(response_data["data"])

            log_message = (
                f"{request.method} {request.url} - {response.status_code} - "
                f"{self._summarize_data(response_data)} - "
                f"{make_size_human_readable(int(response.headers.get('content-length')))}"
            )
            if response.status_code >= 400:
                self.error(log_message)
            elif response.status_code != 307: # Temporary Redirect
                self.info(log_message)
        except Exception as e:
            self.error("Error while logging request and response: %s" % str(e))
