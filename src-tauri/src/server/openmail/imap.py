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

from typing import List, override, TypedDict
from types import MappingProxyType
from datetime import datetime
from enum import Enum

from .parser import MessageParser
from .utils import extract_domain, choose_positive
from .utils import truncate_text, contains_non_ascii, make_size_human_readable
from .types import SearchCriteria, Attachment, Mailbox, EmailSummary, EmailWithContent, Flags

# Exceptions
class IMAPManagerException(Exception):
    """Custom exception for IMAPManager class."""

class IMAPManagerLoggedOutException(IMAPManagerException):
    """Custom exception for when the IMAPManager is logged out
    while trying to perform an action that requires authentication."""

# Enums
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

# Custom consts
GET_EMAILS_OFFSET = MappingProxyType({
    "start": 0,
    "end": 10
})
UNKNOWN_PLACEHOLDERS = MappingProxyType({
    "receiver": "Unknown Receiver",
    "sender": "Unknown Sender",
    "subject": "No Subject",
    "date": "Unknown Date"
})
BODY_SHORT_THRESHOLD = 50
MAX_FOLDER_NAME_LENGTH = 100
CONN_TIMEOUT = 30 # 30 seconds
IDLE_TIMEOUT = 30 * 60 # 30 minutes
WAIT_RESPONSE_TIMEOUT = 3 * 60 # 3 minutes

# Regular expressions
INLINE_ATTACHMENT_PATTERN = re.compile(r'<img src="cid:([^"]+)"')

