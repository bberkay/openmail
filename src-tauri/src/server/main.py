"""
This module contains the main FastAPI application and its routes.
TODO: improve docstring
"""

import json
import os
import concurrent.futures
from urllib.parse import unquote
from typing import Annotated, Optional
from contextlib import asynccontextmanager

import uvicorn
from pydantic import BaseModel
from fastapi import FastAPI, Form, UploadFile, Request, Response as FastAPIResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from openmail import OpenMail
from openmail.types import EmailToSend, Attachment
from openmail.imap import Folder, Mark

from classes.file_system import FileSystem
from classes.http_request_logger import HTTPRequestLogger
from classes.secure_storage import SecureStorage, Account, AccountColumn
from classes.port_manager import PortManager

from consts import TRUSTED_HOSTS
from utils import is_email_valid, err_msg, parse_err_msg

#################### SET UP #######################

openmail_clients: dict[str, OpenMail] = {}
secure_storage = SecureStorage()
http_request_logger = HTTPRequestLogger()


def create_and_idle_openmail_clients():
    accounts: list[Account] = secure_storage.get_accounts(
        None, [AccountColumn.EMAIL_ADDRESS, AccountColumn.PASSWORD]
    )
    if not accounts:
        return

    for account in accounts:
        openmail_clients[account["email_address"]] = OpenMail()
        status, _ = openmail_clients[account["email_address"]].connect(
            account["email_address"], account["password"]
        )
        print(f"Connected to {account['email_address']}")
        """if status:
            openmail_clients[account["email_address"]].imap.idle()"""


def reconnect_and_idle_logged_out_openmail_clients():
    for email_address, openmail_client in openmail_clients.items():
        if not openmail_client.is_logged_in():
            account: Account = secure_storage.get_accounts(
                [email_address], AccountColumn.PASSWORD
            )
            if account:
                status = openmail_client.connect(email_address, account[0]["password"])
                print(f"Reconnected to {email_address}")
                if status:
                    openmail_client.imap.idle()


def shutdown_openmail_clients():
    try:
        for email, openmail_client in openmail_clients.items():
            openmail_client.disconnect()
    except:
        pass


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
app.add_middleware(TrustedHostMiddleware, allowed_hosts=TRUSTED_HOSTS)


class Response(BaseModel):
    success: bool
    message: str
    data: dict | list | None = None


@app.middleware("http")
async def catch_request_for_logging(request: Request, call_next):
    async def get_response_body(response: FastAPIResponse) -> bytes:
        response_body = b""
        async for chunk in response.body_iterator:
            response_body += chunk
            return response_body

    response = await call_next(request)
    response._body = await get_response_body(response)
    print("Response Body: ", response._body)
    http_request_logger.request(request, response)
    return FastAPIResponse(
        content=parse_err_msg(response._body)[0],
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type=response.media_type,
    )

@app.get("/hello")
async def hello() -> Response:
    return Response(success=True, message="Hello, Server is ready for you!")

#################################################


################ FOR TESTS ONLY #################

@app.post("/refresh-whole-universe")
def refresh_whole_universe() -> Response:
    try:
        FileSystem().reset()
        secure_storage.delete_accounts()
        return Response(success=True, message="You asked and the whole universe completely refreshed!")
    except Exception as e:
        return Response(success=False, message=err_msg("Some forces prevented you from doing this.", str(e)))


@app.post("/reset-file-system")
def reset_file_system() -> Response:
    try:
        FileSystem().reset()
        return Response(success=True, message="Files are recreated successfully")
    except Exception as e:
        return Response(success=False, message=err_msg("There was an error while recreating files.", str(e)))

#####################################################


################ ACCOUNT OPERATIONS #################

class AddEmailAccountFormData(BaseModel):
    email_address: str
    password: str
    fullname: Optional[str] = None


