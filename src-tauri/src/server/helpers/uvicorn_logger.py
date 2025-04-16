import sys
import json

import logging
from typing import Any
from logging.handlers import RotatingFileHandler

from fastapi import WebSocket, Request

from utils import make_size_human_readable, safe_json_loads
from consts import APP_NAME
from .file_system import FileSystem

"""
Constants
"""
MAX_BYTES_TO_LOG = 1 * 1024 * 1024 # 1 MB
MAX_BACKUP_COUNT = 5
# Character count
MAX_SUMMARIZED_DATA_LENGTH = 256
DATA_PREVIEW_LENGTH = 5
CENSOR_TRACE_LENGTH = 10

class UvicornLogger(logging.Logger):
    def __init__(self):
        super().__init__(APP_NAME)
        self.name = APP_NAME
        self._initialize_handlers()

    def _initialize_handlers(self) -> None:
        self.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)

        file_handler = RotatingFileHandler(
            FileSystem().get_uvicorn_log().fullpath,
            maxBytes=MAX_BYTES_TO_LOG,
            backupCount=MAX_BACKUP_COUNT
        )
        file_handler.setFormatter(formatter)

        self.addHandler(stream_handler)
        self.addHandler(file_handler)

    def _censor(self, data: Any) -> dict | str:
        def mask(data: str):
            return f"{data}{"*" * CENSOR_TRACE_LENGTH}"

        if not data:
            return ""

        if isinstance(data, dict):
            return {
                key: f"{mask(json.dumps(value)[:DATA_PREVIEW_LENGTH])}" if value else ""
                for key, value in data.items()
            }
        elif isinstance(data, list):
            return f"[{mask(str(data)[1:DATA_PREVIEW_LENGTH])}]" if data[0] else "[]"
        elif isinstance(data, str):
            return f"{mask(data[:DATA_PREVIEW_LENGTH])}"

        return "`response_data` could not censored properly."

    def _summarize(self, data: Any) -> dict | str:
        if isinstance(data, dict):
            return {key: self._summarize(value) for key, value in data.items()}
        elif isinstance(data, list):
            return self._summarize(str(data))
        elif isinstance(data, str) and len(data) >= MAX_SUMMARIZED_DATA_LENGTH:
            return f"{data[:MAX_SUMMARIZED_DATA_LENGTH]}...{']' if data.startswith('[') else ''}"
        return data

    def request(self, request: Request, response: Any) -> None:
        try:
            response_data = safe_json_loads(response._body)
            if isinstance(response_data, dict) and "data" in response_data.keys():
                response_data["data"] = self._censor(response_data["data"])

            log_message = (
                f"{request.method} {request.url} - {response.status_code} - "
                f"{self._summarize(response_data)} - "
                f"{make_size_human_readable(int(response.headers.get('content-length', '0')))}"
            )

            if response.status_code >= 400:
                self.error(log_message)
            elif response.status_code != 307: # Temporary Redirect
                self.info(log_message)

        except Exception as e:
            self.error("Error while logging request and response: %s" % str(e))

    def websocket(self, websocket: WebSocket, response: Any) -> None:
        try:
            response = (
                self._censor(response)
                if isinstance(response, dict)
                else safe_json_loads(response)
            )

            log_message = (
                f"WebSocket {str(websocket.url)}"
                f"{self._summarize(response)} - "
                f"{make_size_human_readable(len(response))}"
            )

            if isinstance(response, str) and "error" in response.lower():
                self.error(log_message)
            else:
                self.info(log_message)

        except Exception as e:
            self.error("Error while logging request and response: %s" % str(e))
