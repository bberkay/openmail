import os
from dotenv import load_dotenv

load_dotenv()

APP_NAME = os.getenv("APP_NAME")
if APP_NAME is None:
    raise Exception("APP_NAME is not specified in .env")

HOST = os.getenv("HOST")
if HOST is None:
    raise Exception("HOST is not specified in .env")

trusted_hosts = os.getenv("TRUSTED_HOSTS")
if trusted_hosts is None:
    raise Exception("TRUSTED_HOSTS is not specified in .env")

TRUSTED_HOSTS = [host.strip() for host in trusted_hosts.split(",")]

port_range = os.getenv("PORT_RANGE")
if port_range is None:
    raise Exception("PORT_RANGE is not specified in .env")

PORT_RANGE = [int(p.strip()) for p in port_range.split(",")]
