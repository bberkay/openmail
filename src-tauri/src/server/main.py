import os, concurrent.futures
from urllib.parse import unquote
from typing import Optional, List
from contextlib import asynccontextmanager

import uvicorn
from pydantic import BaseModel
from fastapi import FastAPI, Form, UploadFile, Request, Response as FastAPIResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from openmail import OpenMail
from openmail.types import EmailToSend, Attachment
from openmail.imap import Folder, Mark

from classes.filesystem import FileSystem
from classes.loghandler import LogHandler
from classes.securestorage import SecureStorage
from classes.portmanager import PortManager
from utils import is_email_valid

openmail_clients: dict[str, OpenMail]  = {}
file_system = FileSystem()
secure_storage = SecureStorage()
logger = LogHandler()

def create_and_idle_openmail_clients():
    accounts = secure_storage.get_accounts(None, ["email", "password"])
    if not accounts:
        return

    for account in accounts:
        openmail_clients[account["email"]] = OpenMail()
        status, _ = openmail_clients[account["email"]].connect(account["email"], account["password"])
        print(f"Connected to {account['email']}")
        if status:
            openmail_clients[account["email"]].imap.idle()

def reconnect_and_idle_logged_out_openmail_clients():
    for email, openmail_client in openmail_clients.items():
        if not openmail_client.is_logged_in():
            account = secure_storage.get_accounts([email], ["password"])
            if account:
                status = openmail_client.connect(email, account[0]["password"])
                print(f"Reconnected to {email}")
                if status:
                    openmail_client.imap.dle()

def shutdown_openmail_clients():
    for openmail_client in openmail_clients.values():
        openmail_client.disconnect()

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_and_idle_openmail_clients()
    yield
    shutdown_openmail_clients()

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["*"]
)

@app.middleware("http")
async def catch_request_for_logging(request: Request, call_next):
    async def get_response_body(response: FastAPIResponse) -> bytes:
        response_body = b""
        async for chunk in response.body_iterator:
            response_body += chunk
            return response_body

    response = await call_next(request)
    print("Response: ", response)
    response._body = await get_response_body(response)
    print("Response Body: ", response._body)
    logger.request(request, response)
    return FastAPIResponse(
        content=response._body,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type=response.media_type
    )

class Response(BaseModel):
    success: bool
    message: str
    data: Optional[dict | list] = None

@app.get("/hello")
async def hello() -> Response:
    return Response(success=True, message="Hello, Server is ready for you!")

@app.post("/add-email-account")
def add_email_account(
    email = Form(...),
    password = Form(...),
    fullname = Form(None)
) -> Response:
    if not is_email_valid(email):
        return Response(success=False, message="Invalid email address format")

    try:
        openmail_client = OpenMail()
        status, msg = openmail_client.connect(email, password)
        if not status:
            return Response(success=status, message=msg)
    
        secure_storage.insert_account(email, password, fullname)
        openmail_clients[email] = openmail_client
        return Response(
            success=True,
            message="Email added",
            data={
                "email": email,
                "fullname": fullname
            }
        )
    except Exception as e:
        return Response(
            success=False,
            message="Failed to add email: " + str(e)
        )

