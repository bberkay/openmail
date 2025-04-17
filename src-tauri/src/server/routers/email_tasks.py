import asyncio
from urllib.parse import unquote
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Form, UploadFile
from pydantic import BaseModel
from typing import Optional, Annotated, TypeVar

from ..types import Response
from ..utils import err_msg
from ..internal.account_manager import AccountManager
from ..internal.client_handler import ClientHandler
from ..helpers.uvicorn_logger import UvicornLogger
from ..modules.openmail.types import Email, Mailbox, Folder, Draft, Attachment
from ..modules.openmail.utils import extract_email_address

client_handler = ClientHandler()
account_manager = AccountManager()
uvicorn_logger = UvicornLogger()

T = TypeVar("T")
OpenmailTaskResults = dict[str, T]

NEW_EMAIL_CHECK_INTERVAL_SEC = 60

router = APIRouter(
    tags=["Emails"]
)

def check_openmail_connection_availability(
    account: str,
    for_new_messages: bool = False
) -> Response | bool:
    if client_handler.is_connection_available(account, for_new_messages):
        return True

    return Response(
        success=False,
        message=f'Error, {account} connection is not available or timed out and could not reconnected.'
    )

@router.websocket("/notifications/{account}")
async def notifications_socket(websocket: WebSocket, account: str):
    await websocket.accept()
    uvicorn_logger.websocket(websocket, "New notification subscription created")
    try:
        while True:
            account = extract_email_address(account)
            if client_handler.is_client_exists(account, True):
                response = check_openmail_connection_availability(account, True)
                if isinstance(response, Response):
                    await websocket.close(reason=response.message)
                    uvicorn_logger.websocket(websocket, response.message)
                    break
            else:
                account = account_manager.get(account)
                if account:
                    client_handler.connect_to_account(account, True)
                else:
                    reason = f"There is no account with {account} email address."
                    await websocket.close(reason=reason)
                    uvicorn_logger.websocket(websocket, reason)
                    break

            # Listen for new messages and send notification when
            # any new message received.
            while True:
                try:
                    await asyncio.sleep(NEW_EMAIL_CHECK_INTERVAL_SEC)
                    print(f"Checking for new emails for {account}")
                    openmail_client = client_handler.get_client(account, True)
                    if openmail_client.imap.any_new_email():
                        print(f"Account {account} has new emails")
                        recent_emails = openmail_client.imap.get_recent_emails()
                        await websocket.send_json({account: recent_emails})
                        uvicorn_logger.websocket(websocket, recent_emails)
                except Exception as e:
                    await websocket.close(reason="There was an error while receving new emails.")
                    uvicorn_logger.websocket(websocket, e)
                    break
    except WebSocketDisconnect:
        pass

@router.get("/get-hierarchy-delimiter/{account}")
async def get_hierarchy_delimiter(
    account: str
) -> Response[OpenmailTaskResults[str]]:
    try:
        account = extract_email_address(account)
        response = check_openmail_connection_availability(account)
        if isinstance(response, Response):
            return response

        return Response(
            success=True,
            message="IMAP hierarchy delimiter found successfully.",
            data={account: client_handler.get_client(account).imap.hierarchy_delimiter}
        )
    except Exception as e:
        return Response(success=False, message=err_msg("There was an error while getting IMAP hierarchy delimiter", str(e)))

@router.get("/search-emails/{account}")
async def search_emails(
    account: str,
    folder: Optional[str] = None,
    search: Optional[str] = None,
) -> Response[OpenmailTaskResults[list[str]]]:
    try:
        account = extract_email_address(account)
        response = check_openmail_connection_availability(account)
        if isinstance(response, Response):
            return response

        return Response(
            success=True,
            message="Emails searched successfully.",
            data={account: client_handler.get_client(account).imap.search_emails(folder, search or "")}
        )
    except Exception as e:
        return Response(success=False, message=err_msg("There was an error while searching emails.", str(e)))

