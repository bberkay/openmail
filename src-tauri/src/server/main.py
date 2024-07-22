from openmail import OpenMail
from fastapi import FastAPI, Form
from urllib.parse import unquote
import json
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel
from typing import Optional, List

class Response(BaseModel):
    success: bool
    message: Optional[str] = ''
    data: Optional[dict | list] = {}

class SearchCriteria(BaseModel):
    from_: List[str]
    to: List[str]
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
def login(email = Form(...), password = Form(...)) -> Response:
    print(email, password)
    success, message, data = OpenMail(EMAIL, PASSWORD).get_emails()
    return {"success": success, "message": message, "data": data}

@app.get("/get-emails")
def get_emails(folder: str = 'INBOX', search: str = 'ALL', offset: str = '0') -> Response:
    folder = unquote(folder)
    search = unquote(search)
    success, message, data = OpenMail(EMAIL, PASSWORD).get_emails(folder, search, int(offset))
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

@app.get("/get-email-content/{folder}/{uid}")
def get_email_content(folder: str, uid: str) -> Response:
    folder = unquote(folder)
    success, message, data = OpenMail(EMAIL, PASSWORD).get_email_content(uid, folder)
    return {"success": success, "message": message, "data": data}

@app.post("/send-email")
def send_email(to: str = Form(...), subject: str = Form(...), body: str = Form(...), attachments: List[str] = []) -> Response:
    success, message = OpenMail(EMAIL, PASSWORD).send_email(to, subject, body, attachments)
    return {"success": success, "message": message}

@app.get("/get-folders")
def get_folders() -> Response:
    success, message, data = OpenMail(EMAIL, PASSWORD).get_folders()
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
