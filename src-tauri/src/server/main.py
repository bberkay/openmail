"""
This module contains the main FastAPI application and its routes.
TODO: improve docstring
"""
from __future__ import annotations
import os
import concurrent.futures
from urllib.parse import unquote
from typing import Annotated, Callable, Generic, Optional, TypeVar
from contextlib import asynccontextmanager

import uvicorn
from pydantic import BaseModel
from fastapi import FastAPI, Form, UploadFile, Request, Response as FastAPIResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from openmail import OpenMail
from openmail.types import EmailToSend, Attachment, EmailWithContent, Mailbox
from openmail.imap import Folder, Mark

from classes.account_manager import AccountManager, Account, AccountWithPassword
from classes.file_system import FileSystem
from classes.http_request_logger import HTTPRequestLogger
from classes.secure_storage import SecureStorage, SecureStorageKey, RSACipher
from classes.port_scanner import PortScanner

from consts import TRUSTED_HOSTS
from utils import is_email_valid, err_msg, parse_err_msg


#################### SET UP #######################
openmail_clients: dict[str, OpenMail] = {}
failed_openmail_clients: list[str] = []
account_manager = AccountManager()
secure_storage = SecureStorage()
http_request_logger = HTTPRequestLogger()
T = TypeVar("T")

def create_and_idle_openmail_clients():
    accounts: list[AccountWithPassword] = account_manager.get()
    if not accounts:
        return

    for account in accounts:
        try:
            openmail_clients[account.email_address] = OpenMail()
            status, _ = openmail_clients[account.email_address].connect(
                account.email_address,
                RSACipher.decrypt_password(
                    account.encrypted_password,
                    secure_storage.get_key_value(SecureStorageKey.PRIVATE_PEM)
                )
            )
            print(f"Connected to {account.email_address}")
            """if status:
                openmail_clients[account["email_address"]].imap.idle()"""
        except Exception as e:
            openmail_clients.pop(account.email_address)
            failed_openmail_clients.append(account.email_address)
            print(f"Failed to connect to {account.email_address}: {e}")

def reconnect_and_idle_logged_out_openmail_clients():
    # TODO: Implement reconnection
    for email_address, openmail_client in openmail_clients.items():
        if not openmail_client.is_logged_in():
            accounts: list[AccountWithPassword] = account_manager.get(email_address)
            if accounts:
                status = openmail_client.connect(
                    email_address,
                    RSACipher.decrypt_password(
                        accounts[0].encrypted_password,
                        secure_storage.get_key_value(SecureStorageKey.PRIVATE_PEM)
                    )
                )
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

class Response(BaseModel, Generic[T]):
    success: bool
    message: str
    data: Optional[T] = None

@app.middleware("http")
async def catch_request_for_logging(request: Request, call_next):
    async def get_response_body(response: FastAPIResponse) -> bytes:
        response_body = b""
        async for chunk in response.body_iterator:
            response_body += chunk
            return response_body

    response = await call_next(request)
    response._body = await get_response_body(response)
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

@app.post("/recreate-whole-universe")
def recreate_whole_universe() -> Response:
    try:
        FileSystem().reset()
        account_manager.remove_all()
        return Response(success=True, message="You asked and the whole universe completely recreated!")
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
class GetPublicKeyData(BaseModel):
    public_key: str

@app.get("/get-public-key")
async def get_public_key() -> Response[GetPublicKeyData]:
    return Response[GetPublicKeyData](
        success=True,
        message="Public key fetched successfully",
        data=GetPublicKeyData(
            public_key=secure_storage.get_key_value(SecureStorageKey.PUBLIC_PEM)
        )
    )

class GetAccountsData(BaseModel):
    connected: list[Account]
    failed: list[Account]

@app.get("/get-accounts")
def get_accounts() -> Response[GetAccountsData]:
    try:
        all_accounts = account_manager.get(include_encrypted_passwords=False)
        email_to_account = {account.email_address: account for account in all_accounts}

        connected_accounts = []
        if openmail_clients:
            connected_accounts = [email_to_account[email_address] for email_address in openmail_clients.keys()]

        failed_accounts = []
        if failed_openmail_clients:
            failed_accounts = [email_to_account[email_address] for email_address in failed_openmail_clients]

        return Response[GetAccountsData](
            success=True,
            message="Email accounts fetched successfully",
            data=GetAccountsData(
                connected=connected_accounts,
                failed=failed_accounts
            )
        )
    except Exception as e:
        return Response(success=False, message=err_msg("Failed to fetch email accounts.", str(e)))