@app.get("/get-email-accounts")
def get_email_accounts() -> Response:
    try:
        return Response(
            success=True,
            message="Email accounts fetched successfully",
            data=secure_storage.get_accounts(None, ["fullname", "email"])
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

def check_email_accounts(accounts: str) -> Response | bool:
    accounts = accounts.split(",")

    for account in accounts:
        if account not in openmail_clients:
            return Response(success=False, message=f"Email account: {account} could not be found.")
        
    return True

@app.get("/get-emails/{accounts}")
async def get_emails(
    accounts: str,
    folder: Optional[str] = Folder.Inbox,
    search: Optional[str] = "ALL",
    offset_start: Optional[int] = 0,
    offset_end: Optional[int] = 10
) -> Response:
    try:
        response = check_email_accounts(accounts)
        if not response:
            return response
        
        run_openmail_func_concurrently(
            accounts.split(","),
            lambda client, **params: client.search_emails(**params),
            folder=folder,
            search=search
        )

        return Response(
            success=True, 
            message="Emails fetched successfully.",
            data=run_openmail_func_concurrently(
                accounts.split(","),
                lambda client, **params: client.get_emails(**params),
                offset_start=offset_start,
                offset_end=offset_end
            )
        )
    except Exception as e:
        return Response(success=False, message=str(e))

@app.get("/paginate-emails/{accounts}")
async def paginate_emails(
    accounts: str,
    offset_start: Optional[int] = 0,
    offset_end: Optional[int] = 10,
) -> Response:
    try:
        response = check_email_accounts(accounts)
        if not response:
            return response
        
        return Response(
            success=True, 
            message="Emails paginated successfully.",
            data=run_openmail_func_concurrently(
                accounts.split(","),
                lambda client, **params: client.get_emails(**params),
                offset_start=offset_start,
                offset_end=offset_end
            )
        )
    except Exception as e:
        return Response(success=False, message=str(e))

@app.get("/get-folders/{accounts}")
async def get_folders(
    accounts: str,
) -> Response:
    try:
        response = check_email_accounts(accounts)
        if not response:
            return response
        
        return Response(
            success=True, 
            message="Folders fetched successfully.",
            data=run_openmail_func_concurrently(
                accounts.split(","),
                lambda client: client.get_folders(),
            )
        )
    except Exception as e:
        return Response(success=False, message=str(e))

@app.get("/get-email-content/{account}/{folder}/{uid}")
def get_email_content(
    account: str,
    folder: str,
    uid: str
) -> Response:
    try:
        response = check_email_accounts(account)
        if not response:
            return response
        
        return Response(
            success=True,
            message="Email content fetched successfully.",
            data=openmail_clients[account].imap.get_email_content(uid, unquote(folder))
        )
    except Exception as e:
        return Response(success=False, message=str(e))

class SendEmailRequestFormData(BaseModel):
    sender: str | tuple[str, str] # (sender_name, sender_email)
    receiver: str # mail addresses separated by comma
    subject: str
    body: str
    uid: Optional[str] = None
    cc: Optional[str] = None
    bcc: Optional[str] = None
    attachments: List[UploadFile] = []

async def convert_attachments(attachments: List[UploadFile]) -> List[Attachment]:
    converted_to_attachment_list = []
    for attachment in attachments:
        data = await attachment.read()
        converted_to_attachment_list.append(Attachment(
            name=attachment.filename,
            data=data,
            type=attachment.content_type,
            size=len(data)
        ))
    return converted_to_attachment_list

@app.post("/send-email")
async def send_email(
    formData: SendEmailRequestFormData
) -> Response:
    try:
        response = check_email_accounts(formData.sender)
        if not response:
            return response
        
        sender_email = formData.sender if isinstance(formData.sender, str) else formData.sender[1]
        status, msg = openmail_clients[sender_email].smtp.send_email(
            EmailToSend(
                sender=formData.sender,
                receiver=formData.receiver,
                subject=formData.subject,
                body=formData.body,
                cc=formData.cc,
                bcc=formData.bcc,
                attachments=await convert_attachments(formData.attachments)
            )
        )

        try:
            if status:
                flags = openmail_clients[sender_email].imap.get_email_flags(formData.uid, Folder.Inbox).flags
                if Mark.SEEN not in flags:
                    status, com_msg = openmail_clients[sender_email].imap.mark_email(formData.uid, Mark.SEEN)
                    msg += " " + f"And {com_msg}"
        except Exception as e:
            msg += " " + "And failed to mark email as seen: " + str(e)
        
        return Response(success=status, message=msg)
    except Exception as e:
        return Response(success=False, message=str(e))

@app.post("/reply-email")
async def reply_email(
    formData: SendEmailRequestFormData
) -> Response:
    try:
        response = check_email_accounts(formData.sender)
        if not response:
            return response
        
        sender_email = formData.sender if isinstance(formData.sender, str) else formData.sender[1]
        status, msg = openmail_clients[sender_email].smtp.send_email(
            EmailToSend(
                sender=formData.sender,
                receiver=formData.receiver,
                subject=formData.subject,
                body=formData.body,
                cc=formData.cc,
                bcc=formData.bcc,
                attachments=await convert_attachments(formData.attachments)
            )
        )

        try:
            if status:
                flags = openmail_clients[sender_email].imap.get_email_flags(formData.uid, Folder.Inbox).flags
                if Mark.ANSWERED not in flags:
                    status, com_msg = openmail_clients[sender_email].imap.mark_email(formData.uid, Mark.ANSWERED)
                    msg += " " + f"And {com_msg}"
                if Mark.SEEN not in flags:
                    status, com_msg = openmail_clients[sender_email].imap.mark_email(formData.uid, Mark.SEEN)
                    msg += " " + f"And {com_msg}"
        except Exception as e:
            msg += " " + "And failed to mark email as answered or seen: " + str(e)

        return Response(success=status, message=msg)
    except Exception as e:
        return Response(success=False, message=str(e))
    
@app.post("/forward-email")
async def forward_email(
    formData: SendEmailRequestFormData
) -> Response:
    try:
        response = check_email_accounts(formData.sender)
        if not response:
            return response
        
        sender_email = formData.sender if isinstance(formData.sender, str) else formData.sender[1]
        status, msg = openmail_clients[sender_email].smtp.send_email(
            EmailToSend(
                sender=formData.sender,
                receiver=formData.receiver,
                subject=formData.subject,
                body=formData.body,
                cc=formData.cc,
                bcc=formData.bcc,
                attachments=await convert_attachments(formData.attachments)
            )
        )

        try:
            if status:
                flags = openmail_clients[sender_email].imap.get_email_flags(formData.uid, Folder.Inbox).flags
                if Mark.ANSWERED not in flags:
                    status, com_msg = openmail_clients[sender_email].imap.mark_email(formData.uid, Mark.ANSWERED)
                    msg += " " + f"And {com_msg}"
                if Mark.SEEN not in flags:
                    status, com_msg = openmail_clients[sender_email].imap.mark_email(formData.uid, Mark.SEEN)
                    msg += " " + f"And {com_msg}"
        except Exception as e:
            msg += " " + "And failed to mark email as answered or seen: " + str(e)

        return Response(success=status, message=msg)
    except Exception as e:
        return Response(success=False, message=str(e))
    
class MarkEmailRequest(BaseModel):
    account: str
    mark: str
    sequence_set: str
    folder: str = Folder.Inbox
    
@app.post("/mark-email")
async def mark_email(mark_email_request: MarkEmailRequest) -> Response:
    try:
        response = check_email_accounts(mark_email_request.account)
        if not response:
            return response
        
        status, msg = openmail_clients[mark_email_request.account].imap.mark_email(
            mark_email_request.mark,
            mark_email_request.sequence_set,
            mark_email_request.folder,
        )
        return Response(success=status, message=msg)
    except Exception as e:
        return Response(success=False, message=str(e))

class UnmarkEmailRequest(BaseModel):
    account: str
    mark: str
    sequence_set: str
    folder: str = Folder.Inbox
    
@app.post("/unmark-email")
async def unmark_email(unmark_email_request: UnmarkEmailRequest) -> Response:
    try:
        response = check_email_accounts(unmark_email_request.account)
        if not response:
            return response
        
        status, msg = openmail_clients[unmark_email_request.account].imap.unmark_email(
            unmark_email_request.mark, 
            unmark_email_request.sequence_set,
            unmark_email_request.folder,
        )
        return Response(success=status, message=msg)
    except Exception as e:
        return Response(success=False, message=str(e))
    
class MoveEmailRequest(BaseModel):
    account: str
    source_folder: str
    destination_folder: str
    sequence_set: str

@app.post("/move-email")
async def move_email(move_email_request: MoveEmailRequest) -> Response:
    try:
        response = check_email_accounts(move_email_request.account)
        if not response:
            return response
        
        status, msg = openmail_clients[move_email_request.account].imap.move_email(
            move_email_request.source_folder,
            move_email_request.destination_folder,
            move_email_request.sequence_set
        )
        return Response(success=status, message=msg)
    except Exception as e:
        return Response(success=False, message=str(e))

class CopyEmailRequest(BaseModel):
    account: str
    source_folder: str
    destination_folder: str
    sequence_set: str

@app.post("/copy-email")
async def copy_email(copy_email_request: CopyEmailRequest) -> Response:
    try:
        response = check_email_accounts(copy_email_request.account)
        if not response:
            return response
        
        status, msg = openmail_clients[copy_email_request.account].imap.copy_email(
            copy_email_request.source_folder,
            copy_email_request.destination_folder,
            copy_email_request.sequence_set
        )
        return Response(success=status, message=msg)
    except Exception as e:
        return Response(success=False, message=str(e))

class DeleteEmailRequest(BaseModel):
    account: str
    folder: str
    sequence_set: str

@app.post("/delete-email")
async def delete_email(delete_email_request: DeleteEmailRequest) -> Response:
    try:
        response = check_email_accounts(delete_email_request.account)
        if not response:
            return response
        
        status, msg = openmail_clients[delete_email_request.account].imap.delete_email(
            delete_email_request.folder, 
            delete_email_request.sequence_set
        )
        return Response(success=status, message=msg)
    except Exception as e:
        return Response(success=False, message=str(e))

class CreateFolderRequest(BaseModel):
    account: str
    folder_name: str
    parent_folder: str | None = None

@app.post("/create-folder")
async def create_folder(create_folder_request: CreateFolderRequest) -> Response:
    try:
        response = check_email_accounts(create_folder_request.account)
        if not response:
            return response
        
        status, msg = openmail_clients[create_folder_request.account].imap.create_folder(
            create_folder_request.folder_name, 
            create_folder_request.parent_folder
        )
        return Response(success=status, message=msg)
    except Exception as e:
        return Response(success=False, message=str(e))

class RenameFolderRequest(BaseModel):
    account: str
    folder_name: str
    new_folder_name: str

@app.post("/rename-folder")
async def rename_folder(rename_folder_request: RenameFolderRequest) -> Response:
    try:
        response = check_email_accounts(rename_folder_request.account)
        if not response:
            return response
        
        status, msg = openmail_clients[rename_folder_request.account].imap.rename_folder(
            rename_folder_request.folder_name, 
            rename_folder_request.new_folder_name
        )
        return Response(success=status, message=msg)
    except Exception as e:
        return Response(success=False, message=str(e))

class MoveFolderRequest(BaseModel):
    account: str
    folder_name: str
    destination_folder: str

@app.post("/move-folder")
async def move_folder(move_folder_request: MoveFolderRequest) -> Response:
    try:
        response = check_email_accounts(move_folder_request.account)
        if not response:
            return response
        
        status, msg = openmail_clients[move_folder_request.account].imap.move_folder(
            move_folder_request.folder_name,
            move_folder_request.destination_folder
        )
        return Response(success=status, message=msg)
    except Exception as e:
        return Response(success=False, message=str(e))

class DeleteFolderRequest(BaseModel):
    account: str
    folder_name: str

@app.post("/delete-folder")
async def delete_folder(delete_folder_request: DeleteFolderRequest) -> Response:
    try:
        response = check_email_accounts(delete_folder_request.account)
        if not response:
            return response
        
        status, msg = openmail_clients[delete_folder_request.account].imap.delete_folder(
            delete_folder_request.folder_name
        )
        return Response(success=status, message=msg)
    except Exception as e:
        return Response(success=False, message=str(e))

def main():
    file_system.init()
    secure_storage.init()
    logger.init()

    host = "127.0.0.1"
    port = PortManager.find_free_port(8000, 9000)
    pid = str(os.getpid())
    file_system.create_uvicorn_info_file(host, str(port), pid)

    logger.info("Starting server at http://%s:%d | PID: %s", host, port, pid)
    uvicorn.run(
        app,
        host=host,
        port=port
    )

if __name__ == "__main__":
    main()