@app.post("/add-email-account")
def add_email_account(
    form_data: Annotated[AddEmailAccountFormData, Form()]
) -> Response:
    if not is_email_valid(form_data.email_address):
        return Response(success=False, message="Invalid email address format")

    try:
        openmail_client = OpenMail()
        status, msg = openmail_client.connect(
            form_data.email_address,
            form_data.password
        )

        if not status:
            return Response(success=status, message=err_msg("Failed to add email.", msg))

        secure_storage.insert_account(Account(
            email_address=form_data.email_address,
            password=form_data.password,
            fullname=form_data.fullname
        ))

        openmail_clients[form_data.email_address] = openmail_client
        return Response(
            success=True,
            message="Email added"
        )
    except Exception as e:
        return Response(success=False, message=err_msg("Failed to add email.", str(e)))


@app.get("/get-email-accounts")
def get_email_accounts() -> Response:
    try:
        return Response(
            success=True,
            message="Email accounts fetched successfully",
            data=secure_storage.get_accounts(
                None, [AccountColumn.FULLNAME, AccountColumn.EMAIL_ADDRESS]
            ),
        )
    except Exception as e:
        return Response(success=False, message=err_msg("Failed to fetch email accounts.", str(e)))


class DeleteEmailAccountRequest(BaseModel):
    account: str


@app.post("/delete-email-account")
def delete_email_account(request_body: DeleteEmailAccountRequest) -> Response:
    try:
        secure_storage.delete_account(request_body.account)
        return Response(success=True, message="Account deleted successfully")
    except Exception as e:
        return Response(success=False, message=err_msg("There was an error while deleting account.", str(e)))


@app.post("/delete-email-accounts")
def delete_email_accounts() -> Response:
    try:
        secure_storage.delete_accounts()
        return Response(success=True, message="Accounts deleted successfully")
    except Exception as e:
        return Response(success=False, message=err_msg("There was an error while deleting accounts.", str(e)))

#####################################################


################ EMAIL OPERATIONS ###################

def run_openmail_func_concurrently(accounts: list, func, **params) -> list[dict]:
    result = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_emails = {
            executor.submit(func, client, **params): email_address
            for email_address, client in openmail_clients.items()
            if email_address in accounts
        }

        for future in concurrent.futures.as_completed(future_to_emails):
            email_address = future_to_emails[future]
            future = future.result()
            result.append({"email_address": email_address, "data": future})
            print(f"Result for {email_address}: {future}")

    return result

def check_if_email_accounts_are_connected(accounts: str) -> Response | bool:
    accounts = accounts.split(",")

    for account in accounts:
        if account not in openmail_clients:
            return Response(
                success=False, message=f"Email account: {account} is not connected"
            )

    return True


@app.get("/get-emails/{accounts}")
async def get_emails(
    accounts: str,
    folder: Optional[str] = Folder.Inbox,
    search: Optional[str] = "ALL",
    offset_start: Optional[int] = 0,
    offset_end: Optional[int] = 10,
) -> Response:
    try:
        response = check_if_email_accounts_are_connected(accounts)
        if not response:
            return response

        run_openmail_func_concurrently(
            accounts.split(","),
            lambda client, **params: client.search_emails(**params),
            folder=folder,
            search=search,
        )

        return Response(
            success=True,
            message="Emails fetched successfully.",
            data=run_openmail_func_concurrently(
                accounts.split(","),
                lambda client, **params: client.get_emails(**params),
                offset_start=offset_start,
                offset_end=offset_end,
            ),
        )
    except Exception as e:
        return Response(success=False, message=err_msg("There was an error while fetching emails.", str(e)))


@app.get("/paginate-emails/{accounts}")
async def paginate_emails(
    accounts: str,
    offset_start: Optional[int] = 0,
    offset_end: Optional[int] = 10,
) -> Response:
    try:
        response = check_if_email_accounts_are_connected(accounts)
        if not response:
            return response

        return Response(
            success=True,
            message="Emails paginated successfully.",
            data=run_openmail_func_concurrently(
                accounts.split(","),
                lambda client, **params: client.get_emails(**params),
                offset_start=offset_start,
                offset_end=offset_end,
            ),
        )
    except Exception as e:
        return Response(success=False, message=err_msg("There was an error while paginating emails.", str(e)))


