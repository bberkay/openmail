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
from openmail.types import Draft, Attachment, Email, SearchCriteria
from openmail.utils import extract_email_addresses
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
MAX_CONNECTION_WORKER = 5
# Timeouts (in seconds)
IMAP_OPERATION_TIMEOUT = 60
IMAP_LOGGED_OUT_INTERVAL = 60
NEW_EMAIL_CHECK_INTERVAL = 60

account_manager = AccountManager()
secure_storage = SecureStorage()
uvicorn_logger = UvicornLogger()

openmail_clients: dict[str, OpenMail] = {}
openmail_clients_for_new_messages: dict[str, OpenMail] = {}
failed_openmail_clients: list[str] = []
monitor_logged_out_clients_task = None

def shutdown_openmail_clients(exit: bool = False):
    try:
        uvicorn_logger.info("Shutting down openmail clients...")
        for email, openmail_client in openmail_clients.items():
            openmail_client.disconnect()
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

def connect_to_account(account: AccountWithPassword):
    print(f"Connecting to {account.email_address}...")
    try:
        openmail_clients[account.email_address] = OpenMail()
        status, _ = openmail_clients[account.email_address].connect(
            account.email_address,
            RSACipher.decrypt_password(
                account.encrypted_password,
                cast(SecureStorageKeyValue, secure_storage.get_key_value(SecureStorageKey.PrivatePem))["value"]
            ),
            imap_enable_idle_optimization=True,
            imap_listen_new_messages=False
        )
        if status:
            print(f"Successfully connected to {account.email_address}")
            openmail_clients[account.email_address].imap.idle()
            try: failed_openmail_clients.remove(account.email_address)
            except ValueError: pass
        else:
            print(f"Could not successfully connected to {account.email_address}.")
            del openmail_clients[account.email_address]
            failed_openmail_clients.append(account.email_address)
    except Exception as e:
        del openmail_clients[account.email_address]
        failed_openmail_clients.append(account.email_address)
        uvicorn_logger.error(f"Failed while connecting to {account.email_address}: {e}")

def create_openmail_clients():
    try:
        print("OpenMail clients are creating...")
        accounts: list[AccountWithPassword] = cast(list[AccountWithPassword], account_manager.get_all())
        if not accounts:
            return

        with ThreadPoolExecutor(max_workers=MAX_CONNECTION_WORKER) as executor:
            executor.map(connect_to_account, accounts)
    except Exception as e:
        uvicorn_logger.error(f"Error while creating openmail clients: {e}")
        raise e

    # Check logged out clients and reconnect them.
    try:
        global monitor_logged_out_clients_task
        monitor_logged_out_clients_task = asyncio.create_task(monitor_logged_out_openmail_clients())
    except Exception as e:
        uvicorn_logger.error(f"Error while creating monitors to logged out openmail clients: {e}")
        pass

def reconnect_to_account(email_address: str):
    print(f"Reconnecton for {email_address}...")
    try:
        created_openmail_clients = openmail_clients.keys()
        if email_address not in created_openmail_clients:
            return

        if not openmail_clients[email_address].imap.is_logged_out():
            print(f"No need to reconnect for {email_address}")
            return

        account: list[AccountWithPassword] = account_manager.get(email_address)
        if account:
            connect_to_account(account)
        else:
            print(f"{email_address} could not found while trying to reconnect.")
    except Exception as e:
        del openmail_clients[email_address]
        failed_openmail_clients.append(email_address)
        uvicorn_logger.error(f"Failed while reconnecting to {email_address}: {e}")

def reconnect_logged_out_openmail_clients(email_addresses: list[str]):
    print("Reconnecting to OpenMail clients: ", email_addresses)
    with ThreadPoolExecutor(max_workers=MAX_CONNECTION_WORKER) as executor:
        executor.map(reconnect_to_account, email_addresses)

