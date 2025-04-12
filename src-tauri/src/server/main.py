"""
This module contains the main FastAPI application and its routes.
TODO: improve docstring
"""
from __future__ import annotations
import os
import asyncio
import concurrent.futures
import sys
import time
from urllib.parse import unquote
from typing import Annotated, Callable, Generic, Optional, Sequence, TypeVar, Any, cast
from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor

import uvicorn
from pydantic import BaseModel
from fastapi import FastAPI, Form, UploadFile, Request, Response as FastAPIResponse, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from openmail import OpenMail
from openmail.types import Draft, Attachment, Email, Mailbox, SearchCriteria
from openmail.utils import extract_email_address, extract_email_addresses
from openmail.imap import Folder, Mark

from classes.account_manager import AccountManager, Account, AccountWithPassword
from classes.file_system import FileSystem
from classes.uvicorn_logger import UvicornLogger
from classes.secure_storage import SecureStorage, SecureStorageKey, RSACipher, SecureStorageKeyValue
from classes.port_scanner import PortScanner

from consts import HOST, TRUSTED_HOSTS
from utils import is_email_valid, err_msg, parse_err_msg, get_key_by_value


#################### SET UP #######################
T = TypeVar("T")
MAX_TASK_WORKER = 5
OpenMailTaskResults = dict[str, T]

# Timeouts (in seconds)
IMAP_OPERATION_TIMEOUT = 60
IMAP_LOGGED_OUT_INTERVAL = 60
NEW_EMAIL_CHECK_INTERVAL = 60

account_manager = AccountManager()
secure_storage = SecureStorage()
uvicorn_logger = UvicornLogger()

openmail_clients: dict[str, OpenMail] = {}
failed_openmail_clients: list[str] = []
openmail_clients_for_new_messages: dict[str, OpenMail] = {}
monitor_logged_out_clients_task = None

def connect_to_account(
    account: AccountWithPassword,
    for_new_messages: bool = False
):
    print(f"Connecting to {account.email_address}...")
    target_openmail_clients = openmail_clients_for_new_messages if for_new_messages else openmail_clients
    target_failed_openmail_clients = None if for_new_messages else failed_openmail_clients
    try:
        target_openmail_clients[account.email_address] = OpenMail()
        status, _ = target_openmail_clients[account.email_address].connect(
            account.email_address,
            RSACipher.decrypt_password(
                account.encrypted_password,
                cast(SecureStorageKeyValue, secure_storage.get_key_value(SecureStorageKey.PrivatePem))["value"]
            ),
            imap_enable_idle_optimization=True,
            imap_listen_new_messages=for_new_messages
        )
        if status:
            print(f"Successfully connected to {account.email_address}")
            #target_openmail_clients[account.email_address].imap.idle()
            try:
                if target_failed_openmail_clients: target_failed_openmail_clients.remove(account.email_address)
            except ValueError: pass
        else:
            print(f"Could not successfully connected to {account.email_address}.")
            del target_openmail_clients[account.email_address]
            if target_failed_openmail_clients: target_failed_openmail_clients.append(account.email_address)
    except Exception as e:
        del target_openmail_clients[account.email_address]
        if target_failed_openmail_clients: target_failed_openmail_clients.append(account.email_address)
        uvicorn_logger.error(f"Failed while connecting to {account.email_address}: {e}")

def create_openmail_clients():
    try:
        print("OpenMail clients are creating...")
        accounts: list[AccountWithPassword] = cast(list[AccountWithPassword], account_manager.get_all())
        if not accounts:
            return

        with ThreadPoolExecutor(max_workers=MAX_TASK_WORKER) as executor:
            executor.map(connect_to_account, accounts)
    except Exception as e:
        uvicorn_logger.error(f"Error while creating openmail clients: {e}")
        raise e

    """
    # TODO: Open this later
    # Check logged out clients and reconnect them.
    try:
        global monitor_logged_out_clients_task
        monitor_logged_out_clients_task = asyncio.create_task(monitor_logged_out_openmail_clients())
    except Exception as e:
        uvicorn_logger.error(f"Error while creating monitors to logged out openmail clients: {e}")
        pass"""

