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

from internal.client_handler import ClientHandler
from internal.account_manager import AccountManager
from internal.file_system import FileSystem
from routers import app_tasks, account_tasks, email_tasks
from helpers.uvicorn_logger import UvicornLogger
from helpers.port_scanner import PortScanner

from .types import Response
from .consts import HOST, TRUSTED_HOSTS, PORT_RANGE
from .utils import parse_err_msg


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
app.include_router(app_tasks.router)
app.include_router(account_tasks.router)
app.include_router(email_tasks.router)


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
    port = PortScanner.find_free_port(PORT_RANGE[0], PORT_RANGE[1])
    pid = str(os.getpid())
    FileSystem().get_uvicorn_info().write(f"URL=http://{HOST}:{str(port)}\nPID={pid}\n")

    uvicorn_logger.info("Starting server at http://%s:%d | PID: %s", HOST, port, pid)
    uvicorn.run(app, host=HOST, port=port)


if __name__ == "__main__":
    main()
