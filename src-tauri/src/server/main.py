import sys, os, re, concurrent.futures
from urllib.parse import unquote
from typing import Optional, List

import uvicorn, sqlcipher3
from pydantic import BaseModel
from fastapi import FastAPI, File, Form, UploadFile, Request, Response as FastAPIResponse
from fastapi.middleware.cors import CORSMiddleware

from openmail import OpenMail, SearchCriteria
from filesystem import FileSystem
from loghandler import LogHandler
from database import Database
from utils import is_email_valid, find_free_port, make_size_human_readable

APP_NAME = "OpenMail"
openmail_clients = {}
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger = LogHandler(APP_NAME)
file_system = FileSystem()
file_system.init()

@app.middleware("http")
async def catch_request_for_logging(request: Request, call_next):
    async def get_response_body(response: FastAPIResponse) -> bytes:
        response_body = b""
        async for chunk in response.body_iterator:
            response_body += chunk
            return response_body

    response = await call_next(request)
    response._body = await get_response_body(response)
    logger.request(request, response)
    return FastAPIResponse(
        content=response._body,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type=response.media_type
    )

def create_and_idle_openmail_clients():
    accounts = Database().get_accounts(None, ["email", "password"])
    if not accounts:
        return

    for account in accounts:
        openmail_clients[account["email"]] = OpenMail()
        status = openmail_clients[account["email"]].connect(account["email"], account["password"])
        print(f"Connected to {account['email']}")
        #if status:
        #    openmail_clients[account["email"]].idle()

def reconnect_and_idle_logged_out_openmail_clients():
    for email, openmail_client in openmail_clients.items():
        if not openmail_client.is_logged_in():
            account = Database().get_accounts([email], ["password"])
            if account:
                status = openmail_client.connect(email, account[0]["password"])
                print(f"Reconnected to {email}")
                #if status:
                #    openmail_client.idle()

@app.on_event("startup")
def startup_event():
    create_and_idle_openmail_clients()

class Response(BaseModel):
    success: bool
    message: str
    data: Optional[dict | list] = None

@app.get("/hello")
async def hello() -> Response:
    return Response(success=True, message="Hello, Server is ready for you!")

class AddEmailAccountRequest(BaseModel):
    email: str = Form(...)
    password: str = Form(...)
    fullname: Optional[str] = Form(None)

@app.post("/add-email-account")
def add_email_account(add_email_account_request: AddEmailAccountRequest) -> Response:
    if not is_email_valid(add_email_account_request.email):
        return Response(success=False, message="Invalid email address format")

    openmail_client = OpenMail()
    if not openmail_client.connect(
        add_email_account_request.email,
        add_email_account_request.password
    ):
        return Response(success=False, message="Invalid email credentials")

    success = Database().insert_account(
        add_email_account_request.email,
        add_email_account_request.password,
        add_email_account_request.fullname
    )
    if success:
        openmail_clients[add_email_account_request.email] = openmail_client
        return Response(
            success=success,
            message="Email added",
            data={
                "email": add_email_account_request.email,
                "fullname": add_email_account_request.fullname
            })
    return Response(
        success=success,
        message="Failed to add email"
    )

@app.get("/get-email-accounts")
def get_email_accounts() -> Response:
    try:
        return Response(
            success=True,
            message="Email accounts fetched successfully",
            data=Database().get_accounts(None, ["fullname", "email"])
        )
    except Exception as e:
        return Response(success=False, message=str(e))

def run_openmail_func_concurrently(accounts: list, func, **params) -> List[dict]:
    result = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_emails = {
            executor.submit(func, client, **params): email for email, client in openmail_clients.items() if email in accounts
        }

        for future in concurrent.futures.as_completed(future_to_emails):
            email = future_to_emails[future]
            future = future.result()
            result.append({"email": email, "data": future})
            print(f"Result for {email}: {future}")

    return result

@app.get("/get-emails/{accounts}")
async def get_emails(
    accounts: str,
    folder: Optional[str] = "INBOX",
    search: Optional[str] = "ALL",
    offset: Optional[int] = 0
) -> Response:
    try:
        return Response(
            success=True,
            message="Emails found",
            data=run_openmail_func_concurrently(
                accounts.split(","),
                lambda client, **params: client.get_emails(**params),
                folder=folder,
                search=search,
                offset=offset
            )
        )
    except Exception as e:
        return Response(success=False, message=str(e))

@app.get("/get-folders/{accounts}")
async def get_folders(
    accounts: str,
) -> Response:
    try:
        return Response(
            success=True,
            message="Folders found",
            data=run_openmail_func_concurrently(
                accounts.split(","),
                lambda client: client.get_folders(),
            )
        )
    except Exception as e:
        return Response(success=False, message=str(e))

@app.get("/get-email-content/{email}/{folder}/{uid}")
def get_email_content(
    email: str,
    folder: str,
    uid: str
) -> Response:
    try:
        if email not in openmail_clients:
            return Response(success=False, message="Email account not found")

        return Response(
            success=True,
            message="Email content fetched",
            data=openmail_clients[email].get_email_content(uid, unquote(folder))
        )
    except Exception as e:
        return Response(success=False, message=str(e))

