import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import cast

from .account_manager import AccountManager, AccountWithPassword
from .secure_storage import (
    SecureStorage,
    SecureStorageKey,
    RSACipher,
    SecureStorageKeyValue,
)
from ..helpers.uvicorn_logger import UvicornLogger
from ..modules.openmail import Openmail

uvicorn_logger = UvicornLogger()
secure_storage = SecureStorage()
account_manager = AccountManager()

type OpenmailClients = dict[str, Openmail]
type FailedOpenmailClients = list[str]

MAX_TASK_WORKER = 5
IMAP_LOGGED_OUT_INTERVAL = 60

openmail_clients: OpenmailClients = {}
failed_openmail_clients: list[str] = []
openmail_clients_for_new_messages: OpenmailClients = {}


class ClientHandler:
    _instance = None
    _monitor_logged_out_clients_task = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._monitor_logged_out_clients_task = None

        return cls._instance

    def create_openmail_clients(self):
        try:
            print("Openmail clients are creating...")
            accounts: list[AccountWithPassword] = cast(
                list[AccountWithPassword], account_manager.get_all()
            )
            if not accounts:
                return

            with ThreadPoolExecutor(max_workers=MAX_TASK_WORKER) as executor:
                executor.map(self.connect_to_account, accounts)
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

    def is_connection_available(
        self, account: str, for_new_messages: bool = False
    ) -> bool:
        target_openmail_clients = (
            openmail_clients_for_new_messages if for_new_messages else openmail_clients
        )

        if not target_openmail_clients[account].imap.is_logged_out():
            print(f"No need to reconnect for {account}")
            return True

        self.reconnect_to_account(account, for_new_messages)

        if not target_openmail_clients[account].imap.is_logged_out():
            print(f"No need to reconnect for {account}")
            return True

        return False

    def add_client(self, account: str, client: Openmail):
        openmail_clients[account] = client
        try:
            failed_openmail_clients.remove(account)
        except ValueError:
            pass

    def get_client(self, account: str, for_new_messages: bool = False) -> Openmail:
        return openmail_clients[account]

    def get_clients(self) -> OpenmailClients:
        return openmail_clients

    def get_failed_clients(self) -> FailedOpenmailClients:
        return failed_openmail_clients

    def is_client_exists(self, account: str, for_new_messages: bool = False) -> bool:
        if for_new_messages:
            return account in openmail_clients_for_new_messages
        else:
            return account in openmail_clients

    def connect_to_account(
        self, account: AccountWithPassword, for_new_messages: bool = False
    ):
        print(f"Connecting to {account.email_address}...")
        target_openmail_clients = (
            openmail_clients_for_new_messages if for_new_messages else openmail_clients
        )
        target_failed_openmail_clients = (
            None if for_new_messages else failed_openmail_clients
        )
        try:
            target_openmail_clients[account.email_address] = Openmail()
            status, _ = target_openmail_clients[account.email_address].connect(
                account.email_address,
                RSACipher.decrypt_password(
                    account.encrypted_password,
                    cast(
                        SecureStorageKeyValue,
                        secure_storage.get_key_value(SecureStorageKey.PrivatePem),
                    )["value"],
                ),
                imap_enable_idle_optimization=True,
                imap_listen_new_messages=for_new_messages,
            )
            if status:
                print(f"Successfully connected to {account.email_address}")
                # TODO: Open this later.
                # target_openmail_clients[account.email_address].imap.idle()
                try:
                    if target_failed_openmail_clients:
                        target_failed_openmail_clients.remove(account.email_address)
                except ValueError:
                    pass
            else:
                print(f"Could not successfully connected to {account.email_address}.")
                del target_openmail_clients[account.email_address]
                if target_failed_openmail_clients:
                    target_failed_openmail_clients.append(account.email_address)
        except Exception as e:
            del target_openmail_clients[account.email_address]
            if target_failed_openmail_clients:
                target_failed_openmail_clients.append(account.email_address)
            uvicorn_logger.error(
                f"Failed while connecting to {account.email_address}: {e}"
            )

    def reconnect_to_account(self, email_address: str, for_new_messages: bool = False):
        print(f"Reconnecton for {email_address}...")
        target_openmail_clients = (
            openmail_clients_for_new_messages if for_new_messages else openmail_clients
        )
        target_failed_openmail_clients = (
            None if for_new_messages else failed_openmail_clients
        )
        try:
            created_openmail_clients = target_openmail_clients.keys()
            if email_address not in created_openmail_clients:
                return

            if not target_openmail_clients[email_address].imap.is_logged_out():
                print(f"No need to reconnect for {email_address}")
                return

            account = account_manager.get(email_address)
            if account:
                self.connect_to_account(account, for_new_messages)
            else:
                print(f"{email_address} could not found while trying to reconnect.")
        except Exception as e:
            del target_openmail_clients[email_address]
            if target_failed_openmail_clients:
                target_failed_openmail_clients.append(email_address)
            uvicorn_logger.error(f"Failed while reconnecting to {email_address}: {e}")

    def reconnect_logged_out_openmail_clients(self):
        print(
            "Reconnecting to Openmail clients...",
        )
        with ThreadPoolExecutor(max_workers=MAX_TASK_WORKER) as executor:
            for email_address, client in openmail_clients.items():
                executor.submit(self.reconnect_to_account, email_address, False)
            for email_address, client in openmail_clients_for_new_messages.items():
                executor.submit(self.reconnect_to_account, email_address, True)

    async def monitor_logged_out_openmail_clients(self):
        try:
            while True:
                await asyncio.sleep(IMAP_LOGGED_OUT_INTERVAL)
                print("Checking logged out Openmail clients...")
                self.reconnect_logged_out_openmail_clients()
        except asyncio.CancelledError:
            uvicorn_logger.info(
                "Monitoring logged out clients task is being cancelled..."
            )
            raise

    def _shutdown_openmail_clients(self):
        try:
            uvicorn_logger.info("Shutting down openmail clients...")
            with ThreadPoolExecutor(max_workers=MAX_TASK_WORKER) as executor:
                for clients in [openmail_clients, openmail_clients_for_new_messages]:
                    executor.map(lambda client: client[1].disconnect(), clients.items())
        except Exception as e:
            uvicorn_logger.error(f"Openmail clients could not properly terminated: {e}")

    def _shutdown_monitors(self):
        if self.__class__._monitor_logged_out_clients_task:
            self.__class__._monitor_logged_out_clients_task.cancel()

    def shutdown(self):
        uvicorn_logger.info(
            "Shutdown signal received. Starting to logging out and terminating threads..."
        )
        try:
            self._shutdown_openmail_clients()
            self._shutdown_monitors()
        except Exception:
            uvicorn_logger.error("Shutdown could not properly executed.")


__all__ = ["ClientHandler"]
