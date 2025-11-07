"""
This module contains the main FastAPI application and its routes.
TODO: improve docstring
"""

from __future__ import annotations
import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request, Response as FastAPIResponse, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from src.internal.client_handler import ClientHandler
from src.internal.account_manager import AccountManager
from src.internal.file_system import FileObject, Root
from src.routers import account_tasks, mailbox_tasks
from src.helpers.uvicorn_logger import UvicornLogger
from src.helpers.port_scanner import PortScanner

from src._types import Response
from src.consts import DEFAULT_HOST, DEFAULT_TRUSTED_HOSTS, DEFAULT_PORT_RANGE, DEFAULT_WHITELISTED_IPS
from src.utils import is_address_valid, parse_err_msg


#################### SET UP #######################

WHITELISTED_IPS = DEFAULT_WHITELISTED_IPS

client_handler = ClientHandler()
account_manager = AccountManager()
uvicorn_logger = UvicornLogger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        client_handler.create_openmail_clients()
        yield
    finally:
        client_handler.shutdown()


app = FastAPI(lifespan=lifespan)
app.include_router(account_tasks.router)
app.include_router(mailbox_tasks.router)

def setup_api_middlewares(**kwargs):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=kwargs.get("allow_origins", ["*"]),
        allow_credentials=kwargs.get("allow_credentials", True),
        allow_methods=kwargs.get("allow_methods", ["*"]),
        allow_headers=kwargs.get("allow_headers", ["*"]),
    )
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=kwargs.get("allowed_hosts", DEFAULT_TRUSTED_HOSTS)
    )

@app.middleware("http")
async def validate_ip(request: Request, call_next):
    global WHITELISTED_IPS
    if WHITELISTED_IPS != DEFAULT_WHITELISTED_IPS:
        ip = str(request.client.host)
        if ip not in WHITELISTED_IPS:
            raise HTTPException(status_code=403, detail="Forbidden: IP not allowed")

    # Proceed if IP is allowed
    return await call_next(request)


@app.middleware("http")
async def catch_request_for_logging(request: Request, call_next):
    async def get_response_body(response: FastAPIResponse) -> bytes:
        response_body = b""
        async for chunk in response.body_iterator:
            response_body += chunk
            return response_body
        return response_body

    response = await call_next(request)
    response._body = await get_response_body(response)
    uvicorn_logger.request(request, response)
    return FastAPIResponse(
        content=parse_err_msg(response._body)[0],
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type=response.media_type,
    )


@app.get("/hello")
async def hello() -> Response:
    return Response(success=True, message="Hello, Server is ready for you!")

def main():
    global WHITELISTED_IPS

    # Config Host
    host = str(input(f"Give an HOST to app run on (e.g. {DEFAULT_HOST}): ") or DEFAULT_HOST)

    # Config Port
    while True:
        try:
            port_start_range = int(input(f"Port start range (e.g. {DEFAULT_PORT_RANGE[0]}): ") or DEFAULT_PORT_RANGE[0])
            port_end_range = int(input(f"Port end range (e.g. {DEFAULT_PORT_RANGE[1]}): ") or DEFAULT_PORT_RANGE[1])
            print(f"Finding free port between {port_start_range}-{port_end_range}...")
            port = PortScanner.find_free_port(host, port_start_range, port_end_range)
            break
        except RuntimeError:
            pass

    # Config Allowed IPs
    while True:
        YES_ANSWER_KEY = "y"
        NO_ANSWER_KEY = "n"
        CANCEL_ADDRESS_KEY = "c"
        try:
            address = input(f"Enter an IP address allowed to connect to the server or type '{CANCEL_ADDRESS_KEY}' to skip: (e.g. 192.168.1.100): ")
            if address.lower() == CANCEL_ADDRESS_KEY.lower():
                if WHITELISTED_IPS == DEFAULT_WHITELISTED_IPS:
                    confirmation = input(
                        f"No IP addresses were provided. The default will be '{DEFAULT_WHITELISTED_IPS}' — meaning anyone can connect to the server.\n"
                        f"Are you sure you want to continue? ({YES_ANSWER_KEY}/{NO_ANSWER_KEY}): "
                    ).strip().lower()
                    if confirmation == YES_ANSWER_KEY:
                        break
                    elif confirmation == NO_ANSWER_KEY:
                        continue
                    else:
                        print("Invalid response. Please enter 'y' or 'n'.")
                        continue
                else:
                    break

            if is_address_valid(address):
                if WHITELISTED_IPS == DEFAULT_WHITELISTED_IPS:
                    WHITELISTED_IPS = []
                WHITELISTED_IPS.append(address)
            else:
                print(f"Error: Given address {address} is not valid. Try again please...")
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            break
        except RuntimeError:
            pass

    # TODO: User must be able change middleware config
    setup_api_middlewares()

    # Create file system
    pid = str(os.getpid())
    etc = Root("etc")
    uvicorn_info = FileObject("uvicorn.info")
    etc.append(uvicorn_info)
    uvicorn_info.write(f"URL=http://{host}:{str(port)}\nPID={pid}\n")

    # Start server
    uvicorn_logger.info("Starting server at http://%s:%d | PID: %s", host, port, pid)
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
