"""
This module contains the main FastAPI application and its routes.
TODO: improve docstring
"""

from __future__ import annotations
import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request, Response as FastAPIResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from src.internal.client_handler import ClientHandler
from src.internal.account_manager import AccountManager
from src.internal.file_system import FileObject, Root
from src.routers import account_tasks, mailbox_tasks
from src.helpers.uvicorn_logger import UvicornLogger
from src.helpers.port_scanner import PortScanner

from src._types import Response
from src.consts import HOST, TRUSTED_HOSTS, PORT_RANGE
from src.utils import parse_err_msg


#################### SET UP #######################

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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=TRUSTED_HOSTS)
app.include_router(account_tasks.router)
app.include_router(mailbox_tasks.router)


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
    host = str(input(f"Give an HOST to app run on (e.g. {HOST}): ") or HOST)

    while True:
        try:
            port_start_range = int(input(f"Port start range (e.g. {PORT_RANGE[0]}): ") or PORT_RANGE[0])
            port_end_range = int(input(f"Port end range (e.g. {PORT_RANGE[1]}): ") or PORT_RANGE[1])
            print(f"Finding free port between {port_start_range}-{port_end_range}")
            port = PortScanner.find_free_port(host, port_start_range, port_end_range)
            break
        except RuntimeError:
            pass

    pid = str(os.getpid())
    etc = Root("etc")
    uvicorn_info = FileObject("uvicorn.info")
    etc.append(uvicorn_info)
    uvicorn_info.write(f"URL=http://{host}:{str(port)}\nPID={pid}\n")

    uvicorn_logger.info("Starting server at http://%s:%d | PID: %s", host, port, pid)
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
