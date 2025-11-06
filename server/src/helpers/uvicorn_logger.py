import sys
import json
import re
from datetime import datetime

import logging
from typing import Any, Mapping
from logging.handlers import RotatingFileHandler

from fastapi import WebSocket, Request

from ..utils import make_size_human_readable, safe_json_loads
from ..consts import APP_NAME
from ..internal.file_system import FileObject, Root

"""
Constants
"""
MAX_BYTES_TO_LOG = 1 * 1024 * 1024 # 1 MB
MAX_BACKUP_COUNT = 5
# Character count
MAX_SUMMARIZED_DATA_LENGTH = 256
DATA_PREVIEW_LENGTH = 5
CENSOR_TRACE_LENGTH = 10

"""
Sensitive Data Masking Patterns
"""
SENSITIVE_PATTERNS = [
    re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'),  # Email pattern
]

uvicorn_logs = Root("logs")
uvicorn_log = FileObject(f"uvicorn_{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}.log")
uvicorn_logs.append(uvicorn_log)

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
            uvicorn_log.fullpath,
            maxBytes=MAX_BYTES_TO_LOG,
            backupCount=MAX_BACKUP_COUNT
        )
        file_handler.setFormatter(formatter)

        self.addHandler(stream_handler)
        self.addHandler(file_handler)

    def _mask(self, text: str) -> str:
        return f"{text[1:DATA_PREVIEW_LENGTH]}{"*" * CENSOR_TRACE_LENGTH}"

    def _censor(self, data: Any) -> dict | str:
        if not data:
            return ""

        if isinstance(data, dict):
            return {
                key: f"{self._mask(json.dumps(value))}" if value else ""
                for key, value in data.items()
            }
        elif isinstance(data, list):
            return f"[{self._mask(str(data))}]" if data[0] else "[]"
        elif isinstance(data, str):
            return f"{self._mask(data)}"

        return "`data` could not censored properly."

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

    def _find_sensitive_keywords(self, msg: str) -> str:
        for pattern in SENSITIVE_PATTERNS:
            matches = pattern.findall(msg)
            for match in matches:
                masked = self._mask(match)
                msg = msg.replace(match, masked)
        return msg

    def info(
        self,
        msg: object,
        *args: object,
        exc_info: Any = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Mapping[str, object] | None = None
    ) -> None:
        if isinstance(msg, str):
            msg = self._find_sensitive_keywords(msg)
        super().info(msg, *args, exc_info=exc_info, stack_info=stack_info,
                     stacklevel=stacklevel, extra=extra)

    def debug(
        self,
        msg: object,
        *args: object,
        exc_info: Any = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Mapping[str, object] | None = None
    ) -> None:
        if isinstance(msg, str):
            msg = self._find_sensitive_keywords(msg)
        super().debug(msg, *args, exc_info=exc_info, stack_info=stack_info,
                      stacklevel=stacklevel, extra=extra)

    def warning(
        self,
        msg: object,
        *args: object,
        exc_info: Any = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Mapping[str, object] | None = None
    ) -> None:
        if isinstance(msg, str):
            msg = self._find_sensitive_keywords(msg)
        super().warning(msg, *args, exc_info=exc_info, stack_info=stack_info,
                        stacklevel=stacklevel, extra=extra)

    def error(
        self,
        msg: object,
        *args: object,
        exc_info: Any = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Mapping[str, object] | None = None
    ) -> None:
        if isinstance(msg, str):
            msg = self._find_sensitive_keywords(msg)
        super().error(msg, *args, exc_info=exc_info, stack_info=stack_info,
                      stacklevel=stacklevel, extra=extra)

    def critical(
        self,
        msg: object,
        *args: object,
        exc_info: Any = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Mapping[str, object] | None = None
    ) -> None:
        if isinstance(msg, str):
            msg = self._find_sensitive_keywords(msg)
        super().critical(msg, *args, exc_info=exc_info, stack_info=stack_info,
                         stacklevel=stacklevel, extra=extra)