def reconnect_to_account(
    email_address: str,
    for_new_messages: bool = False
):
    print(f"Reconnecton for {email_address}...")
    target_openmail_clients = openmail_clients_for_new_messages if for_new_messages else openmail_clients
    target_failed_openmail_clients = None if for_new_messages else failed_openmail_clients
    try:
        created_openmail_clients = target_openmail_clients.keys()
        if email_address not in created_openmail_clients:
            return

        if not target_openmail_clients[email_address].imap.is_logged_out():
            print(f"No need to reconnect for {email_address}")
            return

        account = account_manager.get(email_address)
        if account:
            connect_to_account(account, for_new_messages)
        else:
            print(f"{email_address} could not found while trying to reconnect.")
    except Exception as e:
        del target_openmail_clients[email_address]
        if target_failed_openmail_clients: target_failed_openmail_clients.append(email_address)
        uvicorn_logger.error(f"Failed while reconnecting to {email_address}: {e}")

def reconnect_logged_out_openmail_clients():
    print("Reconnecting to OpenMail clients...",)
    with ThreadPoolExecutor(max_workers=MAX_TASK_WORKER) as executor:
        for email_address, client in openmail_clients.items():
            executor.submit(reconnect_to_account, email_address, False)
        for email_address, client in openmail_clients_for_new_messages.items():
            executor.submit(reconnect_to_account, email_address, True)

async def monitor_logged_out_openmail_clients():
    try:
        while True:
            await asyncio.sleep(IMAP_LOGGED_OUT_INTERVAL)
            print("Checking logged out OpenMail clients...")
            reconnect_logged_out_openmail_clients()
    except asyncio.CancelledError:
        uvicorn_logger.info("Monitoring logged out clients task is being cancelled...")
        raise

def shutdown_openmail_clients():
    try:
        uvicorn_logger.info("Shutting down openmail clients...")
        with ThreadPoolExecutor(max_workers=MAX_TASK_WORKER) as executor:
            for clients in [openmail_clients, openmail_clients_for_new_messages]:
                executor.map(lambda client: client[1].disconnect(), clients.items())
    except Exception as e:
        uvicorn_logger.error(f"Openmail clients could not properly terminated: {e}")

def shutdown_monitors():
    global monitor_logged_out_clients_task
    if monitor_logged_out_clients_task:
        monitor_logged_out_clients_task.cancel()

def shutdown_completely() -> None:
    uvicorn_logger.info("Shutdown signal received. Starting to logging out and terminating threads...")
    try:
        shutdown_openmail_clients()
        shutdown_monitors()
    except Exception as e:
        uvicorn_logger.error("Shutdown could not properly executed.")

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        create_openmail_clients()
        yield
    finally:
        shutdown_completely()

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
    allowed_hosts=TRUSTED_HOSTS
)

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
"""
def execute_openmail_task_concurrently(
    accounts: set[str], # unique email addresses
    func: Callable[...],
    **params
) -> OpenMailTaskResults:
    result: OpenMailTaskResults = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_TASK_WORKER) as executor:
        future_to_emails = {
            executor.submit(func, client, **params): email_address
            for email_address, client in openmail_clients.items()
            if email_address in accounts
        }

        for future in concurrent.futures.as_completed(future_to_emails, IMAP_OPERATION_TIMEOUT):
            email_address = future_to_emails[future]
            future = future.result()
            result[email_address] = future
            print(f"Result for {email_address}: {future}") # TODO: Comment this

        return result

# Usage examples of `execute_openmail_task_concurrently`:
# instance.imap.get_folders()
execute_openmail_task_concurrently(
    unique_email_addresses,
    lambda client, **params: client.imap.get_folders(),
)
# instance.imap.search_emails()
execute_openmail_task_concurrently(
    unique_email_addresses,
    lambda client, **params: client.imap.search_emails(**params),
    folder=folder,
    search=SearchCriteria.parse_raw(search) if search else None,
)
# instance.imap.get_emails()
execute_openmail_task_concurrently(
    unique_email_addresses,
    lambda client, **params: client.imap.get_emails(**params),
    offset_start=offset_start,
    offset_end=offset_end,
)
"""

