"""
This module contains the main FastAPI application and its routes.
TODO: improve docstring
"""
from __future__ import annotations
import os
import concurrent.futures
from urllib.parse import unquote
from typing import Annotated, Callable, Generic, Optional, TypeVar, cast
from contextlib import asynccontextmanager

import uvicorn
from pydantic import BaseModel
from fastapi import FastAPI, Form, UploadFile, Request, Response as FastAPIResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from openmail import OpenMail
from openmail.types import Draft, Attachment, Email, SearchCriteria
from openmail.imap import Folder, Mark

from classes.account_manager import AccountManager, Account, AccountWithPassword
from classes.file_system import FileSystem
from classes.http_request_logger import HTTPRequestLogger
from classes.secure_storage import SecureStorage, SecureStorageKey, RSACipher, SecureStorageKeyValue
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
    accounts: list[AccountWithPassword] = cast(list[AccountWithPassword], account_manager.get_all())
    if not accounts:
        return

    for account in accounts:
        try:
            print(f"Connecting to {account.email_address}...")
            openmail_clients[account.email_address] = OpenMail()
            status, _ = openmail_clients[account.email_address].connect(
                account.email_address,
                RSACipher.decrypt_password(
                    account.encrypted_password,
                    cast(SecureStorageKeyValue, secure_storage.get_key_value(SecureStorageKey.PrivatePem))["value"]
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
                        cast(SecureStorageKeyValue, secure_storage.get_key_value(SecureStorageKey.PrivatePem))["value"]
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
    #secure_storage.destroy()
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

################ ACCOUNT OPERATIONS #################
class GetPublicKeyData(BaseModel):
    public_key: str

@app.get("/get-public-key")
async def get_public_key() -> Response[GetPublicKeyData]:
    return Response[GetPublicKeyData](
        success=True,
        message="Public key fetched successfully",
        data=GetPublicKeyData(
            public_key=cast(SecureStorageKeyValue, secure_storage.get_key_value(SecureStorageKey.PublicPem))["value"]
        )
    )

class GetAccountsData(BaseModel):
    connected: list[Account]
    failed: list[Account]

@app.get("/get-accounts")
def get_accounts() -> Response[GetAccountsData]:
    try:
        all_accounts = account_manager.get_all(include_passwords=False)
        connected_accounts = []
        failed_accounts =[]
        if all_accounts:
            email_to_account = {account.email_address: account for account in all_accounts}
            if openmail_clients:
                connected_accounts = [email_to_account[email_address] for email_address in openmail_clients.keys()]
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
                cast(SecureStorageKeyValue, secure_storage.get_key_value(SecureStorageKey.PrivatePem))["value"]
            )
        )

        if not status:
            return Response(success=status, message=err_msg("Could not connect to email.", msg))

        account_manager.add(AccountWithPassword(
            email_address=request.email_address,
            encrypted_password=RSACipher.encrypt_password(
                RSACipher.decrypt_password(
                    request.encrypted_password,
                    cast(SecureStorageKeyValue, secure_storage.get_key_value(SecureStorageKey.PrivatePem))["value"]
                ),
                cast(SecureStorageKeyValue, secure_storage.get_key_value(SecureStorageKey.PublicPem))["value"]
            ),
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
                    cast(SecureStorageKeyValue, secure_storage.get_key_value(SecureStorageKey.PrivatePem))["value"]
                )
            )

            if not status:
                return Response(success=status, message=err_msg("Could not connect to email.", msg))

            account_manager.edit(AccountWithPassword(
                email_address=request.email_address,
                encrypted_password=RSACipher.encrypt_password(
                    RSACipher.decrypt_password(
                        request.encrypted_password,
                        cast(SecureStorageKeyValue, secure_storage.get_key_value(SecureStorageKey.PrivatePem))["value"]
                    ),
                    cast(SecureStorageKeyValue, secure_storage.get_key_value(SecureStorageKey.PublicPem))["value"]
                ),
                fullname=request.fullname
            ))

            openmail_clients[request.email_address] = openmail_client
            try:
                failed_openmail_clients.remove(request.email_address)
            except ValueError:
                pass
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
        return Response(success=True, message="All accounts removed successfully")
    except Exception as e:
        return Response(success=False, message=err_msg("There was an error while removing accounts.", str(e)))

#####################################################


################ EMAIL OPERATIONS ###################
class OpenMailTaskResult(BaseModel):
    email_address: str
    result: dict | list | str | tuple | object

def execute_openmail_task_concurrently(
    accounts: list[str],
    func: Callable[...],
    **params
) -> list[OpenMailTaskResult]:
    results: list[OpenMailTaskResult] = []
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
    for account in accounts.split(","):
        if account not in openmail_clients:
            return Response(
                success=False,
                message=f"Error, {account} is not (or not anymore) connected."
            )

    return True

