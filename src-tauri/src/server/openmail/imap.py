"""
IMAPManager
This module extends the functionality of the 
`imaplib.IMAP4_SSL` class to simplify its usage and 
add new features.

Key features include:
- Automated server selection based on email domain.
- Support for idling and event-driven response handling on separate threads.
- New abstractions for managing email folders, marks, and search criteria.
- Built-in utility methods for email parsing, attachment handling, and UTF-8 compatibility.
- Custom error handling and logging.

Primarily designed for use by the `OpenMail` class.

Author: <berkaykayaforbusiness@outlook.com>
License: MIT
"""
import imaplib
import email
import threading
import re
import base64
import time

from typing import List, override
from types import MappingProxyType
from datetime import datetime
from enum import Enum

from .parser import MessageParser
from .utils import extract_domain, choose_positive
from .utils import truncate_text, contains_non_ascii, make_size_human_readable
from .types import SearchCriteria, Attachment, Mailbox, EmailSummary, EmailWithContent

# Exceptions
class IMAPManagerException(Exception):
    """Custom exception for IMAPManager class."""

class IMAPManagerLoggedOutException(IMAPManagerException):
    """Custom exception for when the IMAPManager is logged out
    while trying to perform an action that requires authentication."""

# Enums
class WaitResponse(Enum):
    """Enum for waiting for a response from the server."""
    # These are not the all possible responses but the ones we are interested in
    # IDLE, DONE: https://datatracker.ietf.org/doc/html/rfc9051#name-idle-command
    # EXISTS: https://datatracker.ietf.org/doc/html/rfc9051#name-exists-response
    # BYE: https://datatracker.ietf.org/doc/html/rfc9051#name-bye-response
    IDLE = "IDLE"
    DONE = "DONE"
    EXISTS = "EXISTS"
    BYE = "BYE"

# https://datatracker.ietf.org/doc/html/rfc9051#name-flags-message-attribute
class Mark(Enum):
    """Enum for email marks."""
    FLAGGED = "\\Flagged"
    SEEN = "\\Seen"
    ANSWERED = "\\Answered"
    #deleted = "\\Deleted"
    #draft = "\\Draft"
    #spam = "\\Spam"

# https://datatracker.ietf.org/doc/html/rfc6154#autoid-3
class Folder(Enum):
    """Enum for email folders."""
    Inbox = b'\\Inbox'
    All = b'\\All'
    Archive = b'\\Archive'
    Drafts = b'\\Drafts'
    Flagged = b'\\Flagged'
    Junk = b'\\Junk'
    Sent = b'\\Sent'
    Trash = b'\\Trash'

# Types
type IMAPCommandResult = tuple[bool, str]

# General consts, avoid changing
IMAP_SERVERS = MappingProxyType({
    "gmail": "imap.gmail.com",
    "yahoo": "imap.mail.yahoo.com",
    "outlook": "outlook.office365.com",
    "hotmail": "outlook.office365.com",
    'yandex': 'imap.yandex.com',
})
IMAP_PORT = 993
# https://datatracker.ietf.org/doc/html/rfc9051#name-state-and-flow-diagram
IMAP_STATES = ('NONAUTH', 'AUTH', 'SELECTED', 'LOGOUT')
INBOX = 'INBOX'
ALL = 'ALL'

# Regular expressions
INLINE_ATTACHMENT_PATTERN = re.compile(r'<img src="cid:([^"]+)"')

# Custom consts
BODY_SHORT_THRESHOLD = 50
MAX_FOLDER_NAME_LENGTH = 100
DEFAULT_CONN_TIMEOUT = 30 # 30 seconds
DEFAULT_IDLE_TIMEOUT = 30 * 60 # 30 minutes
DEFAULT_WAIT_RESPONSE_TIMEOUT = 3 * 60 # 3 minutes