@app.post("/send-email")
async def send_email(
    sender: str | tuple[str, str] = Form(...), # (sender_name, sender_email)
    receivers: str = Form(...), # mail addresses separated by comma
    subject: str = Form(...),
    body: str = Form(...),
    attachments: List[UploadFile] = File(None),
    cc: Optional[str] = Form(None),
    bcc: Optional[str] = Form(None)
) -> Response:
    try:
        return Response(
            success=True,
            message="Email sent",
            data=openmail_clients[(sender if isinstance(sender, str) else sender[1])].send_email(
                sender,
                receivers,
                subject,
                body,
                attachments,
                cc,
                bcc
            )
        )
    except Exception as e:
        return Response(success=False, message=str(e))

class MarkEmailRequest(BaseModel):
    email: str
    uid: str
    mark: str
    folder: str = 'INBOX'

@app.post("/mark-email")
async def mark_email(mark_email_request: MarkEmailRequest) -> Response:
    try:
        return Response(
            success=True,
            message="Email marked successfully",
            data=openmail_clients[mark_email_request.email].mark_email(
                mark_email_request.uid,
                mark_email_request.mark,
                mark_email_request.folder
            )
        )
    except Exception as e:
        return Response(success=False, message=str(e))

class MoveEmailRequest(BaseModel):
    email: str
    uid: str
    source: str
    destination: str

@app.post("/move-email")
async def move_email(move_email_request: MoveEmailRequest) -> Response:
    try:
        return Response(
            success=True,
            message="Email moved successfully",
            data=openmail_clients[move_email_request.email].move_email(
                move_email_request.uid,
                move_email_request.source,
                move_email_request.destination
            )
        )
    except Exception as e:
        return Response(success=False, message=str(e))

class CopyEmailRequest(BaseModel):
    email: str
    uid: str
    source: str
    destination: str

@app.post("/copy-email")
async def copy_email(copy_email_request: CopyEmailRequest) -> Response:
    try:
        return Response(
            success=True,
            message="Email moved successfully",
            data=openmail_clients[copy_email_request.email].copy_email(
                copy_email_request.uid,
                copy_email_request.source,
                copy_email_request.destination
            )
        )
    except Exception as e:
        return Response(success=False, message=str(e))

class DeleteEmailRequest(BaseModel):
    email: str
    uid: str
    folder: str

@app.post("/delete-email")
async def delete_email(delete_email_request: DeleteEmailRequest) -> Response:
    try:
        return Response(
            success=True,
            messages="Email deleted successfully",
            data=openmail_clients[delete_email_request.email].delete_email(
                delete_email_request.uid,
                delete_email_request.folder
            )
        )
    except Exception as e:
        return Response(success=False, message=str(e))

class CreateFolderRequest(BaseModel):
    email: str
    folder_name: str
    parent_folder: str | None = None

@app.post("/create-folder")
async def create_folder(create_folder_request: CreateFolderRequest) -> Response:
    try:
        return Response(
            success=True,
            message="Folder created successfully",
            data=openmail_clients[create_folder_request.email].create_folder(
                create_folder_request.folder_name,
                create_folder_request.parent_folder
            )
        )
    except Exception as e:
        return Response(success=False, message=str(e))

class RenameFolderRequest(BaseModel):
    email: str
    folder_name: str
    new_name: str

@app.post("/rename-folder")
async def rename_folder(rename_folder_request: RenameFolderRequest) -> Response:
    try:
        return Response(
            success=True,
            message="Folder renamed successfully",
            data=openmail_clients[rename_folder_request.email].rename_folder(
                rename_folder_request.folder_name,
                rename_folder_request.new_name
            )
        )
    except Exception as e:
        return Response(success=False, message=str(e))

class MoveFolderRequest(BaseModel):
    email: str
    folder_name: str
    destination_folder: str

@app.post("/move-folder")
async def move_folder(move_folder_request: MoveFolderRequest) -> Response:
    try:
        return Response(
            success=True,
            message="Folder moved successfully",
            data=openmail_clients[move_folder_request.email].move_folder(
                move_folder_request.folder_name,
                move_folder_request.destination_folder
            )
        )
    except Exception as e:
        return Response(success=False, message=str(e))

class DeleteFolderRequest(BaseModel):
    folder_name: str

@app.post("/delete-folder")
async def delete_folder(delete_folder_request: DeleteFolderRequest) -> Response:
    try:
        return Response(
            success=True,
            message="Folder deleted successfully",
            data=openmail_clients[delete_folder_request.email].delete_folder(
                delete_folder_request.folder_name
            )
        )
    except Exception as e:
        return Response(success=False, message=str(e))

if __name__ == "__main__":
    host = "127.0.0.1"
    port = find_free_port(8000, 9000)
    pid = str(os.getpid())
    file_system.create_uvicorn_info_file(host, str(port), pid)
    logger.info("Starting server at http://%s:%d | PID: %s", host, port, pid)
    uvicorn.run(
        app,
        host=host,
        port=port
    )