class IMAPManager(imaplib.IMAP4_SSL):
    """
    IMAPManager extends the `imaplib.IMAP4` class.
    Does not override any methods except `login`, `logout`
    and `__simple_command`. Provides additional features 
    especially idling and listening exists responses on 
    different threads. Mainly used in `OpenMail` class.
    """

    class SearchedEmails(TypedDict):
        """Type hinting for `__searched_emails` dict."""
        uids: list[str]
        folder: str
        search_query: str

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

    def __init__(
        self,
        email_address: str,
        password: str,
        host: str = "",
        port: int = IMAP_PORT,
        ssl_context: any = None,
        timeout: int = CONN_TIMEOUT
    ):
        self.__searched_emails = None

        # IDLE and READLINE vars
        self.__is_idle = False
        self.__current_idle_start_time = None
        self.__current_idle_tag = None
        self.__wait_for_response = None

        self.__idle_thread_event = None
        self.__idle_thread = None

        self.__readline_thread_event = None
        self.__readline_thread = None
        
        # These are must be called after IDLE and READLINE vars are 
        # initialized because these methods are using `_simple_command`
        # and `_simple_command` is overridden in this class to handle
        # IDLE and READLINE operations and uses these vars.
        super().__init__(
            host or self.__find_imap_server(email_address),
            port or IMAP_PORT,
            ssl_context=ssl_context,
            timeout=choose_positive(timeout, CONN_TIMEOUT)
        )

        self.login(email_address, password)


    def __find_imap_server(self, email_address: str) -> str:
        """
        Determines the IMAP server address for a given email address.

        Args:
            email_address (str): The email address for which to find the 
            corresponding IMAP server.

        Returns:
            str: The IMAP server address associated with the email's domain.

        Example:
            >>> email_address = "user@gmail.com"
            >>> self.__find_imap_server(email_address)
            "imap.gmail.com"
            >>> email_address = "user@unknown.com"
            >>> self.__find_imap_server(email_address)
            IMAPManagerException: Unsupported email domain

        Raises:
            IMAPManagerException: If the email domain is not supported or 
            not found in the IMAP_SERVERS mapping.
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

        # If the command is "DONE", idle checking 
        # and restoring must not be done since
        # `DONE` command is used to leave IDLE mode.
        # Also, in the timeout case, the `idle` method
        # will be called after the `done` method, 
        # which is already handled in the `__idle` method.
        if name == "DONE":
            return super()._simple_command(name, *args)
        
        # Leaving IDLE mode if needed
        try:
            was_idle_before_call = self.__is_idle
            if was_idle_before_call:
                self.done()
        except Exception as e:
            if is_logged_out(str(e).lower()):
                raise IMAPManagerLoggedOutException(f"To perform this action, the IMAPManager must be logged in: {str(e)}") from None
            else:
                print(f"Unexpected error while leaving IDLE mode: {str(e)}")
                # Even if leaving IDLE failed, set idle and readline threads and set
                # __is_idle to False.
                self.__handle_done_response()
                print("Active IDLE status set to False and threads stopped forcefully.")

        # Run wanted command.
        try:
            result = super()._simple_command(name, *args)
        except Exception as e:
            if is_logged_out(str(e).lower()):
                raise IMAPManagerLoggedOutException(f"To perform this action, the IMAPManager must be logged in: {str(e)}") from None
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
            raise IMAPManagerException(f"There was an error while parsing command `{result}` result: {str(e)}") from None

    def idle(self):
        """
        Initiates the IMAP IDLE command to start monitoring changes 
        in the mailbox on its own thread. If already in IDLE mode, 
        does nothing.
        """
        if not self.__is_idle:
            self.__current_idle_tag = self._new_tag()
            self.send(b"%s IDLE\r\n" % self.__current_idle_tag)
            print(f"'IDLE' command sent with tag: {self.__current_idle_tag} at {datetime.now()}.")
            self.__readline()
            self.__wait_response(IMAPManager.WaitResponse.IDLE)

    def done(self):
        """
        Terminates the current IDLE session if active.
        """
        if self.__is_idle:
            self.send(b"DONE\r\n")
            print(f"DONE command sent for {self.__current_idle_tag} at {datetime.now()}.")
            self.__wait_response(IMAPManager.WaitResponse.DONE)

    def __wait_response(self, wait_response: WaitResponse):
        """
        Waits for a specific response type from the IMAP server.
        
        Args:
            wait_response (IMAPManager.WaitResponse): Expected response type to wait for
            
        Times out after WAIT_RESPONSE_TIMEOUT seconds and resets wait state.
        """
        counter = 0
        while self.__wait_for_response != wait_response:
            time.sleep(1)
            counter += 1
            if counter > WAIT_RESPONSE_TIMEOUT:
                print(f"IMAPManager.WaitResponse: {wait_response} did not received in time at {datetime.now()}. IMAPManager.WaitResponse set to None")
                break

        self.__wait_for_response = None

    def __idle(self):
        """
        Background thread handler for IDLE mode monitoring.

        Continuously checks IDLE session duration and automatically 
        refreshes the connection when IDLE_TIMEOUT is reached.
        """
        while not self.__idle_thread_event.is_set():
            print(f"IDLING for {self.__current_idle_tag} at {datetime.now()}.")
            time.sleep(1)
            if time.time() - self.__current_idle_start_time > IDLE_TIMEOUT:
                print(f"IDLING timeout reached for {self.__current_idle_tag} at {datetime.now()}.")
                self.done()
                if not self.__idle_thread_event.is_set():
                    self.idle()

    def __readline(self):
        """
        Initializes and manages the response reading thread.
        
        Creates a new thread for continuously reading server responses
        if one doesn't exist or isn't active. Processes responses through
        the handle_response method.
        """
        def readline_thread():
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

    def __handle_idle_response(self):
        """
        Handles the server's response to the IDLE command.
        Marks the client as being in the IDLE state, sets 
        start time, and starts the IDLE monitoring thread.
        This method shouldn't be called directly, but rather 
        through the `handle_response` method.
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

        self.__wait_for_response = IMAPManager.WaitResponse.IDLE
        print(f"'IDLE' response for {self.__current_idle_tag} handled, IDLE thread started at {self.__current_idle_start_time}.")

    def __handle_done_response(self):
        """
        Handles the server's response to the DONE command.
        Marks the client as no longer in the IDLE state 
        and stops the IDLE monitoring thread. This method
        shouldn't be called directly, but rather through
        the `handle_response` method.
        """
        print(f"'DONE' response received for {self.__current_idle_tag} at {datetime.now()}.")
        self.__is_idle = False
        self.__current_idle_tag = None

        self.__idle_thread_event.set()
        self.__readline_thread_event.set()

        self.__wait_for_response = IMAPManager.WaitResponse.DONE
        print(
            f"'DONE' response for {self.__current_idle_tag} handled, IDLE thread stopped at {datetime.now()}."
        )

    def __handle_bye_response(self):
        """
        Handles the server's 'BYE' response, which indicates the server 
        is closing the connection. Safely terminates the connection, stops 
        threads, and raises an exception to signal the logout event. This
        method shouldn't be called directly, but rather through the 
        `handle_response`method.
        """
        print(f"'BYE' response received from server at {datetime.now()}.")
        self.__wait_for_response = IMAPManager.WaitResponse.BYE
        self.__readline_thread_event.set()
        self.__idle_thread_event.set()
        self.__is_idle = False
        self.__current_idle_tag = None
        raise IMAPManagerLoggedOutException(f"'BYE' response received from server at {datetime.now()}. IMAPManager connection closed safely.") from None

    def __handle_exists_response(self, response: bytes):
        """
        Handles the 'EXISTS' response from the server, which indicates the 
        number of messages in the mailbox. Updates internal state or performs 
        necessary actions based on the response. This method shouldn't be
        called directly, but rather through the `handle_response` method.
    
        Args:
            response (bytes): The server's EXISTS response data.
        """
        print(f"'EXISTS' response received from server at {datetime.now()}.")
        self.__wait_for_response = IMAPManager.WaitResponse.EXISTS
        # TODO: Implement handling of EXISTS response
        pass

    def __handle_response(self, response: bytes):
        """
        Determines the type of server response and delegates handling to the 
        appropriate method. This method shouldn't be called directly, but rather 
        through the `readline` method.

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
            requested_folder (bytes): The IMAP folder name (e.g., `b'\\Inbox'` or `b'\\Trash'`).

        Returns:
            bytes | None: The folder name in bytes if a match is found; otherwise, None.

        Example:
            >>> find_matching_folder(b'\\Inbox')
            b'INBOX'
            >>> find_matching_folder(b'\\Trash')
            b'Papelera' # In Spanish
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

        Example:
            >>> __encode_folder("INBOX")
            b'\\Inbox'
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

        Example:
            >>> __decode_folder(b'\\Inbox')
            'INBOX'
            >>> __decode_folder(b'(\\HasNoChildren) "/" "INBOX"')
            'INBOX'
            >>> __decode_folder(b'(\\HasNoChildren) "|" "INBOX"')
            'INBOX'
        """
        try:
            # Most of the servers return folder name as b'(\\HasNoChildren) "/" "INBOX"'
            # But some servers like yandex return folder name as b'(\\HasNoChildren) "|" "INBOX"'
            # So we're replacing "|" with "/" to make it consistent
            return folder.decode().replace(' "|" ', ' "/" ').split(' "/" ')[1].replace('"', '')
        except Exception as e:
            raise IMAPManagerException(f"Error while decoding folder name `{str(folder)}`: `{str(e)}`.") from None

    def __check_folder_names(self, folders: str | List[str], raise_error: bool = True) -> bool:
        """
        Check if a folder name(s) is valid.

        Args:
            folders (str | List[str]): Folder name or list of folder names
            raise_error (bool, optional): If True, raise an error if the folder name is invalid. 
                                          Default is True

        Returns:
            bool: True if folder name is valid, False otherwise

        Example:
            >>> self.__check_folder_names("INBOX")
            True
            >>> self.__check_folder_names(["INBOX", "Trash"])
            True
            >>> self.__check_folder_names("")
            raises IMAPManagerException
            >>> self.__check_folder_names("INBOX", raise_error=False)
            False

        Raises:
            IMAPManagerException: If the folder name is invalid and raise_error is True
        """
        if isinstance(folders, str):
            folders = [folders]

        for folder_name in folders:
            folder_name_length = len(folder_name)
            if folder_name is None or folder_name == "" or folder_name_length > MAX_FOLDER_NAME_LENGTH or folder_name_length < 1:
                if raise_error:
                    raise IMAPManagerException(f"Invalid folder name: `{folder_name}`")
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
            raise IMAPManagerException(f"There was an error while listing folders: `{str(e)}`") from None

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
                raise IMAPManagerException(f"Unsupported flag: `{flag}`. The supported flags are: `{', '.join(mark_list)}`.")

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

        def save_emails(uids: list[str], folder: str, search_query: str):
            """
            Save emails to a specified folder for later use.

            Args:
                uids (list[str]): A list of email uids to save.
                folder (str): The folder to save the emails to.
                search_query (str): The search query used to fetch the emails.
            """
            self.__searched_emails = IMAPManager.SearchedEmails(
                folder=folder,
                search_query=search_query,
                uids=uids
            )

        status, _ = self.select(folder, readonly=True)
        if status != 'OK':
            raise IMAPManagerException(f"Error while selecting folder `{folder}`: `{status}`")

        # Creating search query
        search_criteria_query = ''
        try:
            search_criteria_query = ''
            if isinstance(search, SearchCriteria):
                search_criteria_query = self.build_search_criteria_query_string(search) or ALL
            else:
                search_criteria_query = search or ALL
        except Exception as e:
            raise IMAPManagerException(f"Error while building search query from `{str(search)}`: `{str(e)}`") from None

        # Searching emails
        try:
            search_status, uids = self.uid(
                'search', 
                None,
                search_criteria_query.encode("utf-8") if search_criteria_query else ALL
            )

            if search_status != 'OK':
                raise IMAPManagerException(f"Error while getting email uids, search query was `{search_criteria_query}` and error is `{search_status}.`")
            
            if not uids or not uids[0]:
                return []
            
            uids = uids[0].split()[::-1]
            save_emails(uids, folder, search_criteria_query)
        except Exception as e:
            raise IMAPManagerException(f"Error while getting email uids, search query was `{search_criteria_query}` and error is `{str(e)}.`")

    def get_emails(
        self,
        offset_start: int = GET_EMAILS_OFFSET["start"],
        offset_end: int = GET_EMAILS_OFFSET["end"]
    ) -> Mailbox:
        """
        Fetch emails from a list of uids.

        Args:
            offset_start (int, optional): Starting index of the emails to fetch. Defaults to 0.
            offset_end (int, optional): Ending index of the emails to fetch. Defaults to 10.

        Returns:
            Mailbox: Dataclass containing the fetched emails, folder, and total number of emails.

        Example:
            >>> get_emails(0, 2)
            Mailbox(folder='INBOX', emails=[EmailSummary(uid="1", sender="a@gmail.com", ...), EmailSummary(uid="2", sender="b@gmail.com", ...)], total=2)
        """
        if not self.__searched_emails or not self.__searched_emails.uids or not self.__searched_emails.uids[0]:
            raise IMAPManagerException("No emails have been searched yet. Call `search_emails` first.")
        
        uids_len = len(self.__searched_emails.uids)
        if offset_start < 0:
            raise IMAPManagerException(f"Invalid `offset_start`: {offset_start}. `offset_start` must be greater than or equal to 0.")
        if offset_end < 0:
            raise IMAPManagerException(f"Invalid `offset_end`: {offset_end}. `offset_end` must be greater than or equal to 0.")
        if offset_end >= uids_len:
            raise IMAPManagerException(f"Invalid `offset_end`: {offset_end}. `offset_end` must be less than the number of emails: `{uids_len}`.")
        if offset_start >= uids_len:
            raise IMAPManagerException(f"Invalid `offset_start`: {offset_start}. `offset_start` must be less than the number of emails: `{uids_len}`.")
        
        if uids_len == 0:
            return Mailbox(folder=self.__searched_emails.folder, emails=[], total=0)

        # Fetching emails
        emails = []
        try:
            sequence_set = f"{self.__searched_emails.uids[offset_start]:self.__searched_emails.uids[offset_end]}"
            status, messages = self.uid(
                'FETCH', 
                sequence_set,
                '(BODY.PEEK[HEADER.FIELDS (FROM TO SUBJECT DATE)] BODY.PEEK[TEXT]<0.500> FLAGS BODYSTRUCTURE)'
            )
            if status != 'OK':
                raise IMAPManagerException(f"Error while fetching emails `{sequence_set}` in folder `{self.__searched_emails.folder}`, fetched email length was `{len(emails)}`: `{str(e)}`") from None


            matches = MessageParser.messages(messages)
            for i, match in enumerate(matches):
                message_headers = MessageParser.headers_from_message(match)
                if not message_headers:
                    print(f"Header fields could not be parsed of email `{self.__searched_emails.uids[i]}` skipping...")
                    continue

                emails.append(EmailSummary(
                    uid=self.__searched_emails.uids[i].decode(),
                    sender=message_headers.get("sender", UNKNOWN_PLACEHOLDERS["sender"]),
                    receiver=message_headers.get("receiver", UNKNOWN_PLACEHOLDERS["receiver"]),
                    subject=message_headers.get("subject", UNKNOWN_PLACEHOLDERS["subject"]),
                    body_short=truncate_text(MessageParser.body_from_message(match), BODY_SHORT_THRESHOLD),
                    date=message_headers.get("date", UNKNOWN_PLACEHOLDERS["date"]),
                    flags=MessageParser.flags_from_message(match),
                    attachments=MessageParser.attachments_from_message(match)
                ))
        except Exception as e:
            raise IMAPManagerException(f"Error while fetching emails `{sequence_set}` in folder `{self.__searched_emails.folder}`, fetched email length was `{len(emails)}`: `{str(e)}`") from None

        return Mailbox(folder=self.__searched_emails.folder, emails=emails, total=uids_len)

    def get_email_flags(self, sequence_set: str) -> list[Flags]:
        """
        Retrieve flags associated with a specific email.

        Args:
            sequence_set (str): The sequence set of the email to fetch flags for.

        Returns:
            list[Flags]: A list of Flags objects representing the flags associated with the email.

        Example:
            >>> get_email_flags("1")
            [Flags(uid="1", flags=["\\Seen", "\\Answered"])]
            >>> get_email_flags("1:3")
            [Flags(uid="1", flags=["\\Seen", "\\Answered"]), Flags(uid="2", flags=["\\Answered"]), Flags(uid="3", flags=["\\Flagged"])]
            >>> get_email_flags("1,3:4")
            [Flags(uid="1", flags=["\\Seen", "\\Answered"]), Flags(uid="3", flags=["\\Flagged"]), Flags(uid="4", flags=["\\Flagged"])]
            >>> get_email_flags("1:*") # In this case, mailbox has 3 emails
            [Flags(uid="1", flags=["\\Seen", "\\Answered"]), Flags(uid="2", flags=["\\Answered"]), Flags(uid="3", flags=["\\Flagged"])]
            >>> get_email_flags("1,3:*") # In this case, mailbox has 4 emails
            [Flags(uid="1", flags=["\\Seen", "\\Answered"]), Flags(uid="3", flags=["\\Flagged"]), Flags(uid="4", flags=["\\Flagged"])]

        """
        if self.state != "SELECTED":
            # Since uid's are unique within each mailbox, we can't just select INBOX
            # or something like that if there is no mailbox selected.
            raise IMAPManagerException("Folder should be selected before fetching flags.")

        try:
            status, result = self.uid(
                'FETCH', 
                sequence_set,
                '(FLAGS)'
            )
        except Exception as e:
            raise IMAPManagerException(f"Error while fetching email flags: {str(e)}") from None

        try:
            flags_list = []
            if status != 'OK':
                raise IMAPManagerException(f"Error while fetching flags of email `{sequence_set}`: `{status}`")
            
            matches = MessageParser.messages(result[1])
            for match in matches:
                flags_list.append(Flags(
                    uid=MessageParser.uid_from_message(match),
                    flags=MessageParser.flags_from_message(match)
                ))
        except Exception as e:
            raise IMAPManagerException(f"Error while fetching flags of email `{sequence_set}`: `{status}`") from None

        return flags_list or []
    
    def get_email_content(
        self,
        uid: str,
        folder: str
    ) -> EmailWithContent:
        """
        Retrieve full content of a specific email. 

        Args:
            uid (str): Unique identifier of the email.
            folder (str): Folder containing the email.

        Returns:
            EmailWithContent: Dataclass containing the email content.

        Example:
            >>> get_email_content("1", "INBOX")
            EmailWithContent(uid="1", sender="a@gmail.com", ...)

        Notes:
            - Replaces inline attachments with data URLs to display them inline
            and if an error occurs while replacing the inline attachments, the
            replacement operation will be skipped without raising an error but
            it will be logged as a warning.
            - Marks the email as "Seen" if it is not already and if an error 
            occurs while marking the email, the mark operation will be skipped
            without raising an error but it will be logged as a warning.
        """
        status, _ = self.select(folder, readonly=True)
        if status != 'OK':
            raise IMAPManagerException(f"Error while selecting folder `{folder}`: `{status}`")

        # Get body and attachments
        body, attachments = "", []
        try:
            status, message = self.uid('fetch', uid, '(RFC822)')
            if status != 'OK':
                raise IMAPManagerException(f"Error while getting email `{uid}`'s content in folder `{folder}`: `{status}`")

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
            raise IMAPManagerException(f"There was a problem with getting email `{uid}`'s content in folder `{folder}`: `{str(e)}`") from None

        try:
            # Replacing inline attachments
            if attachments:
                inline_cids = MessageParser.inline_attachment_cids_from_message(body)
                if inline_cids:
                    for attachment in attachments:
                        if attachment.cid in inline_cids or attachment.name in inline_cids:
                            body = body.replace(
                                f'cid:{attachment.cid}',
                                f'data:{attachment.type};base64,{attachment.data}'
                            )
                else:
                    print(f"No inline attachments found for found attachments of email `{uid}`'s content in folder `{folder}`.")
        except Exception as e:
            # If there is a problem with inline attachments
            # just ignore them.
            print(f"An error occurred while replacing inline attachments: `{str(e)}` of email `{uid}`'s content in folder `{folder}`.")
            pass

        try:
            self.mark_email(Mark.SEEN, uid, folder)
        except Exception as e:
            # If there is a problem with marking the email as seen
            # just ignore it.
            print(f"An error occurred while marking email as seen: `{str(e)}` of email `{uid}`'s content in folder `{folder}`.")
            pass

        return EmailWithContent(
            uid=uid,
            sender=message.get("From", UNKNOWN_PLACEHOLDERS["sender"]),
            receiver=message.get("To", UNKNOWN_PLACEHOLDERS["receiver"]),
            subject=message.get("Subject", UNKNOWN_PLACEHOLDERS["subject"]),
            body=body,
            date=message.get("Date", UNKNOWN_PLACEHOLDERS["date"]),
            cc=message.get("Cc", ""),
            bcc=message.get("Bcc", ""),
            message_id=message.get("Message-Id", ""),
            metadata={
                "In-Reply-To": message.get("In-Reply-To", ""),
                "References": message.get("References", "")
            },
            flags=self.get_emails_flags(uid)[0].flags or [],
            attachments=attachments
        )
        
    def __mark_email(
        self,
        mark: Mark,
        sequence_set: str,
        command: str,
        folder: str,
        success_msg: str,
        err_msg: str
    ) -> IMAPCommandResult:
        """
        Mark an email with a specific flag with given `command`.

        Args:
            mark (str): Flag to apply to the email.
            sequence_set (str): Sequence set of emails to mark.
            command (str): IMAP command to apply the flag like 
            `+FLAGS` or `-FLAGS`.
            folder (str): Folder containing the email.
            success_msg (str): Success message to display.
            err_msg (str): Error message to display.

        Returns:
            IMAPCommandResult: A tuple containing:
                - A bool indicating whether the email was marked successfully.
                - A string containing a success message or an error message.

        Example:
            >>> __mark_email(Mark.Seen, "1", "+FLAGS", "INBOX", "Email marked as seen", "Error while marking email as seen")
            True, "Email(s) `1` marked with `seen` successfully."
            >>> __mark_email(Mark.Flagged, "1:3", "+FLAGS", "INBOX", "Email marked as flagged", "Error while marking email as flagged")
            True, "Email(s) `1:3` marked with `flagged` successfully."
            >>> __mark_email(Mark.Seen, "1,3:5", "+FLAGS", "INBOX", "Email marked as seen", "Error while marking email as seen")
            True, "Email(s) `1,3:5` marked with `seen` successfully."
            >>> __mark_email(Mark.Answered, "1:*", "+FLAGS", "INBOX", "Email marked as seen", "Error while marking email as seen")
            True, "Email(s) `1:*` marked with `answered` successfully."
            >>> __mark_email(Mark.Flagged, "1,3:*", "+FLAGS", "INBOX", "Email marked as flagged", "Error while marking email as flagged")
            True, "Email(s) `1,3:*` marked with `flagged` successfully."

        References:
            uid_range is a sequence set as defined in RFC 9051:
            sequence-set = Example: a message sequence number set of
                        2,4:7,9,12:* for a mailbox with 15 messages is
                        equivalent to 2,4,5,6,7,9,12,13,14,15
                        Example: a message sequence number set of
                        *:4,5:7 for a mailbox with 10 messages is
                        equivalent to 10,9,8,7,6,5,4,5,6,7 and MAY
                        be reordered and overlap coalesced to be
                        4,5,6,7,8,9,10.
            - https://datatracker.ietf.org/doc/html/rfc9051#name-formal-syntax
        """        
        status, _ = self.select(folder)
        if status != 'OK':
            raise IMAPManagerException(f"Error while selecting folder `{folder}`: `{status}`")

        mark = mark.lower()
        mark_list = [m.value for m in Mark]
        if not mark or mark not in mark_list:
            raise IMAPManagerException(
                f"Unsupported mark: `{mark}`. Please use one of the following: `{', '.join(mark_list)}`"
            )

        mark_result = self.__parse_command_result(
            self.uid(
                'STORE', 
                sequence_set,
                command,
                mark
            ),
            success_msg,
            err_msg
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
        mark: Mark,
        sequence_set: str,
        folder: str = Folder.Inbox
    ) -> IMAPCommandResult:
        """
        Mark an email with a specific flag.

        Args:
            mark (str): Flag to apply to the email.
            sequence_set (str): Sequence set of emails to mark.
            folder (str, optional): Folder containing the email. 
            Defaults to "inbox".

        Returns:
            IMAPCommandResult: A tuple containing:
                - A bool indicating whether the email was marked successfully.
                - A string containing a success message or an error message.

        Example:
            >>> mark_email(Mark.Seen, "1") # Marks email with UID 1 from INBOX
            True, "Email(s) `1` marked with `seen` successfully."
            >>> mark_email(Mark.Seen, "1:3") # Marks email with UID 1,2,3 from INBOX
            True, "Email(s) `1:3` marked with `seen` successfully."
            >>> mark_email(Mark.Seen, "1,3:5") # Marks email with UID 1 and 3,4,5 from INBOX
            True, "Email(s) `1,3:5` marked with `seen` successfully."
            >>> mark_email(Mark.Seen, "1:*") # Marks all emails in the INBOX
            True, "Email(s) `1:*` marked with `seen` successfully."
            >>> mark_email(Mark.Seen, "1,3:*") # Marks all emails in the INBOX, except email with UID 2
            True, "Email(s) `1,3:*` marked with `seen` successfully."

        References:
            uid_range is a sequence set as defined in RFC 9051:
            sequence-set = Example: a message sequence number set of
                        2,4:7,9,12:* for a mailbox with 15 messages is
                        equivalent to 2,4,5,6,7,9,12,13,14,15
                        Example: a message sequence number set of
                        *:4,5:7 for a mailbox with 10 messages is
                        equivalent to 10,9,8,7,6,5,4,5,6,7 and MAY
                        be reordered and overlap coalesced to be
                        4,5,6,7,8,9,10.
            - https://datatracker.ietf.org/doc/html/rfc9051#name-formal-syntax
        """
        return self.__mark_email(
            mark,
            sequence_set,
            "+FLAGS",
            folder if isinstance(folder, str) else folder.decode("utf-8"),
            f"Email(s) `{sequence_set}` in `{folder}` marked with `{mark}` successfully.",
            f"There was an error while marking the email(s) `{sequence_set}` in `{folder}` with `{mark}`."
        )

    def unmark_email(
        self,
        mark: Mark,
        sequence_set: str,
        folder: str = Folder.Inbox,
    ) -> IMAPCommandResult:
        """
        Unmark an email with a specific flag.

        Args:
            mark (str): Flag to remove from the email.
            sequence_set (str): Sequence set of emails to unmark.
            folder (str, optional): Folder containing the email. Defaults to "inbox".

        Returns:
            IMAPCommandResult: A tuple containing:
                - A bool indicating whether the email was unmarked successfully.
                - A string containing a success message or an error message.

        Example:
            >>> unmark_email(Mark.Seen, "1") # Unmarks email with UID 1 from INBOX
            True, "Email(s) `1` unmarked with `seen` successfully."
            >>> unmark_email(Mark.Seen, "1:3") # Unmarks email with UID 1,2,3 from INBOX
            True, "Email(s) `1:3` unmarked with `seen` successfully."
            >>> unmark_email(Mark.Seen, "1,3:5") # Unmarks email with UID 1 and 3,4,5 from INBOX
            True, "Email(s) `1,3:5` unmarked with `seen` successfully."
            >>> unmark_email(Mark.Seen, "1:*") # Unmarks all emails in the INBOX
            True, "Email(s) `1:*` unmarked with `seen` successfully."
            >>> unmark_email(Mark.Seen, "1,3:*") # Unmarks all emails in the INBOX, except email with UID 2
            True, "Email(s) `1,3:*` unmarked with `seen` successfully."

        References:
            uid_range is a sequence set as defined in RFC 9051:
            sequence-set = Example: a message sequence number set of
                        2,4:7,9,12:* for a mailbox with 15 messages is
                        equivalent to 2,4,5,6,7,9,12,13,14,15
                        Example: a message sequence number set of
                        *:4,5:7 for a mailbox with 10 messages is
                        equivalent to 10,9,8,7,6,5,4,5,6,7 and MAY
                        be reordered and overlap coalesced to be
                        4,5,6,7,8,9,10.
            - https://datatracker.ietf.org/doc/html/rfc9051#name-formal-syntax
        """
        return self.__mark_email(
            mark,
            sequence_set,
            "-FLAGS",
            folder,
            f"Email(s) `{sequence_set}` in `{folder}` unmarked with `{mark}` successfully.",
            f"There was an error while unmarking the email(s) `{sequence_set}` in `{folder}` with `{mark}`."
        )

    def move_email(self,
        source_folder: str,
        destination_folder: str,
        sequence_set: str,
    ) -> IMAPCommandResult:
        """
        Move an email from one folder to another.

        Args:
            source_folder (str): Current folder of the email.
            destination_folder (str): Target folder to move the email to.
            sequence_set (str): Sequence set of emails to move.

        Returns:
            IMAPCommandResult: A tuple containing:
                - A bool indicating whether the email was moved successfully.
                - A string containing a success message or an error message.

        Example:
            >>> move_email("INBOX", "ARCHIVE", "1") # Moves email with UID 1 from INBOX to SENT
            True, "Email(s) `1` moved successfully from `INBOX` to `ARCHIVE`."
            >>> move_email("INBOX", "ARCHIVE", "1:3") # Moves email with UID 1,2,3 from INBOX to SENT
            True, "Email(s) `1:3` moved successfully from `INBOX` to `ARCHIVE`."
            >>> move_email("INBOX", "ARCHIVE", "1,3:5") # Moves email with UID 1 and 3,4,5 from INBOX to SENT
            True, "Email(s) `1,3:5` moved successfully from `INBOX` to `ARCHIVE`."
            >>> move_email("INBOX", "ARCHIVE", "1:*") # Moves all emails in the INBOX to ARCHIVE folder
            True, "Email(s) `1:*` moved successfully from `INBOX` to `ARCHIVE`."
            >>> move_email("INBOX", "ARCHIVE", "1,3:*") # Moves all emails in the INBOX to ARCHIVE folder, except email with UID 2
            True, "Email(s) `1,3:*` moved successfully from `INBOX` to `ARCHIVE`."
            
        References:
            uid_range is a sequence set as defined in RFC 9051:
            sequence-set = Example: a message sequence number set of
                        2,4:7,9,12:* for a mailbox with 15 messages is
                        equivalent to 2,4,5,6,7,9,12,13,14,15
                        Example: a message sequence number set of
                        *:4,5:7 for a mailbox with 10 messages is
                        equivalent to 10,9,8,7,6,5,4,5,6,7 and MAY
                        be reordered and overlap coalesced to be
                        4,5,6,7,8,9,10.
            - https://datatracker.ietf.org/doc/html/rfc9051#name-formal-syntax
        """
        self.__check_folder_names([source_folder, destination_folder])

        if source_folder == destination_folder:
            return IMAPCommandResult(success=True, message=f"Destination folder `{destination_folder}` is the same as the source folder `{source_folder}`.")

        status, _ = self.select(source_folder)
        if status != "OK":
            raise IMAPManagerException(f"Error while selecting folder `{source_folder}`: `{status}`")

        succes_msg = f"Email(s) `{sequence_set}` moved successfully from `{source_folder}` to `{destination_folder}`."
        err_msg = f"Failed to move email(s) `{sequence_set}` from `{source_folder}` to `{destination_folder}`."

        move_result = self.__parse_command_result(
            self.uid(
                'MOVE', 
                sequence_set,
                self.__encode_folder(destination_folder)
            ),
            succes_msg,
            err_msg
        )

        if move_result[0]:
            return self.__parse_command_result(
                self.expunge(),
                succes_msg,
                err_msg
            )

        return move_result

    def copy_email(self,
        source_folder: str,
        destination_folder: str,
        sequence_set: str,
    ) -> IMAPCommandResult:
        """
        Create a copy of an email in another folder.

        Args:
            source_folder (str): Current folder of the email.
            destination_folder (str): Target folder to copy the email to.
            sequence_set (str): Sequence set of emails to copy.

        Returns:
            IMAPCommandResult: A tuple containing:
                - A bool indicating whether the email was copied successfully.
                - A string containing a success message or an error message.

        Example:
            >>> copy_email("INBOX", "ARCHIVE", "1") # Copies emails with UID 1 to ARCHIVE from INBOX.
            True, "Email(s) `1` copied successfully from `INBOX` to `ARCHIVE`."
            >>> copy_email("INBOX", "ARCHIVE", "1:3") # Copies emails with UID 1,2,3 to ARCHIVE from INBOX.
            True, "Email(s) `1:3` copied successfully from `INBOX` to `ARCHIVE`."
            >>> copy_email("INBOX", "ARCHIVE", "1,3:5") # Copies email with UID 1 and 3,4,5 to ARCHIVE from INBOX.
            True, "Email(s) `1,3:5` copied successfully from `INBOX` to `ARCHIVE`."
            >>> copy_email("INBOX", "ARCHIVE", "1:*") # Copies all emails in the INBOX to ARCHIVE folder
            True, "Email(s) `1:*` copied successfully from `INBOX` to `ARCHIVE`."
            >>> copy_email("INBOX", "ARCHIVE", "1,3:*") # Copies all emails in the INBOX to ARCHIVE folder, except email with UID 2
            True, "Email(s) `1,3:*` copied successfully from `INBOX` to `ARCHIVE`."
            
        References:
            uid_range is a sequence set as defined in RFC 9051:
            sequence-set = Example: a message sequence number set of
                        2,4:7,9,12:* for a mailbox with 15 messages is
                        equivalent to 2,4,5,6,7,9,12,13,14,15
                        Example: a message sequence number set of
                        *:4,5:7 for a mailbox with 10 messages is
                        equivalent to 10,9,8,7,6,5,4,5,6,7 and MAY
                        be reordered and overlap coalesced to be
                        4,5,6,7,8,9,10.
            - https://datatracker.ietf.org/doc/html/rfc9051#name-formal-syntax
        """
        self.__check_folder_names([source_folder, destination_folder])

        status, _ = self.select(source_folder)
        if status != "OK":
            raise IMAPManagerException(f"Error while selecting folder `{source_folder}`: `{status}`")

        succes_message = f"Email(s) `{sequence_set}` copied successfully from `{source_folder}` to `{destination_folder}`."
        err_msg = f"Failed to copy email(s) `{sequence_set}` from `{source_folder}` to `{destination_folder}`."

        copy_result = self.__parse_command_result(
            self.uid(
                'COPY',
                sequence_set,
                self.__encode_folder(destination_folder)
            ),
            succes_message,
            err_msg
        )

        if copy_result[0]:
            return self.__parse_command_result(
                self.expunge(),
                succes_message,
                err_msg
            )

        return copy_result

    def delete_email(self, folder: str, sequence_set: str) -> IMAPCommandResult:
        """
        Delete an email from a specific folder.

        Args:
            folder (str): Folder containing the email.
            sequence_set (str): Sequence set of emails to delete.

        Returns:
            IMAPCommandResult: A tuple containing:
                - A bool indicating whether the email was deleted successfully.
                - A string containing a success message or an error message.

        Example:
            >>> delete_email("INBOX", "1") # Deletes email with UID 1
            True, "Email(s) `1` deleted from `INBOX` successfully."
            >>> delete_email("INBOX", "1:3") # Deletes email with UID 1,2,3
            True, "Email(s) `1:3` deleted from `INBOX` successfully."
            >>> delete_email("INBOX", "1,3:5") # Deletes email with UID 1 and 3,4,5
            True, "Email(s) `1,3:5` deleted from `INBOX` successfully."
            >>> delete_email("INBOX", "1:*") # Deletes all emails in the folder
            True, "Email(s) `1:*` deleted from `INBOX` successfully."
            >>> delete_email("INBOX", "1,3:*") # Deletes all emails in the folder except email with UID 2
            True, "Email(s) `1,3:*` deleted from `INBOX` successfully."

        References:
            uid_range is a sequence set as defined in RFC 9051:
            sequence-set = Example: a message sequence number set of
                        2,4:7,9,12:* for a mailbox with 15 messages is
                        equivalent to 2,4,5,6,7,9,12,13,14,15
                        Example: a message sequence number set of
                        *:4,5:7 for a mailbox with 10 messages is
                        equivalent to 10,9,8,7,6,5,4,5,6,7 and MAY
                        be reordered and overlap coalesced to be
                        4,5,6,7,8,9,10.
            - https://datatracker.ietf.org/doc/html/rfc9051#name-formal-syntax
        """
        self.__check_folder_names(folder)
        
        try:
            trash_mailbox_name = self.find_matching_folder(Folder.Trash)
            if folder != trash_mailbox_name:
                status, _ = self.move_email(folder, sequence_set, trash_mailbox_name)
                if not status:
                    raise IMAPManagerException(
                        f"Error while moving email(s) `{sequence_set}` to trash folder for deletion."
                    )
        except Exception as e:
            raise IMAPManagerException(
                f"Error while moving email(s) `{sequence_set}` to trash folder for deletion: `{str(e)}`."
            ) from None

        status, _ = self.select(trash_mailbox_name)
        if status != 'OK':
            raise IMAPManagerException(
                f"Error while selecting trash folder for deletion: `{status}`."
            )

        success_msg = f"Email(s) `{sequence_set}` deleted from `{folder}` successfully."
        err_msg = f"There was an error while deleting the email(s) `{sequence_set}` from `{folder}`."

        delete_result = self.__parse_command_result(
            self.uid(
                'STORE', 
                sequence_set,
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

        Example:
            >>> create_folder("RED")
            (True, "Folder `RED` created successfully.")
            >>> create_folder("BLUE", "COLORS") # BLUE will be created under COLORS like `COLORS/BLUE`
            (True, "Folder `BLUE` created successfully.")
            >>> create_folder("DARKBLUE", "COLORS/DARK") # DARKBLUE will be created under DARK like `COLORS/DARK/DARKBLUE`
            (True, "Folder `DARKBLUE` created successfully.")
        """
        self.__check_folder_names([folder_name, parent_folder])

        if parent_folder:
            folder_name = f"{parent_folder}/{folder_name}"

        encoded_folder_name = self.__encode_folder(folder_name)

        return self.__parse_command_result(
            self.create(encoded_folder_name),
            f"Folder `{folder_name}` created successfully.",
            f"There was an error while creating folder `{folder_name}`."
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

        Example:
            >>> delete_folder("RED")
            (True, "Folder `RED` deleted successfully.")
        """
        self.__check_folder_names(folder_name)

        encoded_folder_name = self.__encode_folder(folder_name)

        return self.__parse_command_result(
            self.delete(encoded_folder_name),
            f"Folder `{folder_name}` deleted successfully.",
            f"There was an error while deleting folder `{folder_name}`."
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

        Example:
            >>> move_folder("RED", "COLORS") # RED will be moved under COLORS like `COLORS/RED`
            (True, "Folder `RED` moved to `COLORS` successfully.")
        """
        self.__check_folder_names([folder_name, destination_folder])

        if "/" in folder_name:
            destination_folder = f"{destination_folder}/{folder_name.split("/")[-1]}"

        encoded_folder_name = self.__encode_folder(folder_name)
        encoded_destination_folder = self.__encode_folder(destination_folder)

        return self.__parse_command_result(
            self.rename(
                encoded_folder_name,
                encoded_destination_folder
            ),
            f"Folder `{folder_name}` moved to `{destination_folder}` successfully.",
            f"There was an error while moving folder `{folder_name}` to `{destination_folder}`."
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

        Example:
            >>> rename_folder("RED", "BLUE")
            (True, "Folder `RED` renamed to `BLUE` successfully.")
        """
        self.__check_folder_names([folder_name, new_folder_name])

        if "/" in folder_name:
            new_folder_name = folder_name.replace(
                folder_name.split("/")[-1],
                new_folder_name
            )
        
        encoded_folder_name = self.__encode_folder(folder_name)
        encoded_new_folder_name = self.__encode_folder(new_folder_name)

        return self.__parse_command_result(
            self.rename(
                encoded_folder_name, 
                encoded_new_folder_name
            ),
            f"Folder `{folder_name}` renamed to `{new_folder_name}` successfully.",
            f"There was an error while renaming folder `{folder_name}` to `{new_folder_name}`."
        )

__all__ = [
    "IMAPManager", 
    "IMAPCommandResult", 
    "IMAPManagerException", 
    "IMAPManagerLoggedOutException",
    "Mark",
    "Folder"
]