@app.get("/get-folders/{accounts}")
async def get_folders(
    accounts: str,
) -> Response:
    try:
        response = check_if_email_accounts_are_connected(accounts)
        if not response:
            return response

        return Response(
            success=True,
            message="Folders fetched successfully.",
            data=run_openmail_func_concurrently(
                accounts.split(","),
                lambda client: client.get_folders(),
            ),
        )
    except Exception as e:
        return Response(success=False, message=err_msg("There was an error while fetching folders.", str(e)))


@app.get("/get-email-content/{account}/{folder}/{uid}")
def get_email_content(account: str, folder: str, uid: str) -> Response:
    try:
        response = check_if_email_accounts_are_connected(account)
        if not response:
            return response

        return Response(
            success=True,
            message="Email content fetched successfully.",
            data=openmail_clients[account].imap.get_email_content(uid, unquote(folder)),
        )
    except Exception as e:
        return Response(success=False, message=err_msg("There was an error while fetching email content.", str(e)))


class SendEmailFormData(BaseModel):
    sender: str | tuple[str, str]  # (sender_name, sender_email)
    receiver: str  # mail addresses separated by comma
    subject: str
    body: str
    uid: Optional[str] = None
    cc: Optional[str] = None
    bcc: Optional[str] = None
    attachments: list[UploadFile] = []


async def convert_attachments(attachments: list[UploadFile]) -> list[Attachment]:
    converted_to_attachment_list = []
    for attachment in attachments:
        data = await attachment.read()
        converted_to_attachment_list.append(
            Attachment(
                name=attachment.filename,
                data=data,
                type=attachment.content_type,
                size=len(data),
            )
        )
    return converted_to_attachment_list


@app.post("/send-email")
async def send_email(
    formData: Annotated[SendEmailFormData, Form()]
) -> Response:
    try:
        response = check_if_email_accounts_are_connected(formData.sender)
        if not response:
            return response

        sender_email = (
            formData.sender if isinstance(formData.sender, str) else formData.sender[1]
        )
        status, msg = openmail_clients[sender_email].smtp.send_email(
            EmailToSend(
                sender=formData.sender,
                receiver=formData.receiver,
                subject=formData.subject,
                body=formData.body,
                cc=formData.cc,
                bcc=formData.bcc,
                attachments=await convert_attachments(formData.attachments),
            )
        )

        try:
            if status:
                flags = (
                    openmail_clients[sender_email]
                    .imap.get_email_flags(formData.uid, Folder.Inbox)
                    .flags
                )
                if Mark.SEEN not in flags:
                    status, com_msg = openmail_clients[sender_email].imap.mark_email(
                        formData.uid, Mark.SEEN
                    )
                    msg += " " + f"And {com_msg}"
        except Exception as e:
            msg = err_msg(msg + " " + "And failed to mark email as seen.", str(e))

        return Response(success=status, message=msg)
    except Exception as e:
        return Response(success=False, message=err_msg("There was an error while sending email.", str(e)))


@app.post("/reply-email")
async def reply_email(
    formData: Annotated[SendEmailFormData, Form()]
) -> Response:
    try:
        response = check_if_email_accounts_are_connected(formData.sender)
        if not response:
            return response

        sender_email = (
            formData.sender if isinstance(formData.sender, str) else formData.sender[1]
        )
        status, msg = openmail_clients[sender_email].smtp.send_email(
            EmailToSend(
                sender=formData.sender,
                receiver=formData.receiver,
                subject=formData.subject,
                body=formData.body,
                cc=formData.cc,
                bcc=formData.bcc,
                attachments=await convert_attachments(formData.attachments),
            )
        )

        try:
            if status:
                flags = (
                    openmail_clients[sender_email]
                    .imap.get_email_flags(formData.uid, Folder.Inbox)
                    .flags
                )
                if Mark.ANSWERED not in flags:
                    status, com_msg = openmail_clients[sender_email].imap.mark_email(
                        formData.uid, Mark.ANSWERED
                    )
                    msg += " " + f"And {com_msg}"
                if Mark.SEEN not in flags:
                    status, com_msg = openmail_clients[sender_email].imap.mark_email(
                        formData.uid, Mark.SEEN
                    )
                    msg += " " + f"And {com_msg}"
        except Exception as e:
            msg = err_msg(msg + " " + "And failed to mark email as answered or seen.", str(e))

        return Response(success=status, message=msg)
    except Exception as e:
        return Response(success=False, message=err_msg("There was an error while replying email.", str(e)))


