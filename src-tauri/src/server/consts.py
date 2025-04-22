import os
from dotenv import load_dotenv
from typing import cast

load_dotenv()

APP_NAME = cast(str, os.getenv("APP_NAME"))
HOST = cast(str, os.getenv("HOST"))

trusted_hosts = cast(str, os.getenv("TRUSTED_HOSTS"))
TRUSTED_HOSTS = [host.strip() for host in trusted_hosts.split(",")]

port_range = cast(str, os.getenv("PORT_RANGE"))
PORT_RANGE = [int(p.strip()) for p in port_range.split(",")]
