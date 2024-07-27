from openmail import OpenMail
from fastapi import FastAPI, File, Form, UploadFile
from urllib.parse import unquote
import json
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List

class Response(BaseModel):
    success: bool
    message: str
    data: Optional[dict | list] = None

class SearchCriteria(BaseModel):
    senders: List[str]
    receivers: List[str]
    subject: str
    since: str
    before: str
    flags: List[str]
    include: str
    exclude: str
    has_attachments: bool

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

accounts = json.load(open("./accounts.json"))
EMAIL = accounts[0]["email"]
PASSWORD = accounts[0]["password"]

@app.post("/login") # TODO: This is temporary until the login system is implemented
def login(
    email = Form(...),
    password = Form(...)
) -> Response:
    print(email, password)
    success, message, data = OpenMail(EMAIL, PASSWORD).get_emails()
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