async def monitor_logged_out_openmail_clients():
    try:
        while True:
            await asyncio.sleep(IMAP_LOGGED_OUT_INTERVAL)
            print("Checking logged out OpenMail clients...")
            reconnect_logged_out_openmail_clients(list(openmail_clients.keys()))
    except asyncio.CancelledError:
        uvicorn_logger.info("Monitoring logged out clients task is being cancelled...")
        raise

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
def get_unique_email_addresses(accounts: str) -> set[str]:
    """
    Get unique email addresses of given accounts.

    Args:
        accounts (str): Email addresses with or without fullnames separated
        by comma.

    Returns:
        set[str]: Unique email addresses.

    Example:
        >>> get_unique_email_addresses("Alex Doe <alex@domain.com>, John Doe <john@domain.com>, Jane Doe <alex@domain.com>")
        set("alex@domain.com", "john@domain.com")
    """
    return set(extract_email_addresses(accounts.split(",")))

class OpenMailTaskResult(BaseModel):
    email_address: str
    result: Any

def execute_openmail_task_concurrently(
    accounts: set[str], # unique email addresses
    func: Callable[...],
    **params
) -> list[OpenMailTaskResult]:
    results: list[OpenMailTaskResult] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_CONNECTION_WORKER) as executor:
        future_to_emails = {
            executor.submit(func, client, **params): email_address
            for email_address, client in openmail_clients.items()
            if email_address in accounts
        }

        for future in concurrent.futures.as_completed(future_to_emails, IMAP_OPERATION_TIMEOUT):
            email_address = future_to_emails[future]
            future = future.result()
            results.append(OpenMailTaskResult(
                email_address=email_address,
                result=future
            ))
            print(f"Result for {email_address}: {future}")

        return results

def check_openmail_connection_availability(
    accounts: set[str] # unique email addresses
) -> Response | bool:
    connected_openmail_clients = openmail_clients.keys()
    terminated_openmail_clients = []
    for account in accounts:
        if account not in connected_openmail_clients:
            terminated_openmail_clients.append(account)

    if not terminated_openmail_clients or len(terminated_openmail_clients) == 0:
        return True

    reconnect_logged_out_openmail_clients(terminated_openmail_clients)

    connected_openmail_clients = openmail_clients.keys()
    for account in terminated_openmail_clients:
        if account not in connected_openmail_clients:
            return Response(
                success=False,
                message=f'Error, {account} connection is not available or timed out and could not reconnected.'
            )

    return True

@app.websocket("/notifications/{accounts}")
async def notifications_socket(websocket: WebSocket, accounts: str):
    await websocket.accept()
    uvicorn_logger.websocket(websocket, "New notification subscription created")
    try:
        while True:
            unique_email_addresses = get_unique_email_addresses(accounts)
            response = check_openmail_connection_availability(unique_email_addresses)
            if isinstance(response, Response):
                await websocket.close(reason=response.message)
                uvicorn_logger.websocket(websocket, response.message)
                break

            """
            TODO: Independent openmail clients just for recent messages.
            for account in unique_email_addresses:
                openmail_clients_for_new_messages[account] = OpenMail()"""

            # Listen for new messages and send notification when
            # any new message received.
            while True:
                try:
                    await asyncio.sleep(NEW_EMAIL_CHECK_INTERVAL)
                    print("Checking for new emails for these accounts: ", accounts)
                    any_new_email: Callable[[OpenMail], bool] = lambda client: client.imap.any_new_email()
                    task_results = execute_openmail_task_concurrently(unique_email_addresses, any_new_email)
                    new_email_accounts = set(account.email_address for account in task_results if account.result)
                    if len(new_email_accounts) > 0:
                        print("These accounts has new emails: ", accounts)
                        get_recent_emails: Callable[[OpenMail], list[Email]] = lambda client: client.imap.get_recent_emails()
                        task_results = execute_openmail_task_concurrently(new_email_accounts, get_recent_emails)
                        await websocket.send_json(task_results)
                        uvicorn_logger.websocket(websocket, task_results)
                except Exception as e:
                    await websocket.close(reason="There was an error while receving new emails.")
                    uvicorn_logger.websocket(websocket, e)
                    break
    except WebSocketDisconnect:
        pass

