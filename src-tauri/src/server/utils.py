import re
import json

def is_email_valid(email: str) -> bool:
    return bool(re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email))

def make_size_human_readable(size: int | None) -> str:
    if size is None:
        return "0 B"
    if size < 1024:
        return f"{size} B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.2f} KB"
    elif size < 1024 * 1024 * 1024:
        return f"{size / 1024 / 1024:.2f} MB"
    else:
        return f"{size / 1024 / 1024 / 1024:.2f} GB"

def safe_json_loads(value: any) -> any:
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return value

def err_msg(message: str, traceback: str) -> str:
    return f"{message}\nError: {traceback}"

def parse_err_msg(message: str | bytes) -> tuple[str, str] | tuple[bytes, bytes]:
    if not message:
        return b"", b""

    return_bytes = False
    if isinstance(message, bytes):
        message = message.decode("utf-8")
        return_bytes = True

    if "Error:" not in message:
        if return_bytes:
            return message.encode("utf-8"), b""
        else:
            return message, ""

    message = message.split("\nError:", 1)

    if "Traceback" in message[0]:
        message[0] = message[0].split("Traceback (most recent call last):", 1)[0]

    len_message = len(message)
    if return_bytes:
        message[0] = message[0].encode("utf-8")
        if len_message > 1:
            message[1] = message[1].encode("utf-8")

    return (message[0], message[1] if len_message > 1 else b"" if return_bytes else "")