@app.post("/forward-email")
async def forward_email(
    formData: Annotated[SendEmailFormData, Form()]
) -> Response:
    try:
        response = check_if_email_accounts_are_connected(formData.sender)
        if not response:
            return response

        sender_email = (
            formData.sender if isinstance(formData.sender, str) else formData.sender[1]
        )
        status, msg = openmail_clients[sender_email].smtp.send_email(
            EmailToSend(
                sender=formData.sender,
                receiver=formData.receiver,
                subject=formData.subject,
                body=formData.body,
                cc=formData.cc,
                bcc=formData.bcc,
                attachments=await convert_attachments(formData.attachments),
            )
        )

        try:
            if status:
                flags = (
                    openmail_clients[sender_email]
                    .imap.get_email_flags(formData.uid, Folder.Inbox)
                    .flags
                )
                if Mark.ANSWERED not in flags:
                    status, com_msg = openmail_clients[sender_email].imap.mark_email(
                        formData.uid, Mark.ANSWERED
                    )
                    msg += " " + f"And {com_msg}"
                if Mark.SEEN not in flags:
                    status, com_msg = openmail_clients[sender_email].imap.mark_email(
                        formData.uid, Mark.SEEN
                    )
                    msg += " " + f"And {com_msg}"
        except Exception as e:
            msg = err_msg(msg + " " + "And failed to mark email as answered or seen.", str(e))

        return Response(success=status, message=msg)
    except Exception as e:
        return Response(success=False, message=err_msg("There was an error while forwarding email.", str(e)))


class MarkEmailRequest(BaseModel):
    account: str
    mark: str
    sequence_set: str
    folder: str = Folder.Inbox


@app.post("/mark-email")
async def mark_email(request_body: MarkEmailRequest) -> Response:
    try:
        response = check_if_email_accounts_are_connected(request_body.account)
        if not response:
            return response

        status, msg = openmail_clients[request_body.account].imap.mark_email(
            request_body.mark,
            request_body.sequence_set,
            request_body.folder,
        )
        return Response(success=status, message=msg)
    except Exception as e:
        return Response(success=False, message=err_msg("There was an error while marking email.", str(e)))


class UnmarkEmailRequest(BaseModel):
    account: str
    mark: str
    sequence_set: str
    folder: str = Folder.Inbox


@app.post("/unmark-email")
async def unmark_email(request_body: UnmarkEmailRequest) -> Response:
    try:
        response = check_if_email_accounts_are_connected(request_body.account)
        if not response:
            return response

        status, msg = openmail_clients[request_body.account].imap.unmark_email(
            request_body.mark,
            request_body.sequence_set,
            request_body.folder,
        )
        return Response(success=status, message=msg)
    except Exception as e:
        return Response(success=False, message=err_msg("There was an error while unmarking email.", str(e)))


class MoveEmailRequest(BaseModel):
    account: str
    source_folder: str
    destination_folder: str
    sequence_set: str


@app.post("/move-email")
async def move_email(request_body: MoveEmailRequest) -> Response:
    try:
        response = check_if_email_accounts_are_connected(request_body.account)
        if not response:
            return response

        status, msg = openmail_clients[request_body.account].imap.move_email(
            request_body.source_folder,
            request_body.destination_folder,
            request_body.sequence_set,
        )
        return Response(success=status, message=msg)
    except Exception as e:
        return Response(success=False, message=err_msg("There was an error while moving email.", str(e)))


