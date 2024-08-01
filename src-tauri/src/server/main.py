import json, logging, sys, socket, os
from urllib.parse import unquote
from typing import Optional, List

import uvicorn
from pydantic import BaseModel
from openmail import OpenMail, SearchCriteria
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware

class Response(BaseModel):
    success: bool
    message: str
    data: Optional[dict | list] = None

logger = logging.getLogger("uvicorn")
logger.setLevel(logging.DEBUG)
log_dir = os.path.expanduser("~/.logs/openmail")
os.makedirs(log_dir, exist_ok=True)
stream_handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
logger.addHandler(logging.FileHandler(os.path.join(log_dir, 'uvicorn.log')))

try:
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    logger.info("FastAPI server started")
except Exception as e:
    logger.critical(f"Error starting FastAPI server: {e}")
    exit(1)

try:
    """
    Temporary solution to get the email and password from the accounts.json file.
    """
    accounts = json.load(open("./accounts.json"))
    EMAIL = accounts[0]["email"]
    PASSWORD = accounts[0]["password"]
except Exception as e:
    logger.critical(f"Error loading accounts: {e}")
    exit(1)

@app.middleware("http")
async def log_requests(request, call_next):
    response = await call_next(request)
    logger.info(f"{request.method} {request.url} - {response.status_code}")
    return response

@app.post("/login")
def login(
    email = Form(...),
    password = Form(...)
) -> Response:
     # TODO: This is temporary until the login system is implemented
    print(email, password)
    success, message, data = OpenMail(EMAIL, PASSWORD).get_emails()
    #success, message, data = OpenMail(email, password).get_emails()
    return {"success": success, "message": message, "data": data}

@app.get("/get-emails")
def get_emails(
    folder: str = 'INBOX',
    search: str = 'ALL',
    offset: str = '0'
) -> Response:
    folder = unquote(folder)
    search = unquote(search)
    success, message, data = OpenMail(EMAIL, PASSWORD).get_emails(folder, search, int(offset))
    return {"success": success, "message": message, "data": data}

@app.get("/get-email-content/{folder}/{uid}")
def get_email_content(
    folder: str,
    uid: str
) -> Response:
    folder = unquote(folder)
    success, message, data = OpenMail(EMAIL, PASSWORD).get_email_content(uid, folder)
    return {"success": success, "message": message, "data": data}

@app.post("/send-email")
async def send_email(
    sender_name: str = Form(...), # TODO: This is going to change to sender: Tuple[str, str]
    receivers: str = Form(...), # mail addresses separated by comma
    subject: str = Form(...),
    body: str = Form(...),
    attachments: List[UploadFile] = File(None)
) -> Response:
    success, message = OpenMail(EMAIL, PASSWORD).send_email(
        (sender_name, EMAIL) if sender_name else EMAIL,
        receivers,
        subject,
        body,
        attachments
    )
    return {"success": success, "message": message}

@app.get("/get-folders")
def get_folders() -> Response:
    success, message, data = OpenMail(EMAIL, PASSWORD).get_folders()
    return {"success": success, "message": message, "data": data}

class SearchRequest(BaseModel):
    folder: str
    search: SearchCriteria
    offset: int

@app.post("/search-emails")
def search_emails(search_request: SearchRequest) -> Response:
    success, message, data = OpenMail(EMAIL, PASSWORD).get_emails(
        search_request.folder,
        search_request.search,
        search_request.offset
    )
    return {"success": success, "message": message, "data": data}

class MarkEmailRequest(BaseModel):
    uid: str
    mark: str
    folder: str = 'INBOX'

@app.post("/mark-email")
async def mark_email(mark_email_request: MarkEmailRequest) -> Response:
    success, message = OpenMail(EMAIL, PASSWORD).mark_email(
        mark_email_request.uid,
        mark_email_request.mark,
        mark_email_request.folder
    )
    return {"success": success, "message": message}

class MarkEmailRequest(BaseModel):
    uid: str
    source: str
    destination: str

@app.post("/move-email")
async def move_email(move_email_request: MarkEmailRequest) -> Response:
    success, message = OpenMail(EMAIL, PASSWORD).move_email(
        move_email_request.uid,
        move_email_request.source,
        move_email_request.destination
    )
    return {"success": success, "message": message}

class DeleteEmailRequest(BaseModel):
    uid: str
    folder: str = 'INBOX'

@app.post("/delete-email")
async def delete_email(delete_email_request: DeleteEmailRequest) -> Response:
    success, message = OpenMail(EMAIL, PASSWORD).delete_email(
        delete_email_request.uid,
        delete_email_request.folder
    )
    return {"success": success, "message": message}

class CreateFolderRequest(BaseModel):
    folder_name: str
    parent_folder: str | None = None

@app.post("/create-folder")
async def create_folder(create_folder_request: CreateFolderRequest) -> Response:
    success, message = OpenMail(EMAIL, PASSWORD).create_folder(
        create_folder_request.folder_name,
        create_folder_request.parent_folder
    )
    return {"success": success, "message": message}

class RenameFolderRequest(BaseModel):
    folder_name: str
    new_name: str

@app.post("/rename-folder")
async def rename_folder(rename_folder_request: RenameFolderRequest) -> Response:
    success, message = OpenMail(EMAIL, PASSWORD).rename_folder(
        rename_folder_request.folder_name,
        rename_folder_request.new_name
    )
    return {"success": success, "message": message}

class DeleteFolderRequest(BaseModel):
    folder_name: str

@app.post("/delete-folder")
async def delete_folder(delete_folder_request: DeleteFolderRequest) -> Response:
    success, message = OpenMail(EMAIL, PASSWORD).delete_folder(delete_folder_request.folder_name)
    return {"success": success, "message": message}

class MoveFolderRequest(BaseModel):
    folder_name: str
    destination_folder: str

@app.post("/move-folder")
async def move_folder(move_folder_request: MoveFolderRequest) -> Response:
    success, message = OpenMail(EMAIL, PASSWORD).move_folder(
        move_folder_request.folder_name,
        move_folder_request.destination_folder
    )
    return {"success": success, "message": message}


def is_port_available(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) != 0

def find_free_port(start_port, end_port):
    for port in range(start_port, end_port + 1):
        if is_port_available(port):
            return port
    raise RuntimeError("No free ports available in the specified range")

if __name__ == "__main__":
    logger.info("Server started listening on port")
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=find_free_port(8000, 9000),
        reload=True,
        reload_excludes=['*.log']
    )