class AddAccountRequest(BaseModel):
    email_address: str
    encrypted_password: str
    fullname: Optional[str] = None

@app.post("/add-account")
def add_account(
    request: AddAccountRequest
) -> Response:
    if not is_email_valid(request.email_address):
        return Response(success=False, message="Invalid email address format")

    try:
        if account_manager.is_exists(request.email_address):
            return Response(success=False, message="Email address already exists")

        openmail_client = OpenMail()
        status, msg = openmail_client.connect(
            request.email_address,
            RSACipher.decrypt_password(
                request.encrypted_password,
                secure_storage.get_key_value(SecureStorageKey.PRIVATE_PEM)
            )
        )

        if not status:
            return Response(success=status, message=err_msg("Could not connect to email.", msg))

        account_manager.add(AccountWithPassword(
            email_address=request.email_address,
            encrypted_password=request.encrypted_password,
            fullname=request.fullname
        ))

        openmail_clients[request.email_address] = openmail_client
        return Response(
            success=True,
            message="Account successfully added"
        )
    except Exception as e:
        return Response(success=False, message=err_msg("Failed to add email.", str(e)))

class EditAccountRequest(BaseModel):
    email_address: str
    encrypted_password: Optional[str] = None
    fullname: Optional[str] = None

@app.post("/edit-account")
def edit_account(
    request: EditAccountRequest
) -> Response:
    if not is_email_valid(request.email_address):
        return Response(success=False, message="Invalid email address format")

    try:
        # E-mail cannot be edited.
        if not account_manager.is_exists(request.email_address):
            return Response(success=False, message="Email address does not exists")

        if not request.encrypted_password:
            account_manager.edit(Account(
                email_address=request.email_address,
                fullname=request.fullname
            ))
        else:
            # If user trying to edit password, connect to the email again.
            openmail_client = OpenMail()
            status, msg = openmail_client.connect(
                request.email_address,
                RSACipher.decrypt_password(
                    request.encrypted_password,
                    secure_storage.get_key_value(SecureStorageKey.PRIVATE_PEM)
                )
            )

            if not status:
                return Response(success=status, message=err_msg("Could not connect to email.", msg))

            account_manager.edit(AccountWithPassword(
                email_address=request.email_address,
                encrypted_password=request.encrypted_password,
                fullname=request.fullname
            ))

            openmail_clients[request.email_address] = openmail_client
            failed_openmail_clients.pop(request.email_address)

        return Response(
            success=True,
            message="Account successfully edited"
        )
    except Exception as e:
        return Response(success=False, message=err_msg("Failed to add email.", str(e)))


class RemoveAccountRequest(BaseModel):
    account: str

@app.post("/remove-account")
def remove_email_account(request_body: RemoveAccountRequest) -> Response:
    try:
        account_manager.remove(request_body.account)
        return Response(success=True, message="Account removed successfully")
    except Exception as e:
        return Response(success=False, message=err_msg("There was an error while removing account.", str(e)))


@app.post("/remove-accounts")
def remove_accounts() -> Response:
    try:
        account_manager.remove_all()
        return Response(success=True, message="Accounts removed successfully")
    except Exception as e:
        return Response(success=False, message=err_msg("There was an error while removing accounts.", str(e)))

#####################################################


################ EMAIL OPERATIONS ###################
class OpenMailTaskResult(BaseModel, Generic[T]):
    email_address: str
    result: T

type OpenMailTaskResults[T] = list[OpenMailTaskResult[T]]

def execute_openmail_task_concurrently[T](
    accounts: list[str],
    func: Callable[..., T],
    **params
) -> OpenMailTaskResults[T]:
    results: OpenMailTaskResults[T] = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_emails = {
            executor.submit(func, client, **params): email_address
            for email_address, client in openmail_clients.items()
            if email_address in accounts
        }

        for future in concurrent.futures.as_completed(future_to_emails):
            email_address = future_to_emails[future]
            future = future.result()
            results.append(OpenMailTaskResult(
                email_address=email_address,
                result=future
            ))
            print(f"Result for {email_address}: {future}")

        return results

def check_if_email_client_is_exists(accounts: str) -> Response | bool:
    accounts = accounts.split(",")

    for account in accounts:
        if account not in openmail_clients:
            return Response(
                success=False,
                message=f"Email account: {account} is not connected"
            )

    return True