class CopyEmailRequest(BaseModel):
    account: str
    source_folder: str
    destination_folder: str
    sequence_set: str


@app.post("/copy-email")
async def copy_email(request_body: CopyEmailRequest) -> Response:
    try:
        response = check_if_email_accounts_are_connected(request_body.account)
        if not response:
            return response

        status, msg = openmail_clients[request_body.account].imap.copy_email(
            request_body.source_folder,
            request_body.destination_folder,
            request_body.sequence_set,
        )
        return Response(success=status, message=msg)
    except Exception as e:
        return Response(success=False, message=err_msg("There was an error while copying email.", str(e)))


class DeleteEmailRequest(BaseModel):
    account: str
    folder: str
    sequence_set: str


@app.post("/delete-email")
async def delete_email(request_body: DeleteEmailRequest) -> Response:
    try:
        response = check_if_email_accounts_are_connected(request_body.account)
        if not response:
            return response

        status, msg = openmail_clients[request_body.account].imap.delete_email(
            request_body.folder, request_body.sequence_set
        )
        return Response(success=status, message=msg)
    except Exception as e:
        return Response(success=False, message=err_msg("There was an error while deleting email.", str(e)))


class CreateFolderRequest(BaseModel):
    account: str
    folder_name: str
    parent_folder: str | None = None


@app.post("/create-folder")
async def create_folder(request_body: CreateFolderRequest) -> Response:
    try:
        response = check_if_email_accounts_are_connected(request_body.account)
        if not response:
            return response

        status, msg = openmail_clients[
            request_body.account
        ].imap.create_folder(
            request_body.folder_name, request_body.parent_folder
        )
        return Response(success=status, message=msg)
    except Exception as e:
        return Response(success=False, message=err_msg("There was an error while creating folder.", str(e)))


class RenameFolderRequest(BaseModel):
    account: str
    folder_name: str
    new_folder_name: str


@app.post("/rename-folder")
async def rename_folder(request_body: RenameFolderRequest) -> Response:
    try:
        response = check_if_email_accounts_are_connected(request_body.account)
        if not response:
            return response

        status, msg = openmail_clients[
            request_body.account
        ].imap.rename_folder(
            request_body.folder_name, request_body.new_folder_name
        )
        return Response(success=status, message=msg)
    except Exception as e:
        return Response(success=False, message=err_msg("There was an error while renaming folder.", str(e)))


class MoveFolderRequest(BaseModel):
    account: str
    folder_name: str
    destination_folder: str


@app.post("/move-folder")
async def move_folder(request_body: MoveFolderRequest) -> Response:
    try:
        response = check_if_email_accounts_are_connected(request_body.account)
        if not response:
            return response

        status, msg = openmail_clients[request_body.account].imap.move_folder(
            request_body.folder_name, request_body.destination_folder
        )
        return Response(success=status, message=msg)
    except Exception as e:
        return Response(success=False, message=err_msg("There was an error while moving folder.", str(e)))


class DeleteFolderRequest(BaseModel):
    account: str
    folder_name: str


@app.post("/delete-folder")
async def delete_folder(request_body: DeleteFolderRequest) -> Response:
    try:
        response = check_if_email_accounts_are_connected(request_body.account)
        if not response:
            return response

        status, msg = openmail_clients[
            request_body.account
        ].imap.delete_folder(request_body.folder_name)
        return Response(success=status, message=msg)
    except Exception as e:
        return Response(success=False, message=err_msg("There was an error while deleting folder.", str(e)))

#######################################################


def create_uvicorn_info_file(host, port, pid):
    FileSystem().root["uvicorn.info"].write(f"URL=http://{host}:{port}\nPID={pid}\n")


def main():
    http_request_logger.init()

    host = "127.0.0.1"
    port = PortManager.find_free_port(8000, 9000)
    pid = str(os.getpid())
    create_uvicorn_info_file(host, str(port), pid)

    http_request_logger.info(
        "Starting server at http://%s:%d | PID: %s", host, port, pid
    )
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