class IMAPManager(imaplib.IMAP4_SSL):
    """
    IMAPManager extends the `imaplib.IMAP4` class.
    Does not override any methods except `login`, `logout`
    and `__simple_command`. Provides additional features 
    especially idling and listening exists responses on 
    different threads. Mainly used in `OpenMail` class.
    """
    def __init__(
        self,
        email_address: str,
        password: str,
        host: str = "",
        port: int = IMAP_PORT,
        ssl_context: any = None,
        timeout: int = DEFAULT_CONN_TIMEOUT
    ):
        super().__init__(
            host or self.__find_imap_server(email_address),
            port or IMAP_PORT,
            ssl_context=ssl_context,
            timeout=choose_positive(timeout, DEFAULT_CONN_TIMEOUT)
        )

        self.login(email_address, password)

        self.__current_folder = (INBOX, False)

        # IDLE - READLINE Handling
        self.__is_idle = False
        self.__current_idle_start_time = None
        self.__current_idle_tag = None
        self.__wait_for_response = None

        self.__idle_thread_event = None
        self.__idle_thread = None

        self.__readline_thread_event = None
        self.__readline_thread = None


    def __find_imap_server(self, email_address: str) -> str:
        """
        Determines the IMAP server address for a given email address.

        Args:
            email_address (str): The email address for which to find the 
            corresponding IMAP server.

        Returns:
            str: The IMAP server address associated with the email's domain.

        Raises:
            IMAPManagerException: If the email domain is not supported or 
            not found in the IMAP_SERVERS mapping.

        Example:
            >>> email_address = "user@gmail.com"
            >>> self.__find_imap_server(email_address)
            "imap.gmail.com"

            >>> email_address = "user@unknown.com"
            >>> self.__find_imap_server(email_address)
            IMAPManagerException: Unsupported email domain
        """
        try:
            return IMAP_SERVERS[extract_domain(email_address)]
        except KeyError as e:
            raise IMAPManagerException(f"Unsupported email domain: {str(e)}") from e

    @override
    def login(self, user: str, password: str) -> IMAPCommandResult:
        """
        Authenticates the user with the IMAP server using the provided credentials.

        Args:
            user (str): The username or email address of the account.
            password (str): The account's password.

        Returns:
            IMAPCommandResult: A tuple containing:
                - True
                - A string containing a success message.

        Raises:
            IMAPManagerException: If the login process fails.

        Notes:
            - UTF-8 encoding is enabled after successful authentication.
            - Supports both ASCII and non-ASCII credentials.
        """
        try:
            if contains_non_ascii(user) or contains_non_ascii(password):
                self.authenticate(
                    "PLAIN", 
                    lambda x: bytes("\x00" + user + "\x00" + password, "utf-8")
                )
            else:
                super().login(user, password)
        except imaplib.IMAP4.error as e:
            raise IMAPManagerException(f"There was an error while logging in: {str(e)}") from None

        try:
            result = self._simple_command('ENABLE', 'UTF8=ACCEPT')
            if result[0] != 'OK':
                print(f"Could not enable UTF-8: {result[1]}")
        except Exception as e:
            print(f"Unexpected error: Could not enable UTF-8: {str(e)}")
            pass

        return (True, "Succesfully logged in to the target IMAP server")

    @override
    def logout(self) -> IMAPCommandResult:
        """
        Logs out from the IMAP server and closes any open mailboxes.

        Returns:
            IMAPCommandResult: A tuple containing:
                - A bool indicating whether the logout was successful.
                - A string containing a success message or an error message.

        Notes:
            - If the state is "SELECTED," the mailbox is closed before disconnecting.
            If there is an error while closing the mailbox, it will be logged but not 
            raised.
        """
        try:
            if self.state == "SELECTED":
                result = self.__parse_command_result(self.close())
                if not result[0]:
                    print(f"Could not close mailbox: {result[1]}")
        except Exception as e:
            print(f"Unexpected Error: Could not close mailbox: {str(e)}")
            pass

        try:
            result = super().logout()
        except Exception as e:
            raise IMAPManagerException(f"Could not logout from the target imap server: {str(e)}") from None

        return self.__parse_command_result(
            result,
            success_message="Logout successful",
            failure_message="Could not logout from the target imap server"
        )

    @override
    def _simple_command(self, name, *args):
        """
        Overrides the _simple_command method to handle continuous IDLE mode and
        raise IMAPManagerLoggedOutException if the IMAPManager is logged out because
        of timeout.
        """

        def is_logged_out(err_msg: str) -> bool:
            """
            Checks if the error message contains the keywords "AUTH" or "SELECTED" to determine if 
            the IMAPManager is logged out.    

            Args:
                err_msg (str): The error message to check.

            Returns:
                bool: True if self.state is "LOGOUT" and the error message contains "AUTH" or 
                "SELECTED", False otherwise.
            """
            return self.state == "LOGOUT" and any(
                item.lower() in err_msg for item in ("AUTH", "SELECTED")
            )

        # Leaving IDLE mode if needed
        try:
            was_idle_before_call = self.__is_idle
            if was_idle_before_call:
                self.done()
        except Exception as e:
            if is_logged_out(str(e).lower()):
                raise IMAPManagerLoggedOutException(
                    f"To perform this action, the IMAPManager must be logged in: {str(e)}"
                ) from None
            else:
                print(f"Unexpected error while leaving IDLE mode: {str(e)}")
                # Even if leaving IDLE failed, set idle and readline threads and set
                # __is_idle to False.
                self.__handle_done_response()
                print("Active IDLE status set to False and threads stopped forcefully.")

        # Run wanted command.
        try:
            result = super()._simple_command(name, args)
        except Exception as e:
            if is_logged_out(str(e).lower()):
                raise IMAPManagerLoggedOutException(
                    f"To perform this action, the IMAPManager must be logged in: {str(e)}"
                ) from None
            else:
                raise IMAPManagerException(str(e)) from None

        # Restoring IDLE mode
        try:
            if was_idle_before_call:
                self.idle()
            return result
        except Exception as e:
            print(f"Unexpected error while restoring IDLE mode: {str(e)}")
            was_idle_before_call = False
            print("IDLE mode could not be restored. IDLE mode completely disabled. Run `idle()` to re-enable IDLE mode if needed.")
            raise IMAPManagerException(str(e)) from None

    def __parse_command_result(self,
        result: tuple[str, list[bytes | None]],
        success_message: str = None,
        failure_message: str = None
    ) -> IMAPCommandResult:
        """
        Parses the result of an IMAP command and returns a structured response.

        Args:
            result (tuple[str, list[bytes | None]]): 
                The command result, where:
                - The first element is the status ("OK", "NO", etc.).
                - The second element is a list containing additional response data.
            success_message (str, optional): 
                A custom success message to include in the response. Will override the 
                default success message. If not provided, the default success message will 
                be used.
            failure_message (str, optional): 
                A custom failure message to include in the response. Will be added at the
                start of the failure message if provided.

        Returns:
            IMAPCommandResult: A tuple containing:
                - A boolean indicating success (True for "OK", False otherwise).
                - The server's response message as a string.

        Raises:
            IMAPManagerException: If parsing the command result fails.

        Example:
            >>> result = ("OK", [b"Command completed successfully"])
            >>> self.__parse_command_result(result, 
                    success_message="Operation successful", 
                    failure_message="Login failed"
                )
            (True, "Operation successful")

            >>> result = ("NO", [b"Invalid credentials"])
            >>> self.__parse_command_result(result, 
                    success_message="Operation successful", 
                    failure_message="Login failed"
                )
            (False, "Login failed: Invalid credentials")

            >>> result = ("BYE", [b"Logout successful"])
            >>> self.__parse_command_result(result, 
                    success_message="Operation successful", 
                    failure_message="Logout failed"
                )
            (True, "Logout successful")

        Notes:
            - If the first element of the result is "BYE", it is considered 
            a logout command and will be searching for a "logout" in the
            result message like in the example. 
        """
        try:
            if result[0] == "OK" or (result[0] == "BYE" and b"logout" in result[1][0].lower()):
                return True, success_message or result[1][0].decode("utf-8")
            else:
                return False, failure_message + ": " + result[1][0].decode("utf-8")
        except Exception as e:
            raise IMAPManagerException(f"There was an error while parsing command result: {str(e)}") from None

    def __ensure_command(self, response: tuple[str, list[bytes | None]]):
        """
        Ensures an IMAP command was successful.

        Args:
            response (tuple[str, list[bytes | None]]): 
                The command response, where the first element is the status 
                (e.g., "OK") and the second contains additional data.

        Raises:
            IMAPManagerException: If the response status is not "OK."
        """
        try:
            if response[0] != "OK":
                raise IMAPManagerException(f"IMAP command failed: {response[1][0].decode("utf-8")}")
        except imaplib.IMAP4.error as e:
            raise IMAPManagerException(f"There was an error while ensuring command: {str(e)}") from None

    def idle(self) -> None:
        """
        Initiates the IMAP IDLE command to start monitoring changes 
        in the mailbox on its own thread. If already in IDLE mode, 
        does nothing.
        """
        if not self.__is_idle:
            self.select_folder(INBOX)
            self.__current_idle_tag = self._new_tag()
            self.send(b"%s IDLE\r\n" % self.__current_idle_tag)
            print(f"'IDLE' command sent with tag: {self.__current_idle_tag} at {datetime.now()}.")
            self.__readline()
            self.__wait_response(WaitResponse.IDLE)

    def done(self) -> None:
        """
        Terminates the current IDLE session if active.
        """
        if self.__is_idle:
            self.send(b"DONE\r\n")
            print(f"DONE command sent for {self.__current_idle_tag} at {datetime.now()}.")
            self.__wait_response(WaitResponse.DONE)

    def __wait_response(self, wait_response: WaitResponse) -> None:
        """
        Waits for a specific response type from the IMAP server.
        
        Args:
            wait_response (WaitResponse): Expected response type to wait for
            
        Times out after DEFAULT_WAIT_RESPONSE_TIMEOUT seconds and resets wait state.
        """
        counter = 0
        while self.__wait_for_response != wait_response:
            time.sleep(1)
            counter += 1
            if counter > DEFAULT_WAIT_RESPONSE_TIMEOUT:
                print(f"WaitResponse: {wait_response} did not received in time at {datetime.now()}. WaitResponse set to None")
                break

        self.__wait_for_response = None

    def __idle(self) -> None:
        """
        Background thread handler for IDLE mode monitoring.

        Continuously checks IDLE session duration and automatically 
        refreshes the connection when DEFAULT_IDLE_TIMEOUT is reached.
        """
        while not self.__idle_thread_event.is_set():
            print(f"IDLING for {self.__current_idle_tag} started at {datetime.now()}.")
            time.sleep(1)
            if time.time() - self.__current_idle_start_time > DEFAULT_IDLE_TIMEOUT:
                print(f"IDLING timeout reached for {self.__current_idle_tag} at {datetime.now()}.")
                self.done()
                self.idle()

    def __readline(self) -> None:
        """
        Initializes and manages the response reading thread.
        
        Creates a new thread for continuously reading server responses
        if one doesn't exist or isn't active. Processes responses through
        the handle_response method.
        """
        def readline_thread() -> None:
            """
            Continuously reads server responses and processes them.
            """
            while not self.__readline_thread_event.is_set():
                response = self.readline()
                if response:
                    print(f"New response received: {response} at {datetime.now()}. Handling response...")
                    self.__handle_response(response)
                time.sleep(1)

        if not self.__readline_thread_event:
            self.__readline_thread_event = threading.Event()
        self.__readline_thread_event.clear()

        if not self.__readline_thread or not self.__readline_thread.is_alive():
            self.__readline_thread = threading.Thread(target=readline_thread)
            self.__readline_thread.start()

    def __handle_idle_response(self) -> None:
        """
        Handles the server's response to the IDLE command.
        Marks the client as being in the IDLE state, sets 
        start time, and starts the IDLE monitoring thread.
        """
        print(f"'IDLE' response received for {self.__current_idle_tag} at {datetime.now()}.")
        self.__is_idle = True
        self.__current_idle_start_time = time.time()

        if not self.__idle_thread_event:
            self.__idle_thread_event = threading.Event()
        self.__idle_thread_event.clear()

        if not self.__idle_thread or not self.__idle_thread.is_alive():
            self.__idle_thread = threading.Thread(target=self.__idle)
            self.__idle_thread.start()

        self.__wait_for_response = WaitResponse.IDLE
        print(f"'IDLE' response for {self.__current_idle_tag} handled, IDLE thread started at {self.__current_idle_start_time}.")

    def __handle_done_response(self) -> None:
        """
        Handles the server's response to the DONE command.
        Marks the client as no longer in the IDLE state 
        and stops the IDLE monitoring thread.
        """
        print(f"'DONE' response received for {self.__current_idle_tag} at {datetime.now()}.")
        self.__is_idle = False
        self.__current_idle_tag = None

        self.__idle_thread_event.set()
        self.__readline_thread_event.set()

        self.__wait_for_response = WaitResponse.DONE
        print(
            f"'DONE' response for {self.__current_idle_tag} handled, IDLE thread stopped at {datetime.now()}."
        )

    def __handle_bye_response(self):
        """
        Handles the server's 'BYE' response, which indicates the server 
        is closing the connection. Safely terminates the connection, stops 
        threads, and raises an exception to signal the logout event.
        """
        print(f"'BYE' response received from server at {datetime.now()}.")
        self.__wait_for_response = WaitResponse.BYE
        self.__readline_thread_event.set()
        self.__idle_thread_event.set()
        self.__is_idle = False
        self.__current_idle_tag = None
        self.close()
        raise IMAPManagerLoggedOutException(f"'BYE' response received from server at {datetime.now()}. IMAPManager connection closed safely.") from None

    def __handle_exists_response(self, response: bytes):
        """
        Handles the 'EXISTS' response from the server, which indicates the 
        number of messages in the mailbox. Updates internal state or performs 
        necessary actions based on the response.
    
        Args:
            response (bytes): The server's EXISTS response data.
        """
        print(f"'EXISTS' response received from server at {datetime.now()}.")
        self.__wait_for_response = WaitResponse.EXISTS
        # TODO: Implement handling of EXISTS response
        pass

    def __handle_response(self, response: bytes):
        """
        Determines the type of server response and delegates handling to the 
        appropriate method.

        Args:
            response (bytes): The raw server response to be processed.
        """
        if b'idling' in response:
            self.__handle_idle_response()
        elif b'OK' in response and bytes(self.__current_idle_tag) in response:
            self.__handle_done_response()
        elif b'BYE' in response:
            self.__handle_bye_response()
        elif b'EXISTS' in response:
            self.__handle_exists_response(response)

    def find_matching_folder(self, requested_folder: Folder) -> bytes | None:
        """
        Retrieve the IMAP folder name matching a specific byte string.

        This method is useful for handling cases where a client's folder names 
        are localized in a different language.

        Args:
            some_param_name (bytes): The IMAP folder name (e.g., `b'\\Inbox'` or `b'\\Trash'`).

        Returns:
            bytes | None: The folder name in bytes if a match is found; otherwise, None.

        Example:
            >>> find_matching_folder(b'\\Inbox')
            b'INBOX'

            >>> find_matching_folder(b'\\Trash')
            b'Çöp Kutusu' # Means "Trash" in Turkish
        """
        folder_list = [m.value for m in Folder]
        if requested_folder not in folder_list:
            raise IMAPManagerException(f"Invalid folder name: {requested_folder}. Please use one of the following: {folder_list}")

        status, folders_as_bytes = self.list()
        if status == "OK" and folders_as_bytes and isinstance(folders_as_bytes, list):
            for folder_as_bytes in folders_as_bytes:
                if requested_folder == folder_as_bytes:
                    return folder_as_bytes
        return None

    def __encode_folder(self, folder: str) -> bytes:
        """
        Encode a folder name into a byte string suitable for IMAP operations.

        Args:
            folder (str): The name of the folder to encode.

        Returns:
            bytes: The encoded folder name in UTF-8 format.

        Raises:
            IMAPManagerException: If encoding the folder name fails.
        """
        try:
            return ('"' + folder + '"').encode("utf-8")
        except Exception as e:
            raise IMAPManagerException(f"Error while encoding folder name: {str(e)}") from None

    def __decode_folder(self, folder: bytes) -> str:
        """
        Decode a folder name from a byte string returned by an IMAP server.

        Args:
            folder (bytes): The byte string containing the folder name.

        Returns:
            str: The decoded and cleaned folder name.

        Raises:
            IMAPManagerException: If decoding the folder name fails.
        """
        try:
            # Most of the servers return folder name as b'(\\HasNoChildren) "/" "INBOX"'
            # But some servers like yandex return folder name as b'(\\HasNoChildren) "|" "INBOX"'
            # So we're replacing "|" with "/" to make it consistent
            return folder.decode().replace(' "|" ', ' "/" ').split(' "/" ')[1].replace('"', '')
        except Exception as e:
            raise IMAPManagerException(f"Error while decoding folder name: {str(e)}.") from None

    def __check_folder_names(self, folders: str | List[str], raise_error: bool = True) -> bool:
        """
        Check if a folder name(s) is valid.

        Args:
            folders (str | List[str]): Folder name or list of folder names
            raise_error (bool, optional): If True, raise an error if the folder name is invalid. 
                                          Default is True

        Returns:
            bool: True if folder name is valid, False otherwise

        Raises:
            IMAPManagerException: If the folder name is invalid and raise_error is True
        """
        if isinstance(folders, str):
            folders = [folders]

        for folder_name in folders:
            folder_name_length = len(folder_name)
            if folder_name is None or folder_name == "" or folder_name_length > MAX_FOLDER_NAME_LENGTH or folder_name_length < 1:
                if raise_error:
                    raise IMAPManagerException(f"Invalid folder name: {folder_name}")
                return False

        return True

    def get_folders(self) -> list[str]:
        """
        Retrieve a list of all email folders.

        Returns:
            list[str]: List of folder names in the email account
        """
        try:
            return [self.__decode_folder(i) for i in self.list()[1] if i.find(b'\\NoSelect') == -1]
        except Exception as e:
            raise IMAPManagerException(f"There was an error while listing folders: {str(e)}") from None

    def select_folder(self, mailbox: str = INBOX, readonly: bool = False):
        """
        Selects a mailbox for further operations.

        Args:
            mailbox (str): The name of the mailbox to select. Defaults to "INBOX".
            readonly (bool): If True, opens the mailbox in read-only mode. 
            Defaults to False.

        Raises:
            IMAPManagerException: If the mailbox cannot be selected or an invalid mailbox
            name is provided.

        Notes:
            - Prevents re-selecting the currently active mailbox with the same mode.
            - Ensures the folder name is properly encoded and valid.
        """
        if self.__current_folder[0] != mailbox or self.__current_folder[1] != readonly:
            self.__check_folder_names(mailbox)
            self.__ensure_command(super().select(self.__encode_folder(mailbox), readonly))
            self.__current_folder = (mailbox, readonly)

    def build_search_criteria_query_string(self, search_criteria: SearchCriteria) -> str:
        """
        Builds an IMAP-compatible search criteria query string based on given search parameters.

        Args:
            search_criteria (SearchCriteria): An object containing various search criteria, 
            such as senders, receivers, subject, date ranges, included/excluded text, and flags.

        Returns:
            str: A search criteria query string ready to be used with IMAP's SEARCH command.

        Notes:
            This function recursively builds complex OR queries and handles multiple search criteria 
            by converting them into the required format as per RFC 9051.

        Example:
            >>> search_criteria = SearchCriteria(senders=["a@mail.com"],
            ...                                  receivers=["b@mail.com", "c@mail.com"],
            ...                                  subject="Hello",
            ...                                  since="2023-01-01",
            ...                                  before="2023-12-31",
            ...                                  text="world",
            ...                                  flags=["Flagged", "Seen"])
            >>> build_search_criteria_query_string(search_criteria)
            'OR (FROM "a@mail.com") (OR (TO "b@mail.com") (TO "c@mail.com")) (SUBJECT "Hello") (SINCE 
            ... "2023-01-01") (BEFORE "2023-12-31") (TEXT "world") (OR (FLAGGED) (SEEN))'

        References:
            - https://datatracker.ietf.org/doc/html/rfc9051#name-search-command
        """

        def recursive_or_query(criteria: str, search_keys: List[str]) -> str:
            """
            Recursively builds an OR query for a list of search keys.

            Args:
                criteria (str): The search criteria, e.g., "FROM".
                search_keys (List[str]): A list of values for the criteria.

            Returns:
                str: A query string with nested OR conditions for the search keys.

            Example:
                >>> recursive_or_query("FROM", ["a@mail.com", "b@mail.com", "c@mail.com"])
                'OR (FROM "a@mail.com") (OR (FROM "b@mail.com") (FROM "c@mail.com"))'
            """
            query = ''
            len_search_keys = len(search_keys)
            if len_search_keys == 1:
                return f'{criteria} "{search_keys[0]}"'

            mid = len_search_keys // 2
            left_part = recursive_or_query(criteria, search_keys[:mid])
            right_part = recursive_or_query(criteria, search_keys[mid:])

            return query + f'OR ({left_part}) ({right_part})'

        def add_criterion(
            criteria: str,
            value: str | list | None,
            seperate_with_or: bool = False
        ) -> str:
            """
            Converts a single search criterion and its value(s) into a query string.

            Args:
                criteria (str): The search criterion, e.g., "FROM" or "SUBJECT".
                value (str | list | None): The value(s) to match for the criterion.
                seperate_with_or (bool): Whether to combine multiple values with OR conditions.

            Returns:
                str: A formatted query string for the given criterion.

            Example:
                >>> add_criterion("FROM", value=["a@mail.com", "b@mail.com"])
                ' (FROM "a@mail.com") (FROM "b@mail.com")'
            """
            if not value:
                return ''

            if isinstance(value, list):
                if criteria == '':
                    # value=["Flagged", "Seen", "Answered"]
                    return ' '.join([i.upper() for i in value])

                if len(value) <= 1:
                    return f' ({criteria} "{value[0]}")'

            if seperate_with_or and len(value) > 1:
                criteria = ''
                value = recursive_or_query(criteria, value)

            return f' ({criteria} "{value}")'

        mark_list = [m.value for m in Mark]
        for flag in search_criteria.flags:
            if flag not in mark_list:
                raise IMAPManagerException(f"Unsupported flag: {flag}. The supported flags are: {', '.join(mark_list)}")

        search_criteria_query = ''
        search_criteria_query += add_criterion(
            'FROM', 
            search_criteria.senders,
            len(search_criteria.senders) > 1
        )
        search_criteria_query += add_criterion(
            'TO', 
            search_criteria.receivers,
            len(search_criteria.receivers) > 1
        )
        search_criteria_query += add_criterion(
            'CC',
            search_criteria.cc,
            len(search_criteria.cc) > 1
        )
        search_criteria_query += add_criterion(
            'BCC',
            search_criteria.bcc,
            len(search_criteria.bcc) > 1
        )
        search_criteria_query += add_criterion("SUBJECT", search_criteria.subject)
        search_criteria_query += add_criterion("SINCE", search_criteria.since)
        search_criteria_query += add_criterion("BEFORE", search_criteria.before)
        search_criteria_query += add_criterion("TEXT", search_criteria.include)
        search_criteria_query += add_criterion("NOT TEXT", search_criteria.exclude)
        search_criteria_query += add_criterion('', search_criteria.flags)
        search_criteria_query += add_criterion('BODY', search_criteria.has_attachments and 'ATTACHMENT' or '')
        # TODO: Add smaller_than and larger_than.
        return search_criteria_query.strip()

    def search_emails(self,
        folder: str = INBOX,
        search: str | SearchCriteria = ALL
    ) -> list[str]:
        """
        Get email uids from a specified folder based on search criteria.

        Args:
            folder (str, optional): Folder to search in. Defaults to "inbox".
            search (str | SearchCriteria, optional): Search criteria. Defaults to "ALL".

        Returns:
            list[str]: List of email uids

        Example:
            >>> search_emails("INBOX") # Means "ALL"
            ['1', '2', '3', '4', '5'] 

            >>> search_emails("INBOX", "FROM 'a@mail.com'")
            ['1', '2', '3']

            >>> search_emails("INBOX", SearchCriteria(senders=['a@mail.com']))
            ['1', '2', '3']
        """
        self.select_folder(folder, readonly=True)

        # Creating search query
        search_criteria_query = ''
        try:
            search_criteria_query = ''
            if isinstance(search, SearchCriteria):
                search_criteria_query = self.build_search_criteria_query_string(search) or ALL
            else:
                search_criteria_query = search or ALL
        except Exception as e:
            raise IMAPManagerException(f"Error while building search query: {str(e)}") from None

        # Searching emails
        try:
            search_status, uids = self.uid(
                'search', 
                None,
                search_criteria_query.encode("utf-8") if search_criteria_query else ALL
            )

            if search_status != 'OK':
                raise IMAPManagerException(f"Error while getting email uids, search query was `{search_criteria_query}`: {search_status}")

            uids = uids[0].split()[::-1]
            return uids
        except Exception as e:
            raise IMAPManagerException(f"Error while getting email uids, search query was `{search_criteria_query}`: {str(e)}") from None

    def fetch_emails(
        self,
        uids: list[str],
        offset: int = 0,
        count: int = 10
    ) -> Mailbox:
        """
        Fetch emails from a list of uids.

        Args:
            uids (list[str]): List of email uids.
            offset (int, optional): Offset to start fetching emails from. Defaults to 0.
            count (int, optional): Number of emails to fetch. Defaults to 10.

        Returns:
            Mailbox: Dataclass containing the fetched emails, folder, and total number of emails.

        Example:
            >>> fetch_emails(["1", "2"])
            Mailbox(folder='INBOX', emails=[EmailSummary(uid="1", sender="a@gmail.com", ...), EmailSummary(uid="2", sender="b@gmail.com", ...)], total=2)
        """
        uids_len = len(uids)
        if offset < 0:
            raise IMAPManagerException(f"Invalid offset: {offset}. Offset must be greater than or equal to 0.")
        if count < 1:
            raise IMAPManagerException(f"Invalid count: {count}. Count must be greater than or equal to 1.")
        if offset >= uids_len:
            raise IMAPManagerException(f"Invalid offset: {offset}. Offset must be less than the number of emails: {uids_len}.")

        if uids_len == 0:
            return Mailbox(folder=self.__current_folder[0], emails=[], total=0)

        # Fetching emails
        emails = []
        try:
            uid_range = uids[offset]
            if count > 1:
                uid_range = f"{uids[offset]:str(int(uids[offset]) + count)}"

            status, messages = self.uid(
                'FETCH', 
                uid_range,
                '(BODY.PEEK[HEADER.FIELDS (FROM TO SUBJECT DATE)] BODY.PEEK[TEXT]<0.500> FLAGS BODYSTRUCTURE)'
            )
            if status != 'OK':
                raise IMAPManagerException(f"Error while fetching emails, fetched email length was `{len(messages)}`: {status}")

            matches = MessageParser.messages(messages)
            for i, match in enumerate(matches):
                message_headers = MessageParser.headers_from_message(match)
                if not message_headers:
                    print(f"Header fields could not be parsed of message: {uids[i]} skipping...")
                    continue

                emails.append(EmailSummary(
                    uid=uids[i].decode(),
                    sender=message_headers["sender"],
                    receiver=message_headers["receiver"],
                    subject=message_headers["subject"],
                    body_short=truncate_text(MessageParser.body_from_message(match), BODY_SHORT_THRESHOLD),
                    date=message_headers["date"],
                    flags=MessageParser.flags_from_message(match),
                    attachments=MessageParser.attachments_from_message(match)
                ))
        except Exception as e:
            raise IMAPManagerException(f"Error while fetching emails, fetched email length was `{len(emails)}`: {str(e)}") from None

        return Mailbox(folder=self.__current_folder[0], emails=emails, total=len(uids))

    def get_email_content(
        self,
        uid: str,
        folder: str = INBOX
    ) -> EmailWithContent:
        """
        Retrieve full content of a specific email. 

        Args:
            uid (str): Unique identifier of the email
            folder (str, optional): Folder containing the email. Defaults to "inbox".

        Returns:
            EmailWithContent: Dataclass containing the email content

        Notes:
            - Replaces inline attachments with data URLs to display them inline
            and if an error occurs while replacing the inline attachments, the
            replacement operation will be skipped without raising an error but
            it will be logged as a warning.
            - Marks the email as "Seen" if it is not already and if an error 
            occurs while marking the email, the mark operation will be skipped
            without raising an error but it will be logged as a warning.
        """
        self.select_folder(folder, readonly=True)

        # Get body and attachments
        body, attachments = "", []
        try:
            status, message = self.uid('fetch', uid, '(RFC822)')
            if status != 'OK':
                raise IMAPManagerException(f"Error while getting email content: {status}")

            message = email.message_from_bytes(message[0][1], policy=email.policy.default)

            for part in (message.walk() if message.is_multipart() else [message]):
                content_type = part.get_content_type()
                file_name = part.get_filename()
                if file_name:
                    attachments.append(Attachment(
                        cid=part.get("X-Attachment-Id"),
                        name=file_name,
                        data=base64.b64encode(
                            part.get_payload(decode=True)
                        ).decode("utf-8", errors="ignore"),
                        size=make_size_human_readable(len(part.get_payload(decode=True))),
                        type=content_type
                    ))
                elif content_type == "text/html" or (content_type == "text/plain" and not body):
                    body = part.get_payload(decode=True)
                    if body:
                        body = body.decode(part.get_content_charset())
        except Exception as e:
            raise IMAPManagerException(f"There was a problem with getting email content: {str(e)}") from None

        try:
            # Replacing inline attachments
            if attachments:
                # TODO: This should be moved to MessageParser class as
                # a static method.
                for match in INLINE_ATTACHMENT_PATTERN.finditer(body):
                    cid = match.group(1)
                    for attachment in attachments:
                        if cid in attachment.name or cid in attachment.cid:
                            body = body.replace(
                                f'cid:{cid}',
                                f'data:{attachment.type};base64,{attachment.data}'
                            )
        except Exception as e:
            # If there is a problem with inline attachments
            # just ignore them.
            print(f"There was a problem with inline attachments: {str(e)}")
            pass

        try:
            self.mark_email(uid, "Seen", folder)
        except Exception as e:
            # If there is a problem with marking the email as seen
            # just ignore it.
            print(f"There was a problem with marking the email as seen: {str(e)}")
            pass

        return EmailWithContent(
            uid=uid,
            sender=message["From"],
            receiver=message["To"],
            subject=message["Subject"],
            body=body,
            date=message["Date"],
            cc=message.get("Cc", ""),
            bcc=message.get("Bcc", ""),
            message_id=message.get("Message-Id", ""),
            metadata={
                "In-Reply-To": message.get("In-Reply-To", ""),
                "References": message.get("References", "")
            },
            flags=self.fetch_flags_of_emails(uid) or [],
            attachments=attachments
        )

    def __mark_email(
        self,
        uid: str,
        mark: Mark,
        limit: int,
        command: str,
        folder: str,
        success_msg: str,
        err_msg: str
    ) -> IMAPCommandResult:
        """
        Mark an email with a specific flag with given `command`.

        Args:
            uid (str): Unique identifier of the email
            mark (str): Flag to apply to the email.
            limit (int): Maximum number of emails to mark.
            command (str): IMAP command to apply the flag like 
            `+FLAGS` or `-FLAGS`.
            folder (str): Folder containing the email.
            success_msg (str): Success message to display.
            err_msg (str): Error message to display.

        Returns:
            IMAPCommandResult: A tuple containing:
                - A bool indicating whether the email was marked successfully.
                - A string containing a success message or an error message.
        """
        if limit < 1:
            raise IMAPManagerException(f"Invalid limit: {limit}. Limit must be at least 1.")

        self.select_folder(folder)

        mark = mark.lower()
        mark_list = [m.value for m in Mark]
        if not mark or mark not in mark_list:
            raise IMAPManagerException(
                f"Unsupported mark: {mark}. Please use one of the following: {', '.join(mark_list)}"
            )

        mark_result = self.uid(
            'STORE', 
            f"{uid:str(int(uid) + limit + 1)}" if limit > 1 else uid,
            command,
            mark
        )
        if mark_result[0]:
            return self.__parse_command_result(
                self.expunge(),
                success_msg,
                err_msg
            )

        return mark_result

    def mark_email(
        self,
        uid: str,
        mark: Mark,
        folder: str = Folder.Inbox,
        limit: int = 1
    ) -> IMAPCommandResult:
        """
        Mark an email with a specific flag.

        Args:
            uid (str): Unique identifier of the email.
            mark (str): Flag to apply to the email.
            folder (str, optional): Folder containing the email. 
            Defaults to "inbox".
            limit (int, optional): Maximum number of emails to mark. 
            Defaults to 1.

        Returns:
            IMAPCommandResult: A tuple containing:
                - A bool indicating whether the email was marked successfully.
                - A string containing a success message or an error message.
        """
        return self.__mark_email(
            uid,
            mark,
            limit,
            "+FLAGS",
            folder,
            f"Email(s) marked with {mark} successfully.",
            f"There was an error while marking the email(s) with {mark}."
        )

    def unmark_email(
        self,
        uid: str,
        mark: Mark,
        folder: str = Folder.Inbox,
        limit: int = 1
    ) -> IMAPCommandResult:
        """
        Unmark an email with a specific flag.

        Args:
            uid (str): Unique identifier of the email.
            mark (str): Flag to remove from the email.
            folder (str, optional): Folder containing the email. Defaults to "inbox".

        Returns:
            IMAPCommandResult: A tuple containing:
                - A bool indicating whether the email was unmarked successfully.
                - A string containing a success message or an error message.
        """
        return self.__mark_email(
            uid,
            mark,
            limit,
            "-FLAGS",
            folder,
            f"Email(s) unmarked with {mark} successfully.",
            f"There was an error while unmarking the email(s) with {mark}."
        )

    def move_email(self,
        uid: str,
        source_folder: str,
        destination_folder: str,
        limit: int = 1
    ) -> IMAPCommandResult:
        """
        Move an email from one folder to another.

        Args:
            uid (str): Unique identifier of the email. Also starts the
            range of emails if `limit` is greater than 1.
            source_folder (str): Current folder of the email.
            destination_folder (str): Target folder to move the email to.
            limit (int, optional): Maximum number of emails to move. 
            Defaults to 1.

        Returns:
            IMAPCommandResult: A tuple containing:
                - A bool indicating whether the email was moved successfully.
                - A string containing a success message or an error message.
        """
        if limit < 1:
            raise IMAPManagerException(f"Invalid limit: {limit}. Limit must be at least 1.")

        self.__check_folder_names([source_folder, destination_folder])

        if source_folder == destination_folder:
            return IMAPCommandResult(success=True, message="Destination folder is the same as the source folder.")

        self.select_folder(source_folder)

        move_result = self.uid(
            'MOVE', 
            f"{uid}:{str(int(uid) + limit + 1)}" if limit > 1 else uid,
            self.__encode_folder(destination_folder)
        )

        if move_result[0]:
            return self.__parse_command_result(
                self.expunge(),
                "Email(s) moved successfully.",
                "There was an error while moving the email(s)."
            )

        return move_result

    def copy_email(self,
        uid: str,
        source_folder: str,
        destination_folder: str,
        limit: int = 1
    ) -> IMAPCommandResult:
        """
        Create a copy of an email in another folder.

        Args:
            uid (str): Unique identifier of the email. Also starts the 
            range of emails if `limit` is greater than 1.
            source_folder (str): Current folder of the email.
            destination_folder (str): Target folder to copy the email to.
            limit (int, optional): Number of emails to copy. Defaults to 1.

        Returns:
            IMAPCommandResult: A tuple containing:
                - A bool indicating whether the email was copied successfully.
                - A string containing a success message or an error message.
        """
        if limit < 1:
            raise IMAPManagerException(f"Invalid limit: {limit}. Limit must be at least 1.")

        self.__check_folder_names([source_folder, destination_folder])

        self.select_folder(source_folder)

        copy_result = self.uid(
            'COPY',
            f"{uid}:{str(int(uid) + limit + 1)}" if limit > 1 else uid,
            self.__encode_folder(destination_folder)
        )

        if copy_result[0]:
            return self.__parse_command_result(
                self.expunge(),
                "Email(s) copied successfully.",
                "There was an error while copying the email(s)."
            )

        return copy_result

    def delete_email(self, uid: str, folder: str, limit: int = 1) -> IMAPCommandResult:
        """
        Delete an email from a specific folder.

        Args:
            uid (str): Unique identifier of the email. Also starts the 
            range of emails if `limit` is greater than 1.
            folder (str): Folder containing the email.
            limit (int, optional): Maximum number of emails to delete. 
            Defaults to 1.

        Returns:
            IMAPCommandResult: A tuple containing:
                - A bool indicating whether the email was deleted successfully.
                - A string containing a success message or an error message.
        """
        if limit < 1:
            raise IMAPManagerException(f"Invalid limit: {limit}. Limit must be at least 1.")

        self.__check_folder_names(folder)

        trash_mailbox_name = self.find_matching_folder(Folder.Trash)

        try:
            if folder != trash_mailbox_name:
                self.move_email(uid, folder, trash_mailbox_name)
        except Exception as e:
            raise IMAPManagerException(
                f"Error while moving email to trash folder for deletion: {str(e)}."
            ) from None

        self.select_folder(trash_mailbox_name)

        success_msg = "Email(s) deleted successfully."
        err_msg = "There was an error while deleting the email(s)."

        delete_result = self.__parse_command_result(
            self.uid(
                'STORE', 
                f"{uid}:{str(int(uid) + limit + 1)}" if limit > 1 else uid,
                '+FLAGS', 
                '\\Deleted'
            ),
            success_msg,
            err_msg
        )

        if delete_result[0]:
            return self.__parse_command_result(
                self.expunge(),
                success_msg,
                err_msg
            )

        return delete_result

    def create_folder(self,
        folder_name: str,
        parent_folder: str | None = None
    ) -> IMAPCommandResult:
        """
        Create a new email folder.

        Args:
            folder_name (str): Name of the new folder.
            parent_folder (str, optional): Parent folder for nested folder creation. 
                                           Defaults to None.

        Returns:
            IMAPCommandResult: A tuple containing:
                - A bool indicating whether the folder was created successfully.
                - A string containing a success message or an error message.
        """
        self.__check_folder_names([folder_name, parent_folder])

        if parent_folder:
            folder_name = f"{parent_folder}/{folder_name}"

        return self.__parse_command_result(
            self.create(self.__encode_folder(folder_name)),
            "Folder created successfully.",
            "There was an error while creating the folder."
        )

    def delete_folder(self, folder_name: str) -> IMAPCommandResult:
        """
        Delete an existing email folder.

        Args:
            folder_name (str): Name of the folder to delete.

        Returns:
            IMAPCommandResult: A tuple containing:
                - A bool indicating whether the folder was deleted successfully.
                - A string containing a success message or an error message.
        """
        self.__check_folder_names(folder_name)

        return self.__parse_command_result(
            self.delete(self.__encode_folder(folder_name)),
            "Folder deleted successfully.",
            "There was an error while deleting the folder."
        )

    def move_folder(self, folder_name: str, destination_folder: str) -> IMAPCommandResult:
        """
        Move a folder to a new location.

        Args:
            folder_name (str): Name of the folder to move.
            destination_folder (str): Target location for the folder.

        Returns:
            IMAPCommandResult: A tuple containing:
                - A bool indicating whether the folder was moved successfully.
                - A string containing a success message or an error message.
        """
        self.__check_folder_names([folder_name, destination_folder])

        if "/" in folder_name:
            destination_folder = f"{destination_folder}/{folder_name.split("/")[-1]}"

        return self.__parse_command_result(
            self.rename(
                self.__encode_folder(folder_name),
                self.__encode_folder(destination_folder)
            ),
            "Folder moved successfully.",
            "There was an error while moving the folder."
        )

    def rename_folder(self, folder_name: str, new_folder_name: str) -> IMAPCommandResult:
        """
        Rename an existing email folder.

        Args:
            folder_name (str): Current name of the folder.
            new_folder_name (str): New name for the folder.

        Returns:
            IMAPCommandResult: A tuple containing:
                - A bool indicating whether the folder was renamed successfully.
                - A string containing a success message or an error message.
        """
        self.__check_folder_names([folder_name, new_folder_name])

        if "/" in folder_name:
            new_folder_name = folder_name.replace(
                folder_name.split("/")[-1],
                new_folder_name
            )

        return self.__parse_command_result(
            self.rename(
                self.__encode_folder(folder_name),
                self.__encode_folder(new_folder_name)
            ),
            "Folder renamed successfully.",
            "There was an error while renaming the folder."
        )

__all__ = [
    "IMAPManager", 
    "IMAPCommandResult", 
    "IMAPManagerException", 
    "IMAPManagerLoggedOutException",
    "Mark",
    "Folder"
]