@app.get("/get-mailboxes/{accounts}")
async def get_mailboxes(
    accounts: str,
    folder: Optional[str] = "INBOX",
    search: Optional[str] = "ALL",
    offset_start: Optional[int] = 0,
    offset_end: Optional[int] = 10,
) -> Response[OpenMailTaskResults[Mailbox]]:
    try:
        response = check_if_email_client_is_exists(accounts)
        if not response:
            return response

        execute_openmail_task_concurrently(
            accounts.split(","),
            lambda client, **params: client.imap.search_emails(**params),
            folder=folder,
            search=search,
        )

        return Response[OpenMailTaskResults[Mailbox]](
            success=True,
            message="Emails fetched successfully.",
            data=execute_openmail_task_concurrently[Mailbox](
                accounts.split(","),
                lambda client, **params: client.imap.get_emails(**params),
                offset_start=offset_start,
                offset_end=offset_end,
            ),
        )
    except Exception as e:
        return Response(success=False, message=err_msg("There was an error while fetching emails.", str(e)))

@app.get("/paginate-mailboxes/{accounts}/{offset_start}/{offset_end}")
async def paginate_mailboxes(
    accounts: str,
    offset_start: int,
    offset_end: int,
) -> Response[OpenMailTaskResults[Mailbox]]:
    try:
        response = check_if_email_client_is_exists(accounts)
        if not response:
            return response

        return Response[OpenMailTaskResults[Mailbox]](
            success=True,
            message="Emails paginated successfully.",
            data=execute_openmail_task_concurrently[Mailbox](
                accounts.split(","),
                lambda client, **params: client.imap.get_emails(**params),
                offset_start=offset_start,
                offset_end=offset_end,
            ),
        )
    except Exception as e:
        return Response(success=False, message=err_msg("There was an error while paginating emails.", str(e)))

@app.get("/get-folders/{accounts}")
async def get_folders(
    accounts: str,
) -> Response[OpenMailTaskResults[list[str]]]:
    try:
        response = check_if_email_client_is_exists(accounts)
        if not response:
            return response

        return Response[OpenMailTaskResults[list[str]]](
            success=True,
            message="Folders fetched successfully.",
            data=execute_openmail_task_concurrently[list[str]](
                accounts.split(","),
                lambda client: client.imap.get_folders(),
            ),
        )
    except Exception as e:
        return Response(success=False, message=err_msg("There was an error while fetching folders.", str(e)))

@app.get("/get-email-content/{account}/{folder}/{uid}")
def get_email_content(
    account: str,
    folder: str,
    uid: str
) -> Response[EmailWithContent]:
    try:
        response = check_if_email_client_is_exists(account)
        if not response:
            return response

        return Response[EmailWithContent](
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
        response = check_if_email_client_is_exists(formData.sender)
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
                if Mark.Seen not in flags:
                    status, com_msg = openmail_clients[sender_email].imap.mark_email(
                        formData.uid, Mark.Seen
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
        response = check_if_email_client_is_exists(formData.sender)
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
                if Mark.Answered not in flags:
                    status, com_msg = openmail_clients[sender_email].imap.mark_email(
                        formData.uid, Mark.Answered
                    )
                    msg += " " + f"And {com_msg}"
                if Mark.Seen not in flags:
                    status, com_msg = openmail_clients[sender_email].imap.mark_email(
                        formData.uid, Mark.Seen
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
        response = check_if_email_client_is_exists(formData.sender)
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
                if Mark.Answered not in flags:
                    status, com_msg = openmail_clients[sender_email].imap.mark_email(
                        formData.uid, Mark.Answered
                    )
                    msg += " " + f"And {com_msg}"
                if Mark.Seen not in flags:
                    status, com_msg = openmail_clients[sender_email].imap.mark_email(
                        formData.uid, Mark.Seen
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
        response = check_if_email_client_is_exists(request_body.account)
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
        response = check_if_email_client_is_exists(request_body.account)
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
        response = check_if_email_client_is_exists(request_body.account)
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
        response = check_if_email_client_is_exists(request_body.account)
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
        response = check_if_email_client_is_exists(request_body.account)
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
        response = check_if_email_client_is_exists(request_body.account)
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
        response = check_if_email_client_is_exists(request_body.account)
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
        response = check_if_email_client_is_exists(request_body.account)
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
        response = check_if_email_client_is_exists(request_body.account)
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
    port = PortScanner.find_free_port(8000, 9000)
    pid = str(os.getpid())
    create_uvicorn_info_file(host, str(port), pid)

    http_request_logger.info(
        "Starting server at http://%s:%d | PID: %s", host, port, pid
    )
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
