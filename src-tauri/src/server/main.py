import json, logging, sys, socket, os
from urllib.parse import unquote
from typing import Optional, List
from logging.handlers import RotatingFileHandler

import uvicorn
from pydantic import BaseModel
from openmail import OpenMail, SearchCriteria
from openmail.utils import make_size_human_readable
from fastapi import FastAPI, File, Form, UploadFile, Request, Response as FastAPIResponse
from fastapi.middleware.cors import CORSMiddleware

class Response(BaseModel):
    success: bool
    message: str
    data: Optional[dict | list] = None

logger = logging.getLogger("server")
logger.setLevel(logging.DEBUG)
log_dir = os.path.expanduser("~/.openmail/logs")
os.makedirs(log_dir, exist_ok=True)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
stream_handler = logging.StreamHandler(sys.stdout)
file_handler = RotatingFileHandler(
    os.path.join(log_dir, 'server.log'),
    maxBytes=1*1024*1024, # 1 MB
    backupCount=5
)
stream_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
logger.addHandler(file_handler)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

"""
Temporary solution to get the email and password from the accounts.json file.
"""
accounts = json.load(open("./accounts.json"))
EMAIL = accounts[0]["email"]
PASSWORD = accounts[0]["password"]

TEMPORARY_REDIRECT = 307

def summarize_data(response_data: any) -> any:
    try:
        if isinstance(response_data, dict):
            return {key: summarize_data(value) for key, value in response_data.items()}
        elif isinstance(response_data, list):
            return [summarize_data(item) for item in response_data]
        elif isinstance(response_data, str) and len(response_data) >= 100:
            return response_data[:100] + "..."
        return response_data
    except Exception as e:
        logger.error(f"Error while summarizing data: {e}")
        return response_data

async def save_request_response_log(request: Request, response: FastAPIResponse):
    try:
        response_body = b""
        async for chunk in response.body_iterator:
            response_body += chunk

        response_data = {}
        if response_body:
            try:
                response_data = json.loads(response_body)
            except Exception as e:
                response_data = response_body.decode("utf-8")
                logger.error(f"Error while parsing response body: {e}")
        else:
            response_data = response.body.decode("utf-8")

        log_message = f"{request.method} {request.url} - {response.status_code} - {summarize_data(response_data)} - {make_size_human_readable(int(response.headers.get('content-length')))}"
        if response.status_code >= 400:
            logger.error(log_message)
        elif response.status_code != TEMPORARY_REDIRECT:
            logger.info(log_message)
    except Exception as e:
        logger.error(f"Error while logging request and response: {e}")
    finally:
        return response_body

@app.middleware("http")
async def log_requests(request: Request, call_next):
    response = await call_next(request)
    response_body = await save_request_response_log(request, response)
    return FastAPIResponse(content=response_body, status_code=response.status_code,
            headers=dict(response.headers), media_type=response.media_type)

def as_response(response: tuple) -> Response:
    if response[0]:
        return Response(success=response[0], message=response[1], data=response[2])
    return Response(success=response[0], message=response[1])

@app.post("/login")
def login(
    email = Form(...),
    password = Form(...)
) -> Response:
     # TODO: This is temporary until the login system is implemented
    print(email, password)
    #success, message, data = OpenMail(email, password).get_emails()
    return as_response(OpenMail(EMAIL, PASSWORD).get_emails())

@app.get("/get-emails")
def get_emails(
    folder: str = 'INBOX',
    search: str = 'ALL',
    offset: str = '0'
) -> Response:
    return as_response(OpenMail(EMAIL, PASSWORD).get_emails(
        unquote(folder),
        unquote(search),
        int(offset)
    ))

@app.get("/get-email-content/{folder}/{uid}")
def get_email_content(
    folder: str,
    uid: str
) -> Response:
    return as_response(OpenMail(EMAIL, PASSWORD).get_email_content(uid, unquote(folder)))