@app.get("/get-mailboxes/{accounts}")
async def get_mailboxes(
    accounts: str,
    background_tasks: BackgroundTasks,
    folder: Optional[str] = None,
    search: Optional[str] = None,
    offset_start: Optional[int] = None,
    offset_end: Optional[int] = None,
) -> Response[list[OpenMailTaskResult]]:
    try:
        unique_email_addresses = get_unique_email_addresses(accounts)
        response = check_openmail_connection_availability(unique_email_addresses)
        if isinstance(response, Response):
            return response

        # Search emails.
        execute_openmail_task_concurrently(
            unique_email_addresses,
            lambda client, **params: client.imap.search_emails(**params),
            folder=folder,
            search=SearchCriteria.parse_raw(search) if search else None,
        )

        # Fetch and send fetched emails.
        return Response[list[OpenMailTaskResult]](
            success=True,
            message="Emails fetched successfully.",
            data=execute_openmail_task_concurrently(
                unique_email_addresses,
                lambda client, **params: client.imap.get_emails(**params),
                offset_start=offset_start,
                offset_end=offset_end,
            ),
        )
    except Exception as e:
        return Response(success=False, message=err_msg("There was an error while fetching emails.", str(e)))

@app.get("/paginate-mailboxes/{accounts}")
async def paginate_mailboxes(
    accounts: str,
    offset_start: int | None = None,
    offset_end: int | None = None
) -> Response[list[OpenMailTaskResult]]:
    try:
        unique_email_addresses = get_unique_email_addresses(accounts)
        response = check_openmail_connection_availability(unique_email_addresses)
        if isinstance(response, Response):
            return response

        return Response[list[OpenMailTaskResult]](
            success=True,
            message="Emails paginated successfully.",
            data=execute_openmail_task_concurrently(
                unique_email_addresses,
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
        unique_email_addresses = get_unique_email_addresses(accounts)
        response = check_openmail_connection_availability(unique_email_addresses)
        if isinstance(response, Response):
            return response

        return Response[list[OpenMailTaskResult]](
            success=True,
            message="Folders fetched successfully.",
            data=execute_openmail_task_concurrently(
                unique_email_addresses,
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
        response = check_openmail_connection_availability(
            get_unique_email_addresses(account)
        )
        if isinstance(response, Response):
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
        response = check_openmail_connection_availability(
            get_unique_email_addresses(account)
        )
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
    senders: str # list of Name Surname <namesurname@domain.com> or namesurname@domain.com, separated by comma
    receivers: str  # mail addresses separated by comma
    subject: str
    body: str
    uid: Optional[str] = None
    cc: Optional[str] = None # mail addresses separated by comma
    bcc: Optional[str] = None # mail addresses separated by comma
    attachments: list[UploadFile] = []

@app.post("/send-email")
async def send_email(
    form_data: Annotated[SendEmailFormData, Form()]
) -> Response:
    try:
        unique_email_addresses = get_unique_email_addresses(form_data.senders)
        response = check_openmail_connection_availability(unique_email_addresses)
        if isinstance(response, Response):
            return response

        results = execute_openmail_task_concurrently(
            unique_email_addresses,
            lambda client, **params: client.smtp.send_email(
                sender=[
                    sender for sender in form_data.senders.split(",")
                    if cast(str, get_key_by_value(openmail_clients, client)) in sender
                ],
                **params
            ),
            email=Draft(
                receivers=form_data.receivers,
                subject=form_data.subject,
                body=form_data.body,
                cc=form_data.cc,
                bcc=form_data.bcc,
                attachments=await convert_uploadfile_to_attachment(form_data.attachments),
            ),
        )

        # Check results
        success = True
        message = ""
        failed_accounts = []
        if not success:
            for account in results:
                if not account.result:
                    success = False
                    failed_accounts.append(account.email_address)

        message = "Email could not be sent from these accounts: " + ",".join(failed_accounts)
        message = message or "Email sent successfully from all accounts."

        return Response(
            success=success,
            message=message
        )
    except Exception as e:
        return Response(success=False, message=err_msg("There was an error while sending email.", str(e)))


@app.post("/reply-email/{original_message_id}")
async def reply_email(
    original_message_id: str,
    form_data: Annotated[SendEmailFormData, Form()]
) -> Response:
    try:
        unique_email_addresses = get_unique_email_addresses(form_data.senders)
        response = check_openmail_connection_availability(unique_email_addresses)
        if isinstance(response, Response):
            return response

        results = execute_openmail_task_concurrently(
            unique_email_addresses,
            lambda client, **params: client.smtp.reply_email(
                sender=[
                    sender for sender in form_data.senders.split(",")
                    if cast(str, get_key_by_value(openmail_clients, client)) in sender
                ],
                **params
            ),
            email=Draft(
                receivers=form_data.receivers,
                subject=form_data.subject,
                body=form_data.body,
                cc=form_data.cc,
                bcc=form_data.bcc,
                attachments=await convert_uploadfile_to_attachment(form_data.attachments),
            ),
        )

        # Check results
        success = True
        message = ""
        failed_accounts = []
        if not success:
            for account in results:
                if not account.result:
                    success = False
                    failed_accounts.append(account.email_address)

        message = "Email could not be replied from these accounts: " + ",".join(failed_accounts)
        message = message or "Email replied successfully from all accounts."

        return Response(
            success=success,
            message=message
        )
    except Exception as e:
        return Response(success=False, message=err_msg("There was an error while replying email.", str(e)))


@app.post("/forward-email/{original_message_id}")
async def forward_email(
    original_message_id: str,
    form_data: Annotated[SendEmailFormData, Form()]
) -> Response:
    try:
        unique_email_addresses = get_unique_email_addresses(form_data.senders)
        response = check_openmail_connection_availability(unique_email_addresses)
        if isinstance(response, Response):
            return response

        results = execute_openmail_task_concurrently(
            unique_email_addresses,
            lambda client, **params: client.smtp.forward_email(
                sender=[
                    sender for sender in form_data.senders.split(",")
                    if cast(str, get_key_by_value(openmail_clients, client)) in sender
                ],
                **params
            ),
            email=Draft(
                receivers=form_data.receivers,
                subject=form_data.subject,
                body=form_data.body,
                cc=form_data.cc,
                bcc=form_data.bcc,
                attachments=await convert_uploadfile_to_attachment(form_data.attachments),
            ),
        )

        # Check results
        success = True
        message = ""
        failed_accounts = []
        if not success:
            for account in results:
                if not account.result:
                    success = False
                    failed_accounts.append(account.email_address)

        message = "Email could not be forwarded from these accounts: " + ",".join(failed_accounts)
        message = message or "Email forwarded successfully from all accounts."

        return Response(
            success=success,
            message=message
        )
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
        response = check_openmail_connection_availability(
            get_unique_email_addresses(request_body.account)
        )
        if isinstance(response, Response):
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
        response = check_openmail_connection_availability(
            get_unique_email_addresses(request_body.account)
        )
        if isinstance(response, Response):
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
        response = check_openmail_connection_availability(
            get_unique_email_addresses(request_body.account)
        )
        if isinstance(response, Response):
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
        response = check_openmail_connection_availability(
            get_unique_email_addresses(request_body.account)
        )
        if isinstance(response, Response):
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
        response = check_openmail_connection_availability(
            get_unique_email_addresses(request_body.account)
        )
        if isinstance(response, Response):
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
        response = check_openmail_connection_availability(
            get_unique_email_addresses(request_body.account)
        )
        if isinstance(response, Response):
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
        response = check_openmail_connection_availability(
            get_unique_email_addresses(request_body.account)
        )
        if isinstance(response, Response):
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
        response = check_openmail_connection_availability(
            get_unique_email_addresses(request_body.account)
        )
        if isinstance(response, Response):
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
        response = check_openmail_connection_availability(
            get_unique_email_addresses(request_body.account)
        )
        if isinstance(response, Response):
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
