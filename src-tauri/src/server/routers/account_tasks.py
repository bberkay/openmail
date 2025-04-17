from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, cast

from ..types import Response
from ..utils import err_msg, is_email_valid
from ..modules.openmail import Openmail
from ..internal.account_manager import AccountManager, Account, AccountWithPassword
from ..internal.secure_storage import SecureStorage, SecureStorageKey, RSACipher, SecureStorageKeyValue
from ..internal.client_handler import ClientHandler

client_handler = ClientHandler()
secure_storage = SecureStorage()
account_manager = AccountManager()

router = APIRouter(
    tags=["Accounts"]
)

class GetPublicKeyData(BaseModel):
    public_key: str

@router.get("/get-public-key")
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

@router.get("/get-accounts")
def get_accounts() -> Response[GetAccountsData]:
    try:
        all_accounts = account_manager.get_all(include_passwords=False)
        connected_accounts = []
        failed_accounts =[]
        if all_accounts:
            email_to_account = {account.email_address: account for account in all_accounts}
            connected_accounts = [email_to_account[email_address] for email_address in client_handler.get_clients().keys()]
            failed_accounts = [email_to_account[email_address] for email_address in client_handler.get_failed_clients()]

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

@router.post("/add-account")
def add_account(request: AddAccountRequest) -> Response:
    if not is_email_valid(request.email_address):
        return Response(success=False, message="Invalid email address format")

    try:
        if account_manager.is_exists(request.email_address):
            return Response(success=False, message="Email address already exists")

        openmail_client = Openmail()

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

        client_handler.add_client(request.email_address, openmail_client)
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

@router.put("/edit-account")
def edit_account(request: EditAccountRequest) -> Response:
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
            openmail_client = Openmail()
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

            client_handler.add_client(request.email_address, openmail_client)
        return Response(
            success=True,
            message="Account successfully edited"
        )
    except Exception as e:
        return Response(success=False, message=err_msg("Failed to add email.", str(e)))

class RemoveAccountRequest(BaseModel):
    account: str

@router.delete("/remove-account")
def remove_email_account(request_body: RemoveAccountRequest) -> Response:
    try:
        account_manager.remove(request_body.account)
        return Response(success=True, message="Account removed successfully")
    except Exception as e:
        return Response(success=False, message=err_msg("There was an error while removing account.", str(e)))


@router.delete("/remove-accounts")
def remove_accounts() -> Response:
    try:
        account_manager.remove_all()
        return Response(success=True, message="All accounts removed successfully")
    except Exception as e:
        return Response(success=False, message=err_msg("There was an error while removing accounts.", str(e)))

__all__ = ["router"]