@router.get("/get-mailbox/{account}")
async def get_mailbox(
    account: str,
    folder: Optional[str] = None,
    search: Optional[str] = None,
    offset_start: Optional[int] = None,
    offset_end: Optional[int] = None,
) -> Response[OpenmailTaskResults[Mailbox]]:
    try:
        account = extract_email_address(account)
        response = check_openmail_connection_availability(account)
        if isinstance(response, Response):
            return response

        client_handler.get_client(account).imap.search_emails(folder, search or "")

        return Response(
            success=True,
            message="Emails fetched successfully.",
            data={account: client_handler.get_client(account).imap.get_emails(offset_start, offset_end)}
        )
    except Exception as e:
        return Response(success=False, message=err_msg("There was an error while fetching emails.", str(e)))

@router.get("/paginate-mailbox/{account}")
async def paginate_mailbox(
    account: str,
    offset_start: int | None = None,
    offset_end: int | None = None
) -> Response[OpenmailTaskResults[Mailbox]]:
    try:
        account = extract_email_address(account)
        response = check_openmail_connection_availability(account)
        if isinstance(response, Response):
            return response

        return Response(
            success=True,
            message="Emails paginated successfully.",
            data={account: client_handler.get_client(account).imap.get_emails(offset_start, offset_end)}
        )
    except Exception as e:
        return Response(success=False, message=err_msg("There was an error while paginating emails.", str(e)))

@router.get("/get-folders/{account}")
async def get_folders(
    account: str,
) -> Response[OpenmailTaskResults[list[str]]]:
    try:
        account = extract_email_address(account)
        response = check_openmail_connection_availability(account)
        if isinstance(response, Response):
            return response

        return Response(
            success=True,
            message="Folders fetched successfully.",
            data={account: client_handler.get_client(account).imap.get_folders(tagged=True)}
        )
    except Exception as e:
        return Response(success=False, message=err_msg("There was an error while fetching folders.", str(e)))

@router.get("/get-email-content/{account}/{folder}/{uid}")
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
            data=client_handler.get_client(account).imap.get_email_content(unquote(folder), uid)
        )
    except Exception as e:
        return Response(success=False, message=err_msg("There was an error while fetching email content.", str(e)))