@app.post("/send-email")
async def send_email(
    sender_name: str = Form(...), # TODO: This is going to change to sender: Tuple[str, str]
    receivers: str = Form(...), # mail addresses separated by comma
    subject: str = Form(...),
    body: str = Form(...),
    attachments: List[UploadFile] = File(None)
) -> Response:
    return as_response(OpenMail(EMAIL, PASSWORD).send_email(
        (sender_name, EMAIL) if sender_name else EMAIL,
        receivers,
        subject,
        body,
        attachments
    ))


@app.get("/get-folders")
def get_folders() -> Response:
    return as_response((EMAIL, PASSWORD).get_folders())

class SearchRequest(BaseModel):
    folder: str
    search: SearchCriteria
    offset: int

@app.post("/search-emails")
def search_emails(search_request: SearchRequest) -> Response:
    return as_response(OpenMail(EMAIL, PASSWORD).get_emails(
        search_request.folder,
        search_request.search,
        search_request.offset
    ))

class MarkEmailRequest(BaseModel):
    uid: str
    mark: str
    folder: str = 'INBOX'

@app.post("/mark-email")
async def mark_email(mark_email_request: MarkEmailRequest) -> Response:
    return as_response(OpenMail(EMAIL, PASSWORD).mark_email(
        mark_email_request.uid,
        mark_email_request.mark,
        mark_email_request.folder
    ))

class MarkEmailRequest(BaseModel):
    uid: str
    source: str
    destination: str

@app.post("/move-email")
async def move_email(move_email_request: MarkEmailRequest) -> Response:
    return as_response(OpenMail(EMAIL, PASSWORD).move_email(
        move_email_request.uid,
        move_email_request.source,
        move_email_request.destination
    ))

class DeleteEmailRequest(BaseModel):
    uid: str
    folder: str = 'INBOX'

@app.post("/delete-email")
async def delete_email(delete_email_request: DeleteEmailRequest) -> Response:
    return as_response(OpenMail(EMAIL, PASSWORD).delete_email(
        delete_email_request.uid,
        delete_email_request.folder
    ))

class CreateFolderRequest(BaseModel):
    folder_name: str
    parent_folder: str | None = None

@app.post("/create-folder")
async def create_folder(create_folder_request: CreateFolderRequest) -> Response:
    return as_response(OpenMail(EMAIL, PASSWORD).create_folder(
        create_folder_request.folder_name,
        create_folder_request.parent_folder
    ))

class RenameFolderRequest(BaseModel):
    folder_name: str
    new_name: str

@app.post("/rename-folder")
async def rename_folder(rename_folder_request: RenameFolderRequest) -> Response:
    return as_response(OpenMail(EMAIL, PASSWORD).rename_folder(
        rename_folder_request.folder_name,
        rename_folder_request.new_name
    ))

class DeleteFolderRequest(BaseModel):
    folder_name: str

@app.post("/delete-folder")
async def delete_folder(delete_folder_request: DeleteFolderRequest) -> Response:
    return as_response(OpenMail(EMAIL, PASSWORD).delete_folder(delete_folder_request.folder_name))

class MoveFolderRequest(BaseModel):
    folder_name: str
    destination_folder: str

@app.post("/move-folder")
async def move_folder(move_folder_request: MoveFolderRequest) -> Response:
    return as_response(OpenMail(EMAIL, PASSWORD).move_folder(
        move_folder_request.folder_name,
        move_folder_request.destination_folder
    ))

def is_port_available(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) != 0

def find_free_port(start_port, end_port):
    for port in range(start_port, end_port + 1):
        if is_port_available(port):
            return port
    raise RuntimeError("No free ports available in the specified range")

#if __name__ == "__main__":
#    logger.info("Starting server...")
#    host = "127.0.0.1"
#    port = find_free_port(8000, 9000)
#    uvicorn.run(
#        app,
#        host=host,
#        port=find_free_port(8000, 9000)
#    )
#    logger.info(f"Server started at http://{host}:{port}")