def check_openmail_connection_availability(
    account: str,
    for_new_messages: bool = False
) -> Response | bool:
    target_openmail_clients = openmail_clients_for_new_messages if for_new_messages else openmail_clients

    if not target_openmail_clients[account].imap.is_logged_out():
        print(f"No need to reconnect for {account}")
        return True

    reconnect_to_account(account, for_new_messages)

    if not target_openmail_clients[account].imap.is_logged_out():
        print(f"No need to reconnect for {account}")
        return True

    return Response(
        success=False,
        message=f'Error, {account} connection is not available or timed out and could not reconnected.'
    )

@app.websocket("/notifications/{account}")
async def notifications_socket(websocket: WebSocket, account: str):
    await websocket.accept()
    uvicorn_logger.websocket(websocket, "New notification subscription created")
    try:
        while True:
            account = extract_email_address(account)
            if account in openmail_clients_for_new_messages:
                response = check_openmail_connection_availability(account, True)
                if isinstance(response, Response):
                    await websocket.close(reason=response.message)
                    uvicorn_logger.websocket(websocket, response.message)
                    break
            else:
                account = account_manager.get(account)
                if account:
                    connect_to_account(account, True)
                else:
                    reason = f"There is no account with {account} email address."
                    await websocket.close(reason=reason)
                    uvicorn_logger.websocket(websocket, reason)
                    break

            # Listen for new messages and send notification when
            # any new message received.
            while True:
                try:
                    await asyncio.sleep(NEW_EMAIL_CHECK_INTERVAL)
                    print(f"Checking for new emails for {account}")
                    if openmail_clients_for_new_messages[account].imap.any_new_email():
                        print(f"Account {account} has new emails")
                        recent_emails = openmail_clients_for_new_messages[account].imap.get_recent_emails()
                        await websocket.send_json({account: recent_emails})
                        uvicorn_logger.websocket(websocket, recent_emails)
                except Exception as e:
                    await websocket.close(reason="There was an error while receving new emails.")
                    uvicorn_logger.websocket(websocket, e)
                    break
    except WebSocketDisconnect:
        pass

@app.get("/get-hierarchy-delimiter/{account}")
async def get_hierarchy_delimiter(
    account: str
) -> Response[OpenMailTaskResults[str]]:
    try:
        account = extract_email_address(account)
        response = check_openmail_connection_availability(account)
        if isinstance(response, Response):
            return response

        return Response(
            success=True,
            message="IMAP hierarchy delimiter found successfully.",
            data={account: openmail_clients[account].imap.hierarchy_delimiter}
        )
    except Exception as e:
        return Response(success=False, message=err_msg("There was an error while getting IMAP hierarchy delimiter", str(e)))

@app.get("/get-mailbox/{account}")
async def get_mailbox(
    account: str,
    folder: Optional[str] = None,
    search: Optional[str] = None,
    offset_start: Optional[int] = None,
    offset_end: Optional[int] = None,
) -> Response[OpenMailTaskResults[Mailbox]]:
    try:
        account = extract_email_address(account)
        response = check_openmail_connection_availability(account)
        if isinstance(response, Response):
            return response

        # Search Emails
        openmail_clients[account].imap.search_emails(folder=folder)

        # Fetch and send fetched emails.
        return Response(
            success=True,
            message="Emails fetched successfully.",
            data={account: openmail_clients[account].imap.get_emails(offset_start, offset_end)}
        )
    except Exception as e:
        return Response(success=False, message=err_msg("There was an error while fetching emails.", str(e)))

@app.get("/paginate-mailbox/{account}")
async def paginate_mailbox(
    account: str,
    offset_start: int | None = None,
    offset_end: int | None = None
) -> Response[OpenMailTaskResults[Mailbox]]:
    try:
        account = extract_email_address(account)
        response = check_openmail_connection_availability(account)
        if isinstance(response, Response):
            return response

        return Response(
            success=True,
            message="Emails paginated successfully.",
            data={account: openmail_clients[account].imap.get_emails(offset_start, offset_end)}
        )
    except Exception as e:
        return Response(success=False, message=err_msg("There was an error while paginating emails.", str(e)))