@app.get("/get-mailboxes/{accounts}")
async def get_mailboxes(
    accounts: str,
    folder: Optional[str] = None,
    search: Optional[str] = None,
    offset_start: Optional[int] = None,
    offset_end: Optional[int] = None,
) -> Response[list[OpenMailTaskResult]]:
    try:
        response = check_if_email_client_is_exists(accounts)
        if not response:
            return response

        execute_openmail_task_concurrently(
            accounts.split(","),
            lambda client, **params: client.imap.search_emails(**params),
            folder=folder,
            search=SearchCriteria.parse_raw(search) if search else None,
        )

        return Response[list[OpenMailTaskResult]](
            success=True,
            message="Emails fetched successfully.",
            data=execute_openmail_task_concurrently(
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
) -> Response[list[OpenMailTaskResult]]:
    try:
        response = check_if_email_client_is_exists(accounts)
        if not response:
            return response

        return Response[list[OpenMailTaskResult]](
            success=True,
            message="Emails paginated successfully.",
            data=execute_openmail_task_concurrently(
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
) -> Response[list[OpenMailTaskResult]]:
    try:
        response = check_if_email_client_is_exists(accounts)
        if not response:
            return response

        return Response[list[OpenMailTaskResult]](
            success=True,
            message="Folders fetched successfully.",
            data=execute_openmail_task_concurrently(
                accounts.split(","),
                lambda client: client.imap.get_folders(tagged=True),
            ),
        )
    except Exception as e:
        return Response(success=False, message=err_msg("There was an error while fetching folders.", str(e)))

@app.get("/get-email-content/{account}/{folder}/{uid}")
def get_email_content(
    account: str,
    folder: str,
    uid: str
) -> Response[Email]:
    try:
        response = check_if_email_client_is_exists(account)
        if not response:
            return response

        return Response[Email](
            success=True,
            message="Email content fetched successfully.",
            data=openmail_clients[account].imap.get_email_content(unquote(folder), uid),
        )
    except Exception as e:
        return Response(success=False, message=err_msg("There was an error while fetching email content.", str(e)))

@app.get("/download-attachment/{account}/{folder}/{uid}/{name}")
def download_attachment(
    account: str,
    folder: str,
    uid: str,
    name: str,
    cid: str = ""
) -> Response[Attachment]:
    try:
        response = check_if_email_client_is_exists(account)
        if not response:
            return response

        return Response[Attachment](
            success=True,
            message="Email content fetched successfully.",
            data=openmail_clients[account].imap.download_attachment(unquote(folder), uid, name, cid),
        )
    except Exception as e:
        return Response(success=False, message=err_msg("There was an error while fetching email content.", str(e)))

async def convert_uploadfile_to_attachment(attachments: list[UploadFile]) -> list[Attachment]:
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

class SendEmailFormData(BaseModel):
    sender: str # Name Surname <namesurname@domain.com> or namesurname@domain.com
    receiver: str  # mail addresses separated by comma
    subject: str
    body: str
    uid: Optional[str] = None
    cc: Optional[str] = None
    bcc: Optional[str] = None
    attachments: list[UploadFile] = []

@app.post("/send-email")
async def send_email(
    form_data: Annotated[SendEmailFormData, Form()]
) -> Response:
    try:
        response = check_if_email_client_is_exists(form_data.sender)
        if not response:
            return response

        sender = form_data.sender.split("<")
        sender_email = ""
        if len(sender) > 1:
            sender = (sender[0], sender[1])
            sender_email = sender[1][1:-1]
        else:
            sender_email = sender[0]

        status, msg = openmail_clients[sender_email].smtp.send_email(
            Draft(
                sender=form_data.sender,
                receiver=form_data.receiver,
                subject=form_data.subject,
                body=form_data.body,
                cc=form_data.cc,
                bcc=form_data.bcc,
                attachments=await convert_uploadfile_to_attachment(form_data.attachments),
            )
        )

        return Response(success=status, message=msg)
    except Exception as e:
        return Response(success=False, message=err_msg("There was an error while sending email.", str(e)))


@app.post("/reply-email/{original_message_id}")
async def reply_email(
    original_message_id: str,
    form_data: Annotated[SendEmailFormData, Form()]
) -> Response:
    try:
        response = check_if_email_client_is_exists(form_data.sender)
        if not response:
            return response

        sender_email = (
            form_data.sender if isinstance(form_data.sender, str) else form_data.sender[1]
        )
        status, msg = openmail_clients[sender_email].smtp.reply_email(
            Draft(
                sender=form_data.sender,
                receiver=form_data.receiver,
                subject=form_data.subject,
                body=form_data.body,
                cc=form_data.cc,
                bcc=form_data.bcc,
                attachments=await convert_uploadfile_to_attachment(form_data.attachments),
            ),
            original_message_id
        )

        return Response(success=status, message=msg)
    except Exception as e:
        return Response(success=False, message=err_msg("There was an error while replying email.", str(e)))


@app.post("/forward-email/{original_message_id}")
async def forward_email(
    original_message_id: str,
    form_data: Annotated[SendEmailFormData, Form()]
) -> Response:
    try:
        response = check_if_email_client_is_exists(form_data.sender)
        if not response:
            return response

        sender_email = (
            form_data.sender if isinstance(form_data.sender, str) else form_data.sender[1]
        )
        status, msg = openmail_clients[sender_email].smtp.forward_email(
            Draft(
                sender=form_data.sender,
                receiver=form_data.receiver,
                subject=form_data.subject,
                body=form_data.body,
                cc=form_data.cc,
                bcc=form_data.bcc,
                attachments=await convert_uploadfile_to_attachment(form_data.attachments),
            ),
            original_message_id
        )

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
    subfolders: bool

@app.post("/delete-folder")
async def delete_folder(request_body: DeleteFolderRequest) -> Response:
    try:
        response = check_if_email_client_is_exists(request_body.account)
        if not response:
            return response

        status, msg = openmail_clients[
            request_body.account
        ].imap.delete_folder(
            request_body.folder_name,
            request_body.subfolders
        )
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