@router.get("/download-attachment/{account}/{folder}/{uid}/{name}")
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
            data=client_handler.get_client(account).imap.download_attachment(
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

@router.post("/send-email")
async def send_email(
    form_data: Annotated[SendEmailFormData, Form()],
) -> Response:
    try:
        account = extract_email_address(form_data.sender)
        response = check_openmail_connection_availability(account)
        if isinstance(response, Response):
            return response

        status, msg = client_handler.get_client(account).smtp.send_email(
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


@router.post("/reply-email/{original_message_id}")
async def reply_email(
    original_message_id: str,
    form_data: Annotated[SendEmailFormData, Form()]
) -> Response:
    try:
        account = extract_email_address(form_data.sender)
        response = check_openmail_connection_availability(account)
        if isinstance(response, Response):
            return response

        status, msg = client_handler.get_client(account).smtp.reply_email(
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


@router.post("/forward-email/{original_message_id}")
async def forward_email(
    original_message_id: str,
    form_data: Annotated[SendEmailFormData, Form()]
) -> Response:
    try:
        account = extract_email_address(form_data.sender)
        response = check_openmail_connection_availability(account)
        if isinstance(response, Response):
            return response

        status, msg = client_handler.get_client(account).smtp.forward_email(
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

@router.post("/save-email-as-draft")
async def save_email_as_draft(
    form_data: Annotated[SendEmailFormData, Form()],
    appenduid: str | None = None
) -> Response:
    try:
        account = extract_email_address(form_data.sender)
        response = check_openmail_connection_availability(account)
        if isinstance(response, Response):
            return response

        appenduid = client_handler.get_client(account).imap.save_email_as_draft(
            client_handler.get_client(account).smtp.create_email(Draft(
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


@router.post("/mark-email")
async def mark_email(request_body: MarkEmailRequest) -> Response:
    try:
        account = extract_email_address(request_body.account)
        response = check_openmail_connection_availability(account)
        if isinstance(response, Response):
            return response

        status, msg = client_handler.get_client(account).imap.mark_email(
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


@router.post("/unmark-email")
async def unmark_email(request_body: UnmarkEmailRequest) -> Response:
    try:
        account = extract_email_address(request_body.account)
        response = check_openmail_connection_availability(account)
        if isinstance(response, Response):
            return response

        status, msg = client_handler.get_client(account).imap.unmark_email(
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


@router.post("/move-email")
async def move_email(request_body: MoveEmailRequest) -> Response:
    try:
        account = extract_email_address(request_body.account)
        response = check_openmail_connection_availability(account)
        if isinstance(response, Response):
            return response

        status, msg = client_handler.get_client(account).imap.move_email(
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


@router.post("/copy-email")
async def copy_email(request_body: CopyEmailRequest) -> Response:
    try:
        account = extract_email_address(request_body.account)
        response = check_openmail_connection_availability(account)
        if isinstance(response, Response):
            return response

        status, msg = client_handler.get_client(account).imap.copy_email(
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


@router.post("/delete-email")
async def delete_email(request_body: DeleteEmailRequest) -> Response:
    try:
        account = extract_email_address(request_body.account)
        response = check_openmail_connection_availability(account)
        if isinstance(response, Response):
            return response

        status, msg = client_handler.get_client(account).imap.delete_email(
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


@router.post("/create-folder")
async def create_folder(request_body: CreateFolderRequest) -> Response:
    try:
        account = extract_email_address(request_body.account)
        response = check_openmail_connection_availability(account)
        if isinstance(response, Response):
            return response

        status, msg = client_handler.get_client(account).imap.create_folder(
            request_body.folder_name, request_body.parent_folder
        )
        return Response(success=status, message=msg)
    except Exception as e:
        return Response(success=False, message=err_msg("There was an error while creating folder.", str(e)))


class RenameFolderRequest(BaseModel):
    account: str
    folder_name: str
    new_folder_name: str


@router.post("/rename-folder")
async def rename_folder(request_body: RenameFolderRequest) -> Response:
    try:
        account = extract_email_address(request_body.account)
        response = check_openmail_connection_availability(account)
        if isinstance(response, Response):
            return response

        status, msg = client_handler.get_client(account).imap.rename_folder(
            request_body.folder_name, request_body.new_folder_name
        )
        return Response(success=status, message=msg)
    except Exception as e:
        return Response(success=False, message=err_msg("There was an error while renaming folder.", str(e)))


class MoveFolderRequest(BaseModel):
    account: str
    folder_name: str
    destination_folder: str


@router.post("/move-folder")
async def move_folder(request_body: MoveFolderRequest) -> Response:
    try:
        account = extract_email_address(request_body.account)
        response = check_openmail_connection_availability(account)
        if isinstance(response, Response):
            return response

        status, msg = client_handler.get_client(account).imap.move_folder(
            request_body.folder_name, request_body.destination_folder
        )
        return Response(success=status, message=msg)
    except Exception as e:
        return Response(success=False, message=err_msg("There was an error while moving folder.", str(e)))


class DeleteFolderRequest(BaseModel):
    account: str
    folder_name: str
    delete_subfolders: bool

@router.post("/delete-folder")
async def delete_folder(request_body: DeleteFolderRequest) -> Response:
    try:
        account = extract_email_address(request_body.account)
        response = check_openmail_connection_availability(account)
        if isinstance(response, Response):
            return response

        status, msg = client_handler.get_client(account).imap.delete_folder(
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

@router.post("/unsubscribe-email")
async def unsubscribe_email(request_body: UnsubscribeEmailRequest) -> Response:
    try:
        account = extract_email_address(request_body.account)
        response = check_openmail_connection_availability(account)
        if isinstance(response, Response):
            return response

        status, msg = client_handler.get_client(account).smtp.unsubscribe(
            request_body.account,
            request_body.list_unsubscribe,
            request_body.list_unsubscribe_post
        )
        return Response(success=status, message=msg)
    except Exception as e:
        return Response(success=False, message=err_msg("There was an error while unsubscribing.", str(e)))

__all__ = ["router"]

"""
Execute openmail tasks with threading module:

def execute_openmail_task_concurrently(
    accounts: set[str], # unique email addresses
    func: Callable[...],
    **params
) -> OpenmailTaskResults:
    result: OpenmailTaskResults = {}
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