@app.get("/get-folders/{account}")
async def get_folders(
    account: str,
) -> Response[OpenMailTaskResults[list[str]]]:
    try:
        account = extract_email_address(account)
        response = check_openmail_connection_availability(account)
        if isinstance(response, Response):
            return response

        return Response(
            success=True,
            message="Folders fetched successfully.",
            data={account: openmail_clients[account].imap.get_folders(tagged=True)}
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
        account = extract_email_address(account)
        response = check_openmail_connection_availability(account)
        if isinstance(response, Response):
            return response

        return Response(
            success=True,
            message="Email content fetched successfully.",
            data=openmail_clients[account].imap.get_email_content(unquote(folder), uid)
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
        account = extract_email_address(account)
        response = check_openmail_connection_availability(account)
        if isinstance(response, Response):
            return response

        return Response[Attachment](
            success=True,
            message="Email content fetched successfully.",
            data=openmail_clients[account].imap.download_attachment(
                unquote(folder),
                uid,
                name,
                cid
            ),
        )
    except Exception as e:
        return Response(success=False, message=err_msg("There was an error while fetching email content.", str(e)))

async def convert_uploadfile_to_attachment(attachments: list[UploadFile]) -> list[Attachment]:
    converted_to_attachment_list = []
    if not attachments:
        return []

    for attachment in attachments:
        data = await attachment.read()
        if data:
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
    receivers: str  # mail addresses separated by comma
    subject: str
    body: str
    uid: Optional[str] = None
    cc: Optional[str] = None # mail addresses separated by comma
    bcc: Optional[str] = None # mail addresses separated by comma
    attachments: list[UploadFile] = []

@app.post("/send-email")
async def send_email(
    form_data: Annotated[SendEmailFormData, Form()],
) -> Response:
    try:
        account = extract_email_address(form_data.sender)
        response = check_openmail_connection_availability(account)
        if isinstance(response, Response):
            return response

        status, msg = openmail_clients[account].smtp.send_email(
            Draft(
                sender=form_data.sender,
                receivers=form_data.receivers,
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
        account = extract_email_address(form_data.sender)
        response = check_openmail_connection_availability(account)
        if isinstance(response, Response):
            return response

        status, msg = openmail_clients[account].smtp.reply_email(
            original_message_id,
            Draft(
                sender=form_data.sender,
                receivers=form_data.receivers,
                subject=form_data.subject,
                body=form_data.body,
                cc=form_data.cc,
                bcc=form_data.bcc,
                attachments=await convert_uploadfile_to_attachment(form_data.attachments),
            )
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
        account = extract_email_address(form_data.sender)
        response = check_openmail_connection_availability(account)
        if isinstance(response, Response):
            return response

        status, msg = openmail_clients[account].smtp.forward_email(
            original_message_id,
            Draft(
                sender=form_data.sender,
                receivers=form_data.receivers,
                subject=form_data.subject,
                body=form_data.body,
                cc=form_data.cc,
                bcc=form_data.bcc,
                attachments=await convert_uploadfile_to_attachment(form_data.attachments),
            )
        )

        return Response(success=status, message=msg)
    except Exception as e:
        return Response(success=False, message=err_msg("There was an error while forwarding email.", str(e)))

@app.post("/save-email-as-draft")
async def save_email_as_draft(
    form_data: Annotated[SendEmailFormData, Form()],
    appenduid: str | None = None
) -> Response:
    try:
        account = extract_email_address(form_data.sender)
        response = check_openmail_connection_availability(account)
        if isinstance(response, Response):
            return response

        appenduid = openmail_clients[account].imap.save_email_as_draft(
            openmail_clients[account].smtp.create_email(Draft(
                sender=form_data.sender,
                receivers=form_data.receivers,
                subject=form_data.subject,
                body=form_data.body,
                cc=form_data.cc,
                bcc=form_data.bcc,
                attachments=await convert_uploadfile_to_attachment(form_data.attachments),
            )),
            appenduid
        )

        return Response(success=True, message="Email saved as draft successfully.", data={appenduid: appenduid})
    except Exception as e:
        return Response(success=False, message=err_msg("There was an error while saving email as draft.", str(e)))

class MarkEmailRequest(BaseModel):
    account: str
    mark: str
    sequence_set: str
    folder: str = Folder.Inbox


@app.post("/mark-email")
async def mark_email(request_body: MarkEmailRequest) -> Response:
    try:
        account = extract_email_address(request_body.account)
        response = check_openmail_connection_availability(account)
        if isinstance(response, Response):
            return response

        status, msg = openmail_clients[account].imap.mark_email(
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
        account = extract_email_address(request_body.account)
        response = check_openmail_connection_availability(account)
        if isinstance(response, Response):
            return response

        status, msg = openmail_clients[account].imap.unmark_email(
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
        account = extract_email_address(request_body.account)
        response = check_openmail_connection_availability(account)
        if isinstance(response, Response):
            return response

        status, msg = openmail_clients[account].imap.move_email(
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
        account = extract_email_address(request_body.account)
        response = check_openmail_connection_availability(account)
        if isinstance(response, Response):
            return response

        status, msg = openmail_clients[account].imap.copy_email(
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
        account = extract_email_address(request_body.account)
        response = check_openmail_connection_availability(account)
        if isinstance(response, Response):
            return response

        status, msg = openmail_clients[account].imap.delete_email(
            request_body.folder,
            request_body.sequence_set
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
        account = extract_email_address(request_body.account)
        response = check_openmail_connection_availability(account)
        if isinstance(response, Response):
            return response

        status, msg = openmail_clients[account].imap.create_folder(
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
        account = extract_email_address(request_body.account)
        response = check_openmail_connection_availability(account)
        if isinstance(response, Response):
            return response

        status, msg = openmail_clients[account].imap.rename_folder(
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
        account = extract_email_address(request_body.account)
        response = check_openmail_connection_availability(account)
        if isinstance(response, Response):
            return response

        status, msg = openmail_clients[account].imap.move_folder(
            request_body.folder_name, request_body.destination_folder
        )
        return Response(success=status, message=msg)
    except Exception as e:
        return Response(success=False, message=err_msg("There was an error while moving folder.", str(e)))


class DeleteFolderRequest(BaseModel):
    account: str
    folder_name: str
    delete_subfolders: bool

@app.post("/delete-folder")
async def delete_folder(request_body: DeleteFolderRequest) -> Response:
    try:
        account = extract_email_address(request_body.account)
        response = check_openmail_connection_availability(account)
        if isinstance(response, Response):
            return response

        status, msg = openmail_clients[account].imap.delete_folder(
            request_body.folder_name,
            request_body.delete_subfolders
        )
        return Response(success=status, message=msg)
    except Exception as e:
        return Response(success=False, message=err_msg("There was an error while deleting folder.", str(e)))

class UnsubscribeEmailRequest(BaseModel):
    account: str
    list_unsubscribe: str
    list_unsubscribe_post: str | None = None

@app.post("/unsubscribe-email")
async def unsubscribe_email(request_body: UnsubscribeEmailRequest) -> Response:
    try:
        account = extract_email_address(request_body.account)
        response = check_openmail_connection_availability(account)
        if isinstance(response, Response):
            return response

        status, msg = openmail_clients[account].smtp.unsubscribe(
            request_body.account,
            request_body.list_unsubscribe,
            request_body.list_unsubscribe_post
        )
        return Response(success=status, message=msg)
    except Exception as e:
        return Response(success=False, message=err_msg("There was an error while unsubscribing.", str(e)))

#######################################################

def main():
    port = PortScanner.find_free_port(8000, 9000)
    pid = str(os.getpid())
    FileSystem().get_uvicorn_info().write(f"URL=http://{HOST}:{str(port)}\nPID={pid}\n")

    uvicorn_logger.info(
        "Starting server at http://%s:%d | PID: %s", HOST, port, pid
    )
    uvicorn.run(app, host=HOST, port=port)

if __name__ == "__main__":
    main()
