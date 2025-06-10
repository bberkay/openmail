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
- Custom error handling.

Primarily designed for use by the `Openmail` class.

Author: <berkaykayaforbusiness@outlook.com>
"""

from email.message import EmailMessage
import imaplib
import re
import threading
import time
from zoneinfo import ZoneInfo
from typing import Callable, override, List
from enum import Enum
from ssl import SSLContext
from types import MappingProxyType
from datetime import datetime, timedelta
from dataclasses import dataclass
from email.utils import parsedate_to_datetime

from .parser import MessageDecoder, MessageParser
from .utils import (
    add_quotes_if_str,
    convert_to_imap_date,
    extract_domain,
    choose_positive,
    extract_email_addresses,
)
from .utils import contains_non_ascii
from .types import SearchCriteria, Attachment, Mailbox, Email, Flags, Mark, Folder

"""
Exceptions
"""
class IMAPManagerException(Exception):
    """Custom exception for IMAPManager class."""

class IMAPManagerLoggedOutException(IMAPManagerException):
    """Custom exception for when the IMAPManager is logged out
    while trying to perform an action that requires authentication."""

"""
Types, that are only used in this module
"""
type IMAPCommandResult = tuple[bool, str]

"""
General consts, avoid changing
"""
IMAP_SERVERS = MappingProxyType(
    {
        "gmail": "imap.gmail.com",
        "yahoo": "imap.mail.yahoo.com",
        "outlook": "outlook.office365.com",
        "hotmail": "outlook.office365.com",
        "yandex": "imap.yandex.com",
    }
)
IMAP_PORT = 993

# Regex Patterns
SEQUENCE_SET_PATTERN = re.compile(
    r"""
    ^(
        (\d+(,|:))*\d+$ |
        \*:((\d+(,|:))*\d+)?$ |
        ((\d+(,|:))*\d+:)?\*$
    )$
""",
    re.VERBOSE,
)

# Typo prevention
CRLF = b"\r\n"
INBOX = "INBOX"

MARK_LIST = [str(m).lower() for m in Mark]
FOLDER_LIST = [str(f).lower() for f in Folder]

"""
Custom consts
"""
GET_EMAILS_OFFSET_START = 1
GET_EMAILS_OFFSET_END = 10
SHORT_BODY_TEXT_CHUNK_SIZE = 4096  # in bytes
EMAIL_LOOKBACK_WINDOW = 5  # minutes
# Character counts
SHORT_BODY_MAX_LENGTH = 100
MAX_FOLDER_NAME_LENGTH = 1024
# Timers in seconds
CONN_TIMEOUT = 30
IDLE_TIMEOUT = 29 * 60
JOIN_TIMEOUT = 1
WAIT_RESPONSE_TIMEOUT = 30
IDLE_ACTIVATION_INTERVAL = 60


class IMAPManager(imaplib.IMAP4_SSL):
    """
    IMAPManager extends the `imaplib.IMAP4` class.
    Overrides `login`, `logout`, `shutdown`, `select`,
    and `__simple_command`. Provides additional features
    especially idling and listening exists responses on
    different threads. Mainly used in `Openmail` class.
    """

    @dataclass
    class IdleSession:
        """Dataclass for storing active idle status."""

        tag: bytes
        start_time: float

    class WaitResponse(Enum):
        """
        Enum for waiting for a response from the server.
        These are not the all possible responses but the ones `IMAPManager`
        is interested in.

        References:
            - https://datatracker.ietf.org/doc/html/rfc9051#name-idle-command
            - https://datatracker.ietf.org/doc/html/rfc9051#name-exists-response
            - https://datatracker.ietf.org/doc/html/rfc9051#name-bye-response
        """

        IDLE = "IDLE"
        DONE = "DONE"
        EXISTS = "EXISTS"
        BYE = "BYE"

    WAIT_RESPONSE_LIST = [f for f in WaitResponse]

    @dataclass
    class SearchedEmails:
        """Dataclass for storing searched emails."""
        uids: List[str]
        count: int
        folder: str
        search_query: str

    def __init__(
        self,
        email_address: str,
        password: str,
        host: str = "",
        port: int = IMAP_PORT,
        *,
        ssl_context: SSLContext | None = None,
        timeout: int = CONN_TIMEOUT,
        enable_idle_optimization: bool = False,
        listen_new_messages: bool = False,
    ):
        self._host = host or self._find_imap_server(email_address)
        self._port = port or IMAP_PORT

        # Idle and Readline variables
        self._idle_optimization = enable_idle_optimization
        self._listen_new_messages = listen_new_messages
        self._current_idle: IMAPManager.IdleSession | None = None
        self._idle_activation_countdown = 0
        self._is_idle_activation_countdown_continue = False
        self._wait_response: IMAPManager.WaitResponse | None = None
        self._previous_mailbox_size = 0
        self._new_message_timestamps: List[datetime] = []
        self._readline_event = threading.Event()
        self._readline_thread = threading.Thread(
            target=self._start_reading_lines, daemon=True
        )
        self._idling_event = threading.Event()
        self._idling_thread = threading.Thread(
            target=self._start_optimized_idle_lifecycle
            if enable_idle_optimization
            else self._start_idle_lifecycle,
            daemon=True,
        )
        self._release_idle_loops_event = threading.Event()
        self._idle_command_in_process_event = threading.Event()
        self._idle_command_in_process_event.set()

        super().__init__(
            self._host,
            self._port,
            ssl_context=ssl_context,
            timeout=choose_positive(timeout, CONN_TIMEOUT),
        )

        self._is_idle_supported = self.is_supported("IDLE")
        self._searched_emails: IMAPManager.SearchedEmails | None = None
        self._hierarchy_delimiter = ""

        self.login(email_address, password)

    @property
    def hierarchy_delimiter(self) -> str:
        """Returns the server's folder hierarchy delimiter character (e.g. '/', '.')."""
        return self._hierarchy_delimiter

    def _find_imap_server(self, email_address: str) -> str:
        """
        Determines the IMAP server address for a given email address.

        Args:
            email_address (str): The email address for which to find the
            corresponding IMAP server.

        Returns:
            str: The IMAP server address associated with the email's domain.

        Example:
            >>> email_address = "user@gmail.com"
            >>> self._find_imap_server(email_address)
            "imap.gmail.com"
            >>> email_address = "user@unknown.com"
            >>> self._find_imap_server(email_address)
            IMAPManagerException: Unsupported email domain

        Raises:
            IMAPManagerException: If the email domain is not supported or
            not found in the IMAP_SERVERS mapping.
        """
        try:
            return IMAP_SERVERS[extract_domain(email_address)]
        except KeyError:
            raise IMAPManagerException("Unsupported email domain") from None

    def _parse_command_result(
        self,
        result: tuple[str, List[bytes | None] | List[bytes]],
        success_message: str = "",
        failure_message: str = "",
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
            >>> self._parse_command_result(result,
                    success_message="Operation successful",
                    failure_message="Login failed"
                )
            (True, "Operation successful")
            >>> result = ("NO", [b"Invalid credentials"])
            >>> self._parse_command_result(result,
                    success_message="Operation successful",
                    failure_message="Login failed"
                )
            (False, "Login failed: Invalid credentials")
            >>> result = ("BYE", [b"Logout successful"])
            >>> self._parse_command_result(result,
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
            if result[0] == "OK" or result[0] == "BYE":
                return True, success_message or (result[1][0] or b"").decode("utf-8")
            else:
                return False, failure_message + ": " + (result[1][0] or b"").decode(
                    "utf-8"
                )
        except Exception as e:
            raise IMAPManagerException(
                f"There was an error while parsing command `{result}` result: {str(e)}"
            ) from None

    def _enable_utf8(self) -> bool:
        """Enable UTF8 if the server supports it. Does not raise any error
        if not found. Typically used right after login."""
        is_success = False
        capability_result = self.capability()
        if capability_result[0] != "OK":
            raise IMAPManagerException(
                f"Could not receive capability list to enable utf8: {capability_result[1]}"
            )

        if [b"UTF8=ACCEPT" in capabilities for capabilities in capability_result[1]]:
            utf8_enable_result = self._simple_command("ENABLE", "UTF8=ACCEPT")
            is_success = utf8_enable_result[0] == "OK"
            if not is_success:
                print(f"Could not enable UTF-8: {utf8_enable_result[1]}")

        return is_success

    def _set_hierarchy_delimiter(self) -> bool:
        """Find the hierarchy delimiter from NAMESPACE and set it.
        Raises an error if not found. Typically used right after login."""
        # https://datatracker.ietf.org/doc/html/rfc9051#name-namespace-command
        status, message = self.namespace()
        if status != "OK":
            raise IMAPManagerException(
                f"Could not receive namespace response to find hierarchy delimiter: {message}"
            )

        self._hierarchy_delimiter = MessageParser.get_hierarchy_delimiter(
            MessageParser.group_messages(message)[0]
        )
        if not self._hierarchy_delimiter:
            raise IMAPManagerException("Could not parse hierarchy delimiter")

        return True

    # Overrides of IMAP4 Command functions to handling IDLING

    @staticmethod
    def handle_idle(imap4_cmd: Callable):
        """
        Before calling imap4 command, handles the continuous IDLE mode and
        raise IMAPManagerLoggedOutException if the IMAPManager is logged
        out because of timeout.
        """

        def wrapper(self, *args, **kwargs):
            def is_logout_error(err_msg: str) -> bool:
                """Checks the imap connection whether it still connected with err_msg."""
                return self.state == "LOGOUT" and any(
                    item.lower() in err_msg for item in ("AUTH", "SELECTED")
                )

            if not self._idle_command_in_process_event.is_set():
                print("Command: ", imap4_cmd.__name__, "Already in idle waiting...")
                """
                For `_idle_command_in_process_event` to be set,
                `_wait_response` must be equal to `WaitResponse.IDLE`,
                Since a TimeoutError will be raised if it is not set
                within WAIT_RESPONSE_TIMEOUT, there is no need to
                provide any timeout to this wait or to consider anything
                further.
                """
                self._idle_command_in_process_event.wait()

            was_idle_before_call = (
                self.is_idle() or self.is_idle_activation_countdown_continue()
            )
            # print("Was Idle Before Call: ", was_idle_before_call, "Command: ", imap4_cmd.__name__)
            try:
                if was_idle_before_call:
                    self.done()
                else:
                    self._release_readline_for_imap4()
            except Exception as e:
                if is_logout_error(str(e).lower()):
                    raise IMAPManagerLoggedOutException(
                        f"To perform this command `{imap4_cmd.__name__}`, the IMAPManager must be logged in: {str(e)}"
                    ) from None
                else:
                    print(f"Unexpected error while leaving IDLE mode: {str(e)}")
                    # Even if leaving IDLE has failed, terminate current idle session.
                    self._handle_done_response()
                    print(
                        "Active IDLE session set to None and threads stopped forcefully."
                    )

            try:
                result = imap4_cmd(self, *args, **kwargs)
            except Exception as e:
                if is_logout_error(str(e).lower()):
                    raise IMAPManagerLoggedOutException(
                        f"To perform this command `{imap4_cmd.__name__}`, the IMAPManager must be logged in: {str(e)}"
                    ) from None
                else:
                    raise IMAPManagerException(
                        f"Error while running command `{imap4_cmd.__name__}`: {str(e)}`"
                    ) from e

            # Restore IDLE mode.
            try:
                # print("Restore - ", "Was Idle Before Call: ", was_idle_before_call, "Command: ", imap4_cmd.__name__)
                if was_idle_before_call and imap4_cmd.__name__.lower() != "logout":
                    self.idle()
                # else:
                #    self._resume_readline_for_imapmanager()
            except Exception as e:
                print(f"Unexpected error while restoring IDLE mode: {str(e)}")
                was_idle_before_call = False
                print(
                    "IDLE mode could not be restored. IDLE mode completely disabled. Run `idle()` to re-enable IDLE mode if needed."
                )
                raise IMAPManagerException(str(e))

            return result

        return wrapper

    @override
    @handle_idle
    def append(self, mailbox: str, flags: str, date_time: str, message):
        return super().append(mailbox, flags, date_time, message)

    @override
    @handle_idle
    def capability(self):
        return super().capability()

    @override
    @handle_idle
    def check(self):
        return super().check()

    @override
    @handle_idle
    def close(self):
        return super().close()

    @override
    @handle_idle
    def copy(self, message_set: str, new_mailbox: str):
        return super().copy(message_set, new_mailbox)

    @override
    @handle_idle
    def create(self, mailbox: str):
        return super().create(mailbox)

    @override
    @handle_idle
    def delete(self, mailbox: str):
        return super().delete(mailbox)

    @override
    @handle_idle
    def deleteacl(self, mailbox: str, who: str):
        return super().deleteacl(mailbox, who)

    @override
    @handle_idle
    def enable(self, capability: str):
        return super().enable(capability)

    @override
    @handle_idle
    def expunge(self):
        return super().expunge()

    @override
    @handle_idle
    def fetch(self, message_set, message_parts: str):
        return super().fetch(message_set, message_parts)

    @override
    @handle_idle
    def getacl(self, mailbox: str):
        return super().getacl(mailbox)

    @override
    @handle_idle
    def getannotation(self, mailbox: str, entry: str, attribute: str):
        return super().getannotation(mailbox, entry, attribute)

    @override
    @handle_idle
    def getquota(self, root: str):
        return super().getquota(root)

    @override
    @handle_idle
    def getquotaroot(self, mailbox: str):
        return super().getquotaroot(mailbox)

    @override
    @handle_idle
    def list(self, directory: str = '""', pattern: str = "*"):
        return super().list(directory, pattern)

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
            - 'password' will be quoted.
        """
        login_result = None
        if contains_non_ascii(user) or contains_non_ascii(password):
            login_result = self.authenticate(
                "PLAIN", lambda x: bytes("\x00" + user + "\x00" + password, "utf-8")
            )
        else:
            login_result = super().login(user, password)

        if login_result[0] != "OK":
            raise IMAPManagerException(
                f"Could not logged in to the target IMAP server: {login_result[1]}"
            )

        self._enable_utf8()
        self._set_hierarchy_delimiter()

        return (True, "Succesfully logged in to the target IMAP server")

    @override
    @handle_idle
    def logout(self) -> IMAPCommandResult:
        """
        Logs out from the IMAP server and closes any open mailboxes.

        Returns:
            IMAPCommandResult: A tuple containing:
                - A bool indicating whether the logout was successful.
                - A string containing a success message or an error message.
        """
        try:
            # Terminate threads
            self._release_idle_loops_event.set()
            self._idling_event.set()
            self._readline_event.set()
            self._current_idle = None
            if self._readline_thread.is_alive():
                self._readline_thread.join(timeout=JOIN_TIMEOUT)
            if self._idling_thread.is_alive():
                self._idling_thread.join(timeout=JOIN_TIMEOUT)
        except Exception as e:
            print("Idle Manager could not terminated properly: ", e)

        return self._parse_command_result(
            super().logout(),
            success_message="Logout successful",
            failure_message="Could not logout from the target imap server",
        )

    @override
    @handle_idle
    def lsub(self, directory: str = '""', pattern: str = "*"):
        return super().lsub(directory, pattern)

    @override
    @handle_idle
    def myrights(self, mailbox: str):
        return super().myrights(mailbox)

    @override
    @handle_idle
    def namespace(self):
        return super().namespace()

    @override
    @handle_idle
    def noop(self):
        return super().noop()

    @override
    @handle_idle
    def partial(self, message_num: str, message_part: str, start: str, length: str):
        return super().partial(message_num, message_part, start, length)

    @override
    @handle_idle
    def proxyauth(self, user: str):
        return super().proxyauth(user)

    @override
    @handle_idle
    def rename(self, oldmailbox: str, newmailbox: str):
        return super().rename(oldmailbox, newmailbox)

    @override
    @handle_idle
    def search(self, charset: str | None, *criteria: str):
        return super().search(charset, *criteria)

    @override
    @handle_idle
    def select(self, folder: str | Folder, readonly: bool = False) -> IMAPCommandResult:
        """
        Overrides the `select` method to handle the `Folder` enum type.
        """
        folder = self.find_matching_folder(folder) or (
            self._encode_folder(folder) if isinstance(folder, str) else folder
        )  # type: ignore

        result = self._parse_command_result(
            super().select(folder, readonly),
            success_message=f"Successfully selected {folder}",
            failure_message=f"Error while selecting folder `{folder}`",
        )

        if not result[0]:
            raise IMAPManagerException(result[1])

        return result

    @override
    @handle_idle
    def setacl(self, mailbox: str, who: str, what: str):
        return super().setacl(mailbox, who, what)

    @override
    @handle_idle
    def setannotation(self, *args: str):
        return super().setannotation(*args)

    @override
    @handle_idle
    def setquota(self, root: str, limits: str):
        return super().setquota(root, limits)

    @override
    @handle_idle
    def sort(self, sort_criteria: str, charset: str, *search_criteria: str):
        return super().sort(sort_criteria, charset, *search_criteria)

    @override
    @handle_idle
    def starttls(self, ssl_context: SSLContext | None = None):
        return super().starttls(ssl_context)

    @override
    @handle_idle
    def status(self, mailbox: str, names: str):
        return super().status(mailbox, names)

    @override
    @handle_idle
    def store(self, message_set: str, command: str, flags: str):
        return super().store(message_set, command, flags)

    @override
    @handle_idle
    def subscribe(self, mailbox: str):
        return super().subscribe(mailbox)

    @override
    @handle_idle
    def thread(self, threading_algorithm: str, charset: str, *search_criteria: str):
        return super().thread(threading_algorithm, charset, *search_criteria)

    @override
    @handle_idle
    def uid(self, command: str, *args: str):
        return super().uid(command, *args)

    @override
    @handle_idle
    def unsubscribe(self, mailbox: str):
        return super().unsubscribe(mailbox)

    @override
    @handle_idle
    def unselect(self):
        return super().unselect()

    @override
    @handle_idle
    def xatom(self, name: str, *args: str):
        return super().xatom(name, *args)

    # IMAPManager commands

    def is_supported(self, keyword: str) -> bool:
        """
        Check if the given capability is supported for current
        host.

        Args:
            keyword (str): The capability keyword to check.

        Returns:
            bool: True if the capability is supported, False otherwise.

        Example:
            >>> client.is_supported("IDLE")
            True
            >>> client.is_supported("UTF8=ACCEPT")
            False
        """
        if self.capabilities:
            return keyword in self.capabilities
        status, data = self.capability()
        if not status or not data or not data[0]:
            raise Exception("Could not reach capability list.")
        return keyword in data[0].decode()

    def is_logged_out(self) -> bool:
        """Check if imap connection is terminated"""
        try:
            if self.is_idle() or self.is_idle_activation_countdown_continue():
                return False
            return super().noop()[0] != "OK"
        except Exception:
            return True

    def is_idle_supported(self) -> bool:
        """Check if idle is supported"""
        return self._is_idle_supported

    def is_idle_optimization_enabled(self) -> bool:
        """Check if idle optimization is enabled"""
        return self._idle_optimization

    def is_idle_activation_countdown_continue(self) -> bool:
        """Check if idle activation countdown is continue"""
        return (
            self.is_idle_optimization_enabled()
            and self._is_idle_activation_countdown_continue
        )

    def is_idle(self) -> bool:
        """Check if idle is active"""
        return self._current_idle is not None

    def idle(self) -> None:
        """
        Initiates the IMAP IDLE command to start monitoring changes
        in the INBOX(is going to select) on its own thread. If already
        in IDLE mode, does nothing.

        If idle_optimization is True, Before starting IDLE mode wait about
        IDLE_ACTIVATION_INTERVAL then start IDLE mode, but if `idle` method
        called while waiting, restart countdown and start waiting from the
        beginning, this technique prevents switching to IDLE mode too much
        in very short period.
        """
        if not self.is_idle_supported():
            raise Exception(f"IDLE is not supported on {self._host}")
        if self.is_idle():
            return
        if not self._idle_command_in_process_event.is_set():
            return

        if self._idle_optimization:
            # Stop current activation countdown
            self._idling_event.set()
            self._idle_activation_countdown = IDLE_ACTIVATION_INTERVAL
            self._is_idle_activation_countdown_continue = True
        else:
            self._is_idle_activation_countdown_continue = False
            # Check out select INBOX in optimized_idle_lifecycle
            # function for description of this selection.
            self.select(Folder.Inbox, readonly=True)

        self._readline_event.clear()
        if not self._readline_thread.is_alive():
            self._readline_thread.start()

        if not self._idle_optimization:
            self._current_idle = IMAPManager.IdleSession(
                tag=self._new_tag(), start_time=time.time()
            )
            self.send(b"%s IDLE\r\n" % self._current_idle.tag)
            print(
                f"'IDLE' command sent with tag: {self._current_idle.tag} at {datetime.now()}."
            )

            self._wait_for_response(IMAPManager.WaitResponse.IDLE)

        self._idling_event.clear()
        if not self._idling_thread.is_alive():
            self._idling_thread.start()

    def _start_reading_lines(self) -> None:
        """
        Continuously reads server responses and processes
        them.
        """
        if self._release_idle_loops_event.is_set():
            raise Exception(
                "Before starting `_start_reading_lines`, clear `_release_idle_loops_event`."
            )

        self.socket().settimeout(None)
        print("`_start_reading_lines` started on its own thread...")
        while not self._release_idle_loops_event.is_set():
            if not self._readline_event.is_set():
                try:
                    print(f"Waiting for new line since {datetime.now()}...")
                    response = self.readline()
                    if response:
                        print(f"New response received: {response} at {datetime.now()}.")
                        self._handle_response(response)
                except (TimeoutError, OSError):
                    print(f"Readline timed out at {datetime.now()}.")
                    pass
            self._release_idle_loops_event.wait(timeout=1)

    def _start_idle_lifecycle(self) -> None:
        """
        Continuously checks IDLE session duration and automatically
        refreshes the connection when IDLE_TIMEOUT is reached.
        """
        if self._release_idle_loops_event.is_set():
            raise Exception(
                "Before starting `_start_idle_lifecycle`, clear `_release_idle_loops_event`."
            )

        if not self._current_idle:
            raise Exception(
                "`_start_idle_lifecycle` cannot be started, if `_current_idle` is None."
            )

        print(f"'IDLE' lifecycle creating for {self._current_idle.tag} ...")
        while not self._release_idle_loops_event.is_set():
            if not self._idling_event.is_set() and self._current_idle is not None:
                print(f"IDLING for {self._current_idle.tag} at {datetime.now()}.")
                if time.time() - self._current_idle.start_time > IDLE_TIMEOUT:
                    print(
                        f"IDLING timeout reached for {self._current_idle.tag} at {datetime.now()}."
                    )
                    self.done()
                    self.idle()
            self._release_idle_loops_event.wait(timeout=1)

    def _start_optimized_idle_lifecycle(self) -> None:
        """
        Starts when the countdown is finished and
        automatically refreshes IDLE mode when
        IDLE_TIMEOUT is reached.
        """
        if self._release_idle_loops_event.is_set():
            raise Exception(
                "Before starting `_start_optimized_idle_lifecycle`, clear `_release_idle_loops_event`."
            )

        while not self._release_idle_loops_event.is_set():
            print(f"IDLE activation countdown started at {datetime.now()}...")
            while (
                self._idle_activation_countdown > 0
                and not self._release_idle_loops_event.is_set()
            ):
                # TODO: Send NOOP if needed
                if (
                    not self._idling_event.is_set()
                    and self._is_idle_activation_countdown_continue
                ):
                    self._idle_activation_countdown -= 1
                time.sleep(1)

            if self._release_idle_loops_event.is_set():
                self._is_idle_activation_countdown_continue = False
                print(
                    "Idle Manager terminated while waiting for countdown. Breaking lifecycle..."
                )
                break

            print(f"IDLE activation countdown finished at {datetime.now()}...")

            # Before starting idle mode, select inbox to receive exists
            # messages: https://datatracker.ietf.org/doc/html/rfc2177.html#autoid-3
            self.select(Folder.Inbox, readonly=True)
            idle_tag = self._new_tag()
            self.send(b"%s IDLE\r\n" % idle_tag)
            print(f"'IDLE' command sent with tag: {idle_tag} at {datetime.now()}.")
            self._idle_command_in_process_event.clear()

            self._wait_for_response(IMAPManager.WaitResponse.IDLE)
            if self._release_idle_loops_event.is_set():
                self._is_idle_activation_countdown_continue = False
                print("Idle Manager is desctructed while waiting for IDLE response.")
                break

            self._current_idle = IMAPManager.IdleSession(
                tag=idle_tag, start_time=time.time()
            )
            self._is_idle_activation_countdown_continue = False
            self._idle_command_in_process_event.set()

            print(
                f"Optimized 'IDLE' lifecycle creating for {self._current_idle.tag} ..."
            )
            while not self._release_idle_loops_event.is_set():
                if not self._idling_event.is_set() and self._current_idle is not None:
                    print(f"IDLING for {self._current_idle.tag} at {datetime.now()}.")
                    if time.time() - self._current_idle.start_time > IDLE_TIMEOUT:
                        print(
                            f"IDLING timeout reached for {self._current_idle.tag} at {datetime.now()}."
                        )
                        self.done()
                        self.idle()
                        break
                self._release_idle_loops_event.wait(timeout=1)

    def done(self) -> None:
        """Terminates the current IDLE session if active."""
        if not self._current_idle:
            self._is_idle_activation_countdown_continue = False
            return

        self._idling_event.set()
        self.send(b"DONE\r\n")
        print(f"DONE command sent for {self._current_idle.tag} at {datetime.now()}.")
        self._wait_for_response(IMAPManager.WaitResponse.DONE)

        self._readline_event.set()
        temp_tag = self._current_idle.tag
        self._current_idle = None
        self._is_idle_activation_countdown_continue = False
        self._release_readline_for_imap4(True)
        print(f"DONE for {temp_tag} handled. IDLE terminated.")

    def _release_readline_for_imap4(self, force: bool = True):
        """
        Sets the readline event in the idle manager, allowing methods like select, uid
        and list in the parent class (IMAP4_SSL) to retrieve messages instead of IMAPManager.

        Args:
            force (bool): If force is True then send NOOP even readline_event is already
            set.
        """
        if not self._readline_event.is_set():
            self._readline_event.set()
            # This will release self.readline in readline_thread
            super().send(b"%s NOOP\r\n" % self._new_tag())
        elif force:
            super().send(b"%s NOOP\r\n" % self._new_tag())

    def _resume_readline_for_imapmanager(self):
        """
        Clears the readline event in the idle manager, allowing IMAPManager to retrieve
        messages such as IDLE, RECENT and EXISTS instead of the parent class.
        """
        if self._readline_event.is_set():
            self._readline_event.clear()

    def _wait_for_response(self, wait_response: WaitResponse):
        """
        Waits for a specific response type from the IMAP server.

        Args:
            wait_response (IMAPManager.WaitResponse): Expected response type to wait for

        Times out after WAIT_RESPONSE_TIMEOUT seconds and resets wait state.
        """
        if not wait_response or wait_response not in IMAPManager.WAIT_RESPONSE_LIST:
            raise ValueError(
                f"`wait_response` must be one of the {IMAPManager.WAIT_RESPONSE_LIST}."
            )

        counter = 0
        while (
            self._wait_response != wait_response
            and not self._release_idle_loops_event.is_set()
        ):
            print(f"Waiting for {wait_response} response at {datetime.now()}...")
            if not self._readline_event.is_set():
                counter += 1
                if counter > WAIT_RESPONSE_TIMEOUT:
                    if self._current_idle:
                        print(
                            "Wait response timeout reached, current idle set to None."
                        )
                        self._current_idle = None
                    self._wait_response = None
                    raise TimeoutError(
                        f"IMAPManager.WaitResponse: {wait_response} did not received in time at {datetime.now()}."
                    )
            else:
                raise Exception("Readline is set while waiting for response.")
            self._release_idle_loops_event.wait(timeout=1)

    def _handle_response(self, response: bytes):
        """
        Determines the type of server response and delegates handling to the
        appropriate method. This method shouldn't be called directly, but rather
        through the `readline` method.

        Args:
            response (bytes): The raw server response to be processed.
        """
        if b"idling" in response:
            self._handle_idle_response()
        elif (
            b"OK" in response and self.is_idle() and self._current_idle.tag in response
        ):  # type: ignore
            self._handle_done_response()
        elif b"BYE" in response:
            self._handle_bye_response()
        elif b"EXISTS" in response and self._listen_new_messages:
            self._handle_exists_response(response)

    def _handle_idle_response(self):
        """
        Catches the server's response to the IDLE command.
        This method shouldn't be called directly, but rather
        through the `handle_response` method.
        """
        self._wait_response = IMAPManager.WaitResponse.IDLE

    def _handle_done_response(self):
        """
        Catches the server's response to the DONE command.
        This method shouldn't be called directly, but rather
        through the `handle_response` method.
        """
        self._wait_response = IMAPManager.WaitResponse.DONE

    def _handle_exists_response(self, response: bytes):
        """
        Catches the 'EXISTS' message of the server, which indicates the
        number of messages in the mailbox. It updates the expected response type,
        determines the new message count, and records the estimated arrival time
        for later processing. This method shouldn't be called directly, but rather
        through the `handle_response` method.

        Args:
            response (bytes): The server's EXISTS response data.
        """
        print(f"'EXISTS' message of server catched at {datetime.now()}.")
        self._wait_response = IMAPManager.WaitResponse.EXISTS
        size = MessageParser.get_exists_size(
            MessageParser.group_messages(response)[0]
        )
        if size > self._previous_mailbox_size:
            # Use of timedelta to account for potential server delays or discrepancies
            # in message arrival times.
            received_at = datetime.now() - timedelta(minutes=EMAIL_LOOKBACK_WINDOW)
            received_at = received_at.astimezone(ZoneInfo("UTC"))
            self._new_message_timestamps.append(received_at)

    def _handle_bye_response(self):
        """
        Handles the server's 'BYE' response, which indicates the server
        is closing the connection. Safely terminates the connection, stops
        threads, and raises an exception to signal the logout event. This
        method shouldn't be called directly, but rather through the
        `handle_response`method.
        """
        print(f"'BYE' message of server catched at {datetime.now()}.")
        self._wait_response = IMAPManager.WaitResponse.BYE

        if not self._idling_event.is_set():
            self.idling_event.set()
        if self._idling_thread.is_alive():
            self._idling_thread.join(timeout=JOIN_TIMEOUT)
        self._release_readline_for_imap4()

        raise IMAPManagerLoggedOutException(
            f"'BYE' response received from server at {datetime.now()}. IMAPManager connection closed safely."
        ) from None

    def _is_sequence_set_valid(self, sequence_set: str, uids: List[str]) -> bool:
        """
        Validates whether the given `sequence_set` correctly represents a subset of the provided `uids`.

        Args:
            sequence_set (str): A string representing a set of sequences as defined in RFC 9051.
            uids (list[int]): A sorted list of integer UIDs to validate against.

        Returns:
            bool: `True` if all UIDs derived from the `sequence_set` are present in the `uids` list.
            `False` otherwise.

        Example:
            >>> uids = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
            >>> _is_sequence_set_valid("1,3:6,9", uids)
            True
            >>> _is_sequence_set_valid("1:5,8:*", uids)
            True
            >>> _is_sequence_set_valid("1,3,20", uids)
            False

        References:
            https://datatracker.ietf.org/doc/html/rfc9051#name-formal-syntax (check sequence-set for more information.)
        """
        if not SEQUENCE_SET_PATTERN.match(sequence_set):
            return False

        max_uid = uids[-1]
        expanded = set()
        segments = sequence_set.split(",")

        for segment in segments:
            if ":" in segment:
                parts = segment.split(":")
                if parts[0] == "*":
                    start = int(max_uid)
                else:
                    start = int(parts[0])

                if parts[-1] == "*":
                    end = int(max_uid)
                else:
                    end = int(parts[-1])

                expanded.update(list(range(start, end + 1)), [max(start, end)])
            else:
                if segment == "*":
                    expanded.add(max_uid)
                else:
                    expanded.add(segment)

        for sequence_set_uid in map(str, expanded):
            if sequence_set_uid not in uids:
                return False

        return True

    @handle_idle
    def find_matching_folder(
        self, requested_folder: str | Folder, encoded: bool = True
    ) -> bytes | None:
        """
        Retrieve the IMAP folder name matching a specific byte string.

        This method is useful for handling cases where a client's folder names
        are localized in a different language.

        Args:
            requested_folder (str | Folder): The IMAP folder name (e.g., 'Inbox' or 'Trash').

        Returns:
            bytes | None: The folder name in bytes if a match is found; otherwise, None.

        Example:
            >>> find_matching_folder(Folder.Inbox)
            b'INBOX'
            >>> find_matching_folder(Folder.Flagged, encoded=True)
            b'"[Gmail]/Y\xc4\xb1ld\xc4\xb1zl\xc4\xb1"'
            >>> find_matching_folder(Folder.Flagged, encoded=False)
            b'"[Gmail]/Yıldızlı"' # Flagged in Turkish
        """
        if requested_folder.lower() not in FOLDER_LIST:
            return None

        status, folders_as_bytes = self.list()
        if status == "OK" and folders_as_bytes and isinstance(folders_as_bytes, list):
            for folder_as_bytes in folders_as_bytes:
                if (
                    requested_folder.upper()
                    in self._decode_folder(folder_as_bytes).upper()
                ):
                    if encoded:
                        return self._encode_folder(
                            self._extract_folder_name(folder_as_bytes)
                        )
                    else:
                        return self._extract_folder_name(folder_as_bytes)
        return None

    def _encode_folder(self, folder: str) -> bytes:
        """Encode a folder name into a byte string suitable for IMAP operations."""
        try:
            return ('"' + folder + '"').encode("utf-8")
        except Exception as e:
            raise IMAPManagerException(
                f"Error while encoding folder name: {str(e)}"
            ) from None

    def _decode_folder(self, folder: bytes) -> str:
        """Decode a folder name from a byte string returned by an IMAP server."""
        try:
            return folder.decode("utf-8")
        except Exception as e:
            raise IMAPManagerException(
                f"Error while decoding folder name `{str(folder)}`: `{str(e)}`."
            ) from None

    def _check_folder_names(self, *folders: str, raise_error: bool = True) -> bool:
        """
        Check if a folder name(s) is valid.

        Args:
            folders (str): Folder names
            raise_error (bool, optional): If True, raise an error if the folder name is invalid.
                                          Default is True

        Returns:
            bool: True if folder name is valid, False otherwise

        Example:
            >>> self._check_folder_names("INBOX")
            True
            >>> self._check_folder_names("INBOX", "Trash")
            True
            >>> self._check_folder_names("")
            raises ValueError
            >>> self._check_folder_names("INBOX", raise_error=False)
            False

        Raises:
            ValueError: If the folder name is invalid and raise_error is True
        """
        for folder_name in folders:
            if not folder_name:
                continue

            folder_name_length = len(folder_name)
            if (
                folder_name is None
                or folder_name == ""
                or folder_name_length > MAX_FOLDER_NAME_LENGTH
                or folder_name_length < 1
            ):
                if raise_error:
                    raise ValueError(f"Invalid folder name: `{folder_name}`")
                return False

        return True

    def _extract_folder_name(self, folder: str | bytes, /, tagged: bool = False) -> str:
        """
        Extract a folder name from a byte string returned by an IMAP server.

        Args:
            folder (str | bytes): The byte or string containing the folder name.
            tagged (boolean): Tag folders with their original name. Inbox will
            also be tagged either has a special tag or not.

        Returns:
            str: The decoded and cleaned folder name.

        Example:
            >>> _extract_folder_name(b'(\\HasNoChildren) "/" "INBOX"')
            'INBOX'
            >>> _extract_folder_name(b'(\\Junk \\HasNoChildren) "|" "[Gmail]/Spam"', tagged=False)
            'Spam'
            >>> _extract_folder_name(b'(\\Junk \\HasNoChildren) "|" "[Gmail]/Spam"', tagged=True)
            '[Folder.Junk]:Spam'
            >>> _extract_folder_name(b'(\\HasNoChildren) "|" "MyCustomFolder"')
            'MyCustomFolder'

        References:
            https://datatracker.ietf.org/doc/html/rfc9051#name-list-response
        """
        try:
            if isinstance(folder, bytes):
                folder = self._decode_folder(folder)

            folder_parts = folder.split(f' "{self._hierarchy_delimiter}" ', 1)
            folder_name = folder_parts[-1].replace('"', "")
            folder_tag = folder_parts[0] if len(folder_parts) > 1 else None

            if tagged and folder_tag:
                folder_tag = folder_tag.lower()

                # Add folder tag to beginning of the folder name like if
                # folder includes any. For example if folder is something like
                # this: "(\HasNoChildren \Trash) | Trash Bin" convert it to
                # "Trash:Trash Bin". This is important to ensure that the client
                # can recognize the folder in a way that is not affected by any
                # language or different spelling.
                for standard_folder in FOLDER_LIST:
                    standard_folder = standard_folder.lower()
                    if (
                        standard_folder in folder_tag
                        or standard_folder == folder_name.lower()
                    ):
                        folder_name = f"{standard_folder.capitalize()}:{folder_name}"

            return folder_name
        except Exception as e:
            raise IMAPManagerException(
                f"Error while decoding folder name `{str(folder)}`: `{str(e)}`."
            ) from None

    @handle_idle
    def get_folders(
        self, folder_name: str | None = None, /, tagged: bool = False
    ) -> List[str]:
        """
        Retrieve a list of all email folders.

        Args:
            folder_name (str, optional): Subfolders of the specified folder.
            Defaults to None. If None, returns all folders.
            tagged (boolean): Tag folders with their original name. Inbox will
            also be tagged either has a special tag or not.

        Returns:
            list[str]: List of folder names in the email account

        Example:
            >>> get_folders(tagged=False)
            ['Inbox', '[Gmail]/Spam', '[Gmail]/Trash Bin', 'My Custom Folder']
            >>> get_folders(tagged=True)
            ['[Folder.Inbox]:Inbox', '[Folder.Junk]:[Gmail]/Spam', '[Folder.Trash]:[Gmail]/Trash Bin', 'My Custom Folder']

        References:
            https://datatracker.ietf.org/doc/html/rfc9051#name-list-response
        """
        status, folders = self.list()
        if not status == "OK":
            raise IMAPManagerException(f"Failed to list folders with status: {status}.")

        folder_list = []
        disallowed_keywords = [b"\\Noselect"]
        disallowed_keywords = [keyword.lower() for keyword in disallowed_keywords]
        for folder in folders:
            if not any(keyword in folder.lower() for keyword in disallowed_keywords):
                decoded_folder = self._extract_folder_name(folder, tagged=tagged)
                if not folder_name or (
                    folder_name in decoded_folder
                    and not decoded_folder.endswith(folder_name)
                ):
                    folder_list.append(decoded_folder)

        # Sort folders
        # Standard folders comes first for example:
        # ['[Folder.Junk]:Spam', '[Folder.Trash]:[Gmail]/Trash Bin', 'customA', 'customA/customAB', ...]
        # Custom folders will be sorted hierarchically for example:
        # [..., 'customA', 'customA/customAB', 'customA/customAB/customABC', 'customB/customBA']
        folder_list.sort(
            key=lambda path: (
                not any(
                    path.startswith(f"{folder.capitalize()}:") for folder in FOLDER_LIST
                ),
                path.split(f"{self._hierarchy_delimiter}"),
                len(path.split(f"{self._hierarchy_delimiter}")),
            )
        )
        return folder_list

    def build_search_criteria_query(self, search_criteria: SearchCriteria | str) -> str:
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
            ...                                  body="world",
            ...                                  included_flags=[Mark.Flagged, Mark.Seen, "customflag"])
            >>> build_search_criteria_query(search_criteria)
            '(FROM "a@mail.com") (OR (TO "b@mail.com") (TO "c@mail.com")) (SUBJECT "Hello") (SINCE
            ... "2023-01-01") (BEFORE "2023-12-31") (BODY "world") FLAGGED SEEN KEYWORD "customflag"'

            >>> build_search_criteria_query("sender@mail.com")
            'TEXT "sender@mail.com"'

            >>> build_search_criteria_query("Some paragraph")
            'TEXT "Some paragraph"'

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
            query = ""
            len_search_keys = len(search_keys)
            if len_search_keys == 1:
                return f'{criteria} "{search_keys[0]}"'

            mid = len_search_keys // 2
            left_part = recursive_or_query(criteria, search_keys[:mid])
            right_part = recursive_or_query(criteria, search_keys[mid:])

            return query + f"OR ({left_part}) ({right_part})"

        def add_criterion(
            criteria: str,
            value: str | int | List | None,
            seperate_with_or: bool = False,
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
                return ""

            if isinstance(value, int):
                value = str(value)
            elif isinstance(value, List):
                if criteria == "":
                    # value=["Flagged", "Seen", "Answered"]
                    return f" {' '.join([i.strip().upper() for i in value])}"

                if len(value) <= 1:
                    return f' ({criteria.strip()} "{value[0].strip()}")'

            if seperate_with_or and len(value) > 1:
                value = recursive_or_query(criteria, value)
                criteria = ""

            if criteria:
                return f" ({criteria.strip()} {add_quotes_if_str(value)})"
            else:
                return f" ({value.strip()})"

        try:
            if isinstance(search_criteria, str):
                return add_criterion("TEXT", search_criteria).strip()

            flag_list = []
            if search_criteria.included_flags:
                for flag in search_criteria.included_flags:
                    if flag.lower() not in MARK_LIST:
                        flag_list.append(f"KEYWORD {flag}")
                    else:
                        flag_list.append(flag.replace("\\", ""))

            if search_criteria.excluded_flags:
                for flag in search_criteria.excluded_flags:
                    if flag.lower() not in MARK_LIST:
                        flag_list.append(f"UNKEYWORD {flag}")
                    else:
                        flag_list.append(
                            flag.replace(
                                "\\",
                                "UN" if not flag.lower().startswith("\\un") else "",
                            )
                        )

            search_criteria_query = ""
            search_criteria_query += add_criterion(
                "FROM",
                extract_email_addresses(search_criteria.senders or []),
                len(search_criteria.senders or []) > 1,
            )
            search_criteria_query += add_criterion(
                "TO",
                extract_email_addresses(search_criteria.receivers or []),
                len(search_criteria.receivers or []) > 1,
            )
            search_criteria_query += add_criterion(
                "CC",
                extract_email_addresses(search_criteria.cc or []),
                len(search_criteria.cc or []) > 1,
            )
            search_criteria_query += add_criterion(
                "HEADER MESSAGE-ID",
                search_criteria.message_id,
                len(search_criteria.message_id or []) > 1,
            )
            search_criteria_query += add_criterion("SUBJECT", search_criteria.subject)
            search_criteria_query += add_criterion("SINCE", search_criteria.since)
            search_criteria_query += add_criterion("BEFORE", search_criteria.before)
            search_criteria_query += add_criterion("BODY", search_criteria.include)
            search_criteria_query += add_criterion("NOT BODY", search_criteria.exclude)
            search_criteria_query += add_criterion("", flag_list)
            search_criteria_query += add_criterion(
                "TEXT", search_criteria.has_attachments and "ATTACHMENT" or ""
            )
            search_criteria_query += add_criterion(
                "LARGER", search_criteria.larger_than
            )
            search_criteria_query += add_criterion(
                "SMALLER", search_criteria.smaller_than
            )
        except Exception as e:
            raise IMAPManagerException(
                f"Error while building search query from `{str(search_criteria)}`"
            ) from e

        return search_criteria_query.strip()

    @handle_idle
    def search_emails(
        self, folder: str | None = None, search: str | SearchCriteria = ""
    ) -> List[str]:
        """
        Get email uids from a specified folder based on search criteria. Also saves
        the result to use them with `get_emails()`.

        Args:
            folder (str, optional): Folder to search in. If folder not provided but
            search is, then Folder will be Folder.All, but neither folder and search
            are provided then folder will be Folder.Inbox
            search (str | SearchCriteria, optional): Search criteria. Defaults to "ALL".

        Example:
            >>> search_emails("INBOX") # Search all emails in INBOX.
            ["1", "2", "3", "4", "5", "6"]
            >>> search_emails("Archived", "FROM 'a@mail.com'") # Search emails from 'a@mail.com'.
            ["1", "2", "5", "6"]
            >>> search_emails("MyCustomFolder", SearchCriteria(senders=['a@mail.com'])) # Search emails from 'a@mail.com'.
            ["1", "2", "3", "4"]
        """

        def save_search_result(
            uids: List[str], folder: str | Folder, search_query: str
        ):
            """
            Save emails to a specified folder for later use.

            Args:
                uids (list[str]): A list of email uids to save.
                folder (str): The folder to save the emails to.
                search_query (str): The search query used to fetch the emails.
            """
            self._searched_emails = IMAPManager.SearchedEmails(
                folder=self._extract_folder_name(
                    self.find_matching_folder(str(folder), encoded=False) or folder
                ),
                search_query=search_query,
                uids=uids,
                count=len(uids)
            )

        if not folder:
            folder = Folder.All if search else Folder.Inbox

        self.select(folder, readonly=True)

        if search:
            search_criteria_query = self.build_search_criteria_query(search).encode(
                "utf-8"
            )
        else:
            search_criteria_query = "ALL"

        # Searching emails
        try:
            search_status, uids = self.uid("search", None, search_criteria_query)

            if search_status != "OK":
                raise IMAPManagerException(
                    f"Error while getting email uids, search query was `{search_criteria_query}` and error is `{search_status}.`"
                )

            if not uids or not uids[0]:
                return uids

            uids = uids[0].decode().split()[::-1]
            save_search_result(uids, folder, search_criteria_query)
            return uids
        except Exception as e:
            raise IMAPManagerException(
                f"Error while getting email uids, search query was `{search_criteria_query}` and error is `{str(e)}.`"
            )

    @handle_idle
    def is_email_exists(self, folder: str, sequence_set: str) -> bool:
        """
        Check is given uid exists in given folder.

        Args:
            folder (str): Folder to search in.
            sequence_set (str): Sequence set of uids to check.

        Returns:
            bool: True if email exists, False otherwise.

        Example:
            >>> is_email_exists("1") # Returns True if the email with UID 1 is found.
            >>> is_email_exists("1,2,3") # Return True if all of the emails with with UID 1,2,3 are found.
            >>> is_email_exists("1:3") # Return True if all of the emails with with UID 1,2,3 are found.
            >>> is_email_exists("1,3:5") # Return True if all of the emails with with UID 1 and 3,4,5 are found.

        Raises:
            ValueError: If the `sequence_set` contains "*".

        References:
            https://datatracker.ietf.org/doc/html/rfc9051#name-formal-syntax (check sequence-set for more information.)
        """
        if "*" in sequence_set:
            raise ValueError(
                f"Error sequence_set can not contain `*` while checking emails `{sequence_set}`"
            )

        self.select(folder, readonly=True)

        status, data = self.uid("search", f"UID {sequence_set}")
        if not status:
            raise IMAPManagerException(
                f"Error while checking emails `{sequence_set}`: `{status}`"
            )

        return self._is_sequence_set_valid(sequence_set, data[0].decode().split(" "))

    def _resolve_offsets(self,
        offset_start: int | None = None,
        offset_end: int | None = None
    ):
        """
        Validate search results and prepare offset parameters for email pagination.

        Args:
           offset_start (int, optional): Starting position for email range (1-based). Defaults to configured value.
           offset_end (int, optional): Ending position for email range (1-based). Defaults to configured value.

        Returns:
           tuple[int, int]: Validated and normalized offset values (0-based start index, 1-based end index).

        Raises:
           IMAPManagerException: If no emails have been searched yet.
           SearchedEmailsEmptyException: If search returned no results.
           ValueError: If offset parameters are invalid.

        Example:
           >>> validate_and_prepare_offsets(1, 5)
           (0, 5)
           >>> validate_and_prepare_offsets(100, 110)  # If only 50 emails found
           (49, 50)
        """
        if not self._searched_emails:
            raise IMAPManagerException(
                "No emails have been searched yet. Call `search_emails` first."
            )

        if offset_start and offset_end and offset_start > offset_end:
            raise ValueError(
                "Invalid `offset_start`: `offset_start` must be less then `offset_end`."
            )

        if not offset_start:
            offset_start = GET_EMAILS_OFFSET_START
        elif offset_start < 1:
            raise ValueError(
                f"Invalid `offset_start`: {offset_start}. `offset_start` must be greater than or equal to 1."
            )

        if not offset_end:
            offset_end = GET_EMAILS_OFFSET_END
        elif offset_end < 1:
            raise ValueError(
                f"Invalid `offset_end`: {offset_end}. `offset_end` must be greater than or equal to 1."
            )

        uids_len = self._searched_emails.count
        offset_start = (
            uids_len - 1 if offset_start >= uids_len else offset_start
        ) - 1
        offset_end = uids_len if offset_end >= uids_len else offset_end
        return offset_start, offset_end

    @handle_idle
    def get_emails(self,
        offset_start: int | None = None,
        offset_end: int | None = None
    ) -> Mailbox:
        """
        Fetch emails from a list of uids.

        Args:
            offset_start (int, optional): Starting index of the emails to fetch. Defaults to 1.
            offset_end (int, optional): Ending index of the emails to fetch. Defaults to 10.

        Returns:
            Mailbox: Dataclass containing the fetched emails, folder, and total number of emails.

        Example:
            >>> get_emails(1, 2)
            Mailbox(folder='INBOX', emails=[Email(uid="1", sender="a@gmail.com", ...),
            Email(uid="2", sender="b@gmail.com", ...)], total=2)
        """
        if not self._searched_emails:
            raise IMAPManagerException(
                "No emails have been searched yet. Call `search_emails` first."
            )

        if self._searched_emails.count == 0:
            return Mailbox(folder=self._searched_emails.folder, emails=[], total=0)

        offset_start, offset_end = self._resolve_offsets(offset_start, offset_end)

        # Fetching emails
        sequence_set = ""
        messages = []
        emails = []
        try:
            sequence_set = ",".join(
                map(str, self._searched_emails.uids[offset_start:offset_end][::-1])
            )
            status, messages = self.uid(
                "FETCH",
                sequence_set,
                "(BODY.PEEK[HEADER.FIELDS (FROM TO SUBJECT DATE CC BCC MESSAGE-ID "
                "IN-REPLY-TO REFERENCES LIST-UNSUBSCRIBE LIST-UNSUBSCRIBE-POST)] "
                "FLAGS BODYSTRUCTURE)",
            )

            if status != "OK":
                raise IMAPManagerException(
                    f"`{sequence_set}` in folder `{self._searched_emails.folder}` could not fetched `{len(emails)}`: `{status}`"
                )

            if not messages or not messages[0]:
                return Mailbox(folder=self._searched_emails.folder, emails=[], total=0)

            grouped_messages = MessageParser.group_messages(messages)[::-1]
            fetchs = {}
            """
            `fetchs` will be something like this:
            {"1.1": ["1234", "1235", "1236"], "1.1.1": ["1250", "1251"], "2": ["1300"]}
            which can be use to create fetch requests like this instead of one by one:
            C: "A101 FETCH 1234, 1235, 1236 (BODY.PEEK[1.1] BODY.PEEK[1.1.MIME])"
            S: ...
            C: "A102 FETCH 1250, 1251 (BODY.PEEK[1.1.1] BODY.PEEK[1.1.1.MIME])"
            S: ...
            C: "A103 FETCH 1300 (BODY.PEEK[2] BODY.PEEK[2.MIME])
            S: ...
            """
            email_uid_map = {}
            for index, grouped_message in enumerate(grouped_messages):
                uid = MessageParser.get_uid(grouped_message)
                email_uid_map[uid] = index
                headers = MessageParser.get_headers(grouped_message)
                emails.append(
                    Email(
                        **headers,
                        uid=uid,
                        body="",  # Temporary until body is fetched.
                        flags=MessageParser.get_flags(grouped_message),
                        attachments=[
                            Attachment(
                                name=attachment[0],
                                size=attachment[1],
                                cid=attachment[2],
                                type=attachment[3],
                            )
                            for attachment in MessageParser.get_attachment_list(grouped_message)
                        ],
                    )
                )

                body_part = (
                    MessageParser.get_part(grouped_message, ["TEXT", "PLAIN"]) or
                    MessageParser.get_part(grouped_message, ["TEXT", "HTML"]) or
                    "1"
                )

                if body_part in fetchs:
                    fetchs[body_part].append(uid)
                else:
                    fetchs[body_part] = [uid]

            messages.clear()
            for body_part, uids in fetchs.items():
                uids = sorted(uids, key=int)
                status, bodies = self.uid(
                    "FETCH",
                    ",".join(uids),
                    f"(BODY.PEEK[{body_part}] BODY.PEEK[{body_part}.MIME])",
                )
                if status != "OK":
                    print(f"Could not found bodies in emails {uids}")
                    continue

                body_group_messages = MessageParser.group_messages(bodies)
                for index, body_grouped_message in enumerate(body_group_messages):
                    content_type, encoding = MessageParser.get_content_type_and_encoding(body_grouped_message)
                    emails[email_uid_map[uids[index]]].body = MessageDecoder.body(
                        MessageParser.get_body(body_grouped_message),
                        encoding=encoding,
                        sanitize="html" not in content_type,
                        parse="html" in content_type
                    )
        except Exception as e:
            fetched_email_count = len(emails)
            raise IMAPManagerException(
                f"Error while fetching emails `{sequence_set}` in folder `{self._searched_emails.folder}`, fetched email length was `{fetched_email_count}`"
            ) from e
        finally:
            del messages

        return Mailbox(
            folder=self._searched_emails.folder, emails=emails, total=self._searched_emails.count
        )

    def any_new_email(self) -> bool:
        """
        Checks if there are any new emails by verifying if new message timestamps
        have been recorded.

        Returns:
            bool: True if new messages exist, False otherwise.
        """
        return bool(self._new_message_timestamps)

    @handle_idle
    def get_recent_emails(self) -> List[Email]:
        """
        Retrieves recent emails from the inbox based on the timestamps of newly detected messages.

        Returns:
            Mailbox: A mailbox object containing the filtered list of recent emails.

        Example:
            >>> get_recent_emails()
            [Email(uid="2", sender="b@gmail.com", ...), Email(uid="3", sender="c@gmail.com", ...)]
        """
        search_start_time = min(self._new_message_timestamps)
        self.search_emails(
            Folder.Inbox,
            SearchCriteria(
                # search_start_time must be converted to an IMAP-compatible date format
                # as defined in RFC 9051, Section 6.4.4
                # https://datatracker.ietf.org/doc/html/rfc9051#name-formal-syntax (check out date-text)
                since=convert_to_imap_date(search_start_time),
                included_flags=[Mark.Unseen],
            ),
        )
        mailbox = self.get_emails()
        if mailbox.total > 0:
            try:
                # email.date must conform to the syntax defined in RFC 5322, Section 3.3
                # https://datatracker.ietf.org/doc/html/rfc5322#autoid-23
                mailbox.emails = [
                    email
                    for email in mailbox.emails
                    if parsedate_to_datetime(email.date).astimezone(ZoneInfo("UTC"))
                    >= search_start_time
                ]
            except Exception as e:
                del mailbox
                raise IMAPManagerException(
                    "Error, recent emails fetched but dates could not parsed!"
                ) from e

        self._new_message_timestamps = []
        return mailbox.emails

    @handle_idle
    def get_email_content(self, folder: str, uid: str) -> Email:
        """
        Retrieve full content of a specific email.

        Args:
            folder (str): Folder containing the email.
            uid (str): Unique identifier of the email.

        Returns:
            Email: Dataclass containing the email content.

        Example:
            >>> get_email_content("1", Folder.Inbox)
            Email(uid="1", sender="a@gmail.com", ...)

        Notes:
            - Replaces inline attachments with data URLs to display them inline
            and if an error occurs while replacing the inline attachments, the
            replacement operation will be skipped without raising an error but
            it will be logged as a warning.
            - Marks the email as "Seen" if it is not already and if an error
            occurs while marking the email, the mark operation will be skipped
            without raising an error but it will be logged as a warning.
        """
        self.select(folder, readonly=True)

        # Get body and attachments
        body = ""
        inline_attachments = []
        try:
            status, message = self.uid(
                "fetch",
                uid,
                "(BODY.PEEK[HEADER.FIELDS (FROM TO SUBJECT DATE CC BCC "
                "MESSAGE-ID IN-REPLY-TO REFERENCES LIST-UNSUBSCRIBE CONTENT-"
                "TRANSFER-ENCODING)] FLAGS BODYSTRUCTURE)",
            )
            if status != "OK":
                raise IMAPManagerException(
                    f"Error while getting email `{uid}`'s content in folder `{folder}`: `{status}`"
                )

            if not message or not message[0]:
                raise ValueError(f"No email found with given {uid} uid.")

            grouped_message = MessageParser.group_messages(message)[0]
            headers = MessageParser.get_headers(grouped_message)
            flags = MessageParser.get_flags(grouped_message)
            for attachment in MessageParser.get_inline_attachment_list(grouped_message):
                inline_attachments.append(
                    Attachment(
                        name=attachment[0],
                        size=attachment[1],
                        cid=attachment[2],
                        type=attachment[3],
                    )
                )

            body_part = (
                MessageParser.get_part(grouped_message, ["TEXT", "HTML"]) or
                "1"
            )

            body = ""
            status, body_raw = self.uid(
                "FETCH",
                uid,
                f"(BODY.PEEK[{body_part}] BODY.PEEK[{body_part}.MIME])",
            )
            if status != "OK":
                print(f"There is no body in email {uid}")
            else:
                body_grouped_message = MessageParser.group_messages(body_raw)[0]
                _, encoding = MessageParser.get_content_type_and_encoding(body_grouped_message)
                body = MessageDecoder.body(
                    MessageParser.get_body(body_grouped_message),
                    encoding=encoding
                )
                try:
                    for cid, data in MessageParser.get_cid_and_data_of_inline_attachments(body_grouped_message):
                        i = 0
                        while i < len(inline_attachments):
                            if inline_attachments[i].cid == cid:
                                body = body.replace(
                                    f"cid:{inline_attachments[i].cid}",
                                    f"data:{inline_attachments[i].type};base64,{data}",
                                )
                                del inline_attachments[i]
                            else:
                                i += 1
                except Exception as e:
                    # If there is a problem with inline attachments
                    # just ignore them.
                    print(
                        f"An error occurred while replacing inline attachments: `{str(e)}` of email `{uid}`'s content in folder `{folder}`."
                    )
                    pass
        except Exception as e:
            raise IMAPManagerException(
                f"There was a problem with getting email `{uid}`'s content in folder `{folder}`: `{str(e)}`"
            ) from e

        return Email(
            **headers,
            uid=uid,
            body=body,
            flags=flags,
            attachments=[
                Attachment(
                    name=attachment[0],
                    size=attachment[1],
                    cid=attachment[2],
                    type=attachment[3],
                )
                for attachment in MessageParser.get_attachment_list(grouped_message)
            ],
        )

    @handle_idle
    def get_email_flags(self, sequence_set: str) -> List[Flags]:
        """
        Retrieve flags associated with a specific email.

        Args:
            sequence_set (str): The sequence set of the email to fetch flags for.

        Returns:
            list[Flags]: A list of Flags objects representing the flags associated with the email.

        Example:
            >>> get_email_flags("1")
            [Flags(uid="1", flags=["\\Seen", "\\Answered"])]
            >>> get_email_flags("1,2,3")
            [Flags(uid="1", flags=["\\Seen", "\\Answered"]), Flags(uid="2", flags=["\\Answered"]), Flags(uid="3", flags=["\\Flagged"])]
            >>> get_email_flags("1:3")
            [Flags(uid="1", flags=["\\Seen", "\\Answered"]), Flags(uid="2", flags=["\\Answered"]), Flags(uid="3", flags=["\\Flagged"])]
            >>> get_email_flags("1,3:4")
            [Flags(uid="1", flags=["\\Seen", "\\Answered"]), Flags(uid="3", flags=["\\Flagged"]), Flags(uid="4", flags=["\\Flagged"])]
            >>> get_email_flags("1:*") # In this case, mailbox has 3 emails
            [Flags(uid="1", flags=["\\Seen", "\\Answered"]), Flags(uid="2", flags=["\\Answered"]), Flags(uid="3", flags=["\\Flagged"])]
            >>> get_email_flags("1,3:*") # In this case, mailbox has 4 emails
            [Flags(uid="1", flags=["\\Seen", "\\Answered"]), Flags(uid="3", flags=["\\Flagged"]), Flags(uid="4", flags=["\\Flagged"])]

        References:
            https://datatracker.ietf.org/doc/html/rfc9051#name-formal-syntax (check sequence-set for more information.)
        """
        if self.state != "SELECTED":
            # Since uid's are unique within each mailbox, we can't just select INBOX
            # or something like that if there is no mailbox selected.
            raise IMAPManagerException(
                "Folder should be selected before fetching flags."
            )

        status, message = self.uid("FETCH", sequence_set, "(FLAGS)")

        try:
            flags_list = []
            if status != "OK":
                raise IMAPManagerException(
                    f"Error while fetching flags of email `{sequence_set}`: `{status}`"
                )

            grouped_messages = MessageParser.group_messages(message)
            for grouped_message in grouped_messages:
                flags_list.append(
                    Flags(
                        uid=MessageParser.get_uid(grouped_message),
                        flags=MessageParser.get_flags(grouped_message),
                    )
                )
        except Exception as e:
            raise IMAPManagerException(
                f"Error while fetching flags of email `{sequence_set}`: `{e}`"
            ) from e

        return flags_list or []

    @handle_idle
    def get_email_size(self, folder: str, uid: str) -> int | None:
        """
        Get email size of the given `uid`.

        Args:
            folder (str): Folder containing the email.
            uid (str): Unique identifier of the email.

        Returns:
            int: Size of the email as bytes.

        Example:
            >>> get_email_size("1", "INBOX")
            24300
        """
        status, messages = self.uid("FETCH", uid, "(RFC822.SIZE)")
        if status != "OK":
            raise IMAPManagerException(
                f"Error while getting size of the `{uid}` email in folder `{folder}`: `{status}`"
            )

        return MessageParser.get_size(
            MessageParser.group_messages(messages)[0]
        )

    @handle_idle
    def download_attachment(
        self, folder: str, uid: str, name: str, cid: str = ""
    ) -> Attachment:
        """
        Download an attachment from an email.

        Args:
            folder (str): Folder containing the email.
            uid (str): Unique identifier of the email.
            name (str): Name of the attachment file to download.
            cid (str, optional): Content ID of the attachment (default is an empty string).

        Returns:
            Attachment: An object containing metadata (name, size, CID, type) and data of the attachment.

        Raises:
            IMAPManagerException: If the body structure of the email cannot be fetched,
                                  the attachment is not found, or there is an error during the fetching process.

        Example:
            >>> attachment = download_attachment("1", "INBOX", "example.pdf")
            >>> print(attachment.name)
            'example.pdf'
        """
        self.select(folder, readonly=True)

        status, message = self.uid("FETCH", uid, "(BODYSTRUCTURE)")
        if status != "OK":
            raise IMAPManagerException(
                f"Error while fetching body structure of the `{uid}` email in folder `{folder}`: `{status}`"
            )

        if not message or not message[0]:
            raise ValueError(
                f"No attachment found in `{uid}` uid in `{folder}` folder with given `{name}` and `{cid}` cid."
            )

        grouped_message = MessageParser.group_messages(message)[0]
        attachment_list = MessageParser.get_attachment_list(grouped_message)
        target_attachment = [
            attachment for attachment in attachment_list if attachment[0] == name
        ][0]
        target_attachment = Attachment(
            name=target_attachment[0],
            size=target_attachment[1],
            cid=target_attachment[2],
            type=target_attachment[3],
        )

        try:
            target_part = MessageParser.get_part(
                grouped_message, ["FILENAME", '"' + name + '"', cid]
            )
            if not target_part:
                raise IMAPManagerException(
                    "Error, target attachment could not found in the email body."
                )

            status, message = self.uid("FETCH", uid, f"(BODY[{target_part}])")
            if status != "OK":
                raise IMAPManagerException(
                    f"Error while fetching attachment part of the `{uid}` email in folder `{folder}`: `{status}`"
                )

            body_grouped_message = MessageParser.group_messages(message)[0]
            content_type, encoding = MessageParser.get_content_type_and_encoding(body_grouped_message)
            target_attachment.data = MessageDecoder.body(
                MessageParser.get_body(body_grouped_message),
                encoding=encoding,
            )
        except:
            raise IMAPManagerException(
                f"Error while fetching attachment part of the `{uid}` email in folder `{folder}`: `{status}`"
            )

        return target_attachment

    @handle_idle
    def save_email_as_draft(
        self, email: EmailMessage, appenduid: str | None = None
    ) -> str:
        """
        Save an email as draft.

        Args:
            email (EmailMessage): The email as EmailMessage object to be saved as a draft.
            appenduid (str | None): The unique identifier (UID) of a previously saved draft.
                    If provided, the existing draft with this UID will be deleted before saving the new one.

        Returns:
            int: APPENDUID of saved draft.
        """
        if appenduid:
            self.delete_email(Folder.Drafts, appenduid)

        draft_mailbox_name = self.find_matching_folder(Folder.Drafts)
        self.select(draft_mailbox_name)

        status, data = self.append(
            draft_mailbox_name,
            "",
            imaplib.Time2Internaldate(time.time()),
            email.as_string().encode("utf-8"),
        )  # type: ignore
        if not status:
            raise IMAPManagerException(f"Error while saving email as draft: `{status}`")

        return MessageParser.get_uid(
            MessageParser.group_messages(data)[0]
        )

    @handle_idle
    def _mark_email(
        self,
        folder: str,
        sequence_set: str,
        command: str,
        mark: str | Mark,
        success_msg: str,
        err_msg: str,
    ) -> IMAPCommandResult:
        """
        Mark an email with a specific flag with given `command`.

        Args:
            folder (str): Folder containing the email.
            sequence_set (str): Sequence set of emails to mark.
            command (str): IMAP command to apply the flag like `+FLAGS` or `-FLAGS`.
            mark (str): Flag to apply to the email.
            success_msg (str): Success message to display.
            err_msg (str): Error message to display.

        Returns:
            IMAPCommandResult: A tuple containing:
                - A bool indicating whether the email was marked successfully.
                - A string containing a success message or an error message.
        """
        self.select(folder)

        if not mark:
            raise IMAPManagerException("`mark` cannot be empty.")

        mark_result = self._parse_command_result(
            self.uid("STORE", sequence_set, command, mark), success_msg, err_msg
        )

        if mark_result[0]:
            return self._parse_command_result(self.expunge(), success_msg, err_msg)

        return mark_result

    def mark_email(
        self, sequence_set: str, mark: str | Mark, folder: str = Folder.Inbox
    ) -> IMAPCommandResult:
        """
        Mark an email with a specific flag.

        Args:
            sequence_set (str): Sequence set of emails to mark.
            mark (str): Flag to apply to the email.
            folder (str, optional): Folder containing the email.
            Defaults to "inbox".

        Returns:
            IMAPCommandResult: A tuple containing:
                - A bool indicating whether the email was marked successfully.
                - A string containing a success message or an error message.

        Example:
            >>> mark_email(Mark.Seen, "1") # Marks email with UID 1 from INBOX
            >>> mark_email(Mark.Seen, "1,2,3") # Marks emails with UID 1,2,3 from INBOX
            >>> mark_email(Mark.Seen, "1:3") # Marks email with UID 1,2,3 from INBOX
            >>> mark_email(Mark.Seen, "1,3:5") # Marks email with UID 1 and 3,4,5 from INBOX
            >>> mark_email(Mark.Seen, "1:*") # Marks all emails in the INBOX
            >>> mark_email(Mark.Seen, "1,3:*") # Marks all emails in the INBOX, except email with UID 2

        References:
            https://datatracker.ietf.org/doc/html/rfc9051#name-formal-syntax (check sequence-set for more information.)
        """
        return self._mark_email(
            folder,
            sequence_set,
            "+FLAGS",
            mark,
            f"Email(s) `{sequence_set}` in `{folder}` marked with `{mark}` successfully.",
            f"There was an error while marking the email(s) `{sequence_set}` in `{folder}` with `{mark}`.",
        )

    def unmark_email(
        self,
        sequence_set: str,
        mark: str | Mark,
        folder: str = Folder.Inbox,
    ) -> IMAPCommandResult:
        """
        Unmark an email with a specific flag.

        Args:
            sequence_set (str): Sequence set of emails to unmark.
            mark (str): Flag to remove from the email.
            folder (str, optional): Folder containing the email. Defaults to "inbox".

        Returns:
            IMAPCommandResult: A tuple containing:
                - A bool indicating whether the email was unmarked successfully.
                - A string containing a success message or an error message.

        Example:
            >>> unmark_email(Mark.Seen, "1") # Removes Seen flag from email with UID 1
            >>> unmark_email(Mark.Seen, "1,2,3") # Removes Seen flag from emails with UID 1,2,3
            >>> unmark_email(Mark.Seen, "1:3") # Removes Seen flag from emails with UID 1,2,3
            >>> unmark_email(Mark.Seen, "1,3:5") # Removes Seen flag from emails with UID 1 and 3,4,5
            >>> unmark_email(Mark.Seen, "1:*") # Removes Seen flag from all emails
            >>> unmark_email(Mark.Seen, "1,3:*") Removes Seen flag from all emails, except email with UID 2

        References:
            https://datatracker.ietf.org/doc/html/rfc9051#name-formal-syntax (check sequence-set for more information.)
        """
        return self._mark_email(
            folder,
            sequence_set,
            "-FLAGS",
            mark,
            f"{mark} removed from email(s) `{sequence_set}` in `{folder}` successfully.",
            f"There was an error while unmarking the email(s) `{sequence_set}` in `{folder}` with `{mark}`.",
        )

    @handle_idle
    def move_email(
        self,
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
            >>> move_email("INBOX", "ARCHIVE", "1,2,3") # Moves emails with UID 1,2,3 from INBOX to SENT
            >>> move_email("INBOX", "ARCHIVE", "1:3") # Moves emails with UID 1,2,3 from INBOX to SENT
            >>> move_email("INBOX", "ARCHIVE", "1,3:5") # Moves emails with UID 1 and 3,4,5 from INBOX to SENT
            >>> move_email("INBOX", "ARCHIVE", "1:*") # Moves all emails in the INBOX to ARCHIVE folder
            >>> move_email("INBOX", "ARCHIVE", "1,3:*") # Moves all emails in the INBOX to ARCHIVE folder, except email with UID 2

        References:
            https://datatracker.ietf.org/doc/html/rfc9051#name-formal-syntax (check sequence-set for more information.)
        """
        self._check_folder_names(source_folder, destination_folder)

        if source_folder == destination_folder:
            return (
                True,
                f"Destination folder `{destination_folder}` is the same as the source folder `{source_folder}`.",
            )

        self.select(source_folder)

        succes_msg = f"Email(s) `{sequence_set}` moved successfully from `{source_folder}` to `{destination_folder}`."
        err_msg = f"Failed to move email(s) `{sequence_set}` from `{source_folder}` to `{destination_folder}`."

        move_result = self._parse_command_result(
            self.uid("MOVE", sequence_set, self._encode_folder(destination_folder)),
            succes_msg,
            err_msg,
        )

        if move_result[0]:
            return self._parse_command_result(self.expunge(), succes_msg, err_msg)

        return move_result

    @handle_idle
    def copy_email(
        self,
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
            >>> copy_email("INBOX", "ARCHIVE", "1") # Copies email with UID 1 to ARCHIVE from INBOX.
            >>> copy_email("INBOX", "ARCHIVE", "1,2,3") # Copies emails with UID 1, 2, 3 to ARCHIVE from INBOX.
            >>> copy_email("INBOX", "ARCHIVE", "1:3") # Copies emails with UID 1,2,3 to ARCHIVE from INBOX.
            >>> copy_email("INBOX", "ARCHIVE", "1,3:5") # Copies email with UID 1 and 3,4,5 to ARCHIVE from INBOX.
            >>> copy_email("INBOX", "ARCHIVE", "1:*") # Copies all emails in the INBOX to ARCHIVE folder
            >>> copy_email("INBOX", "ARCHIVE", "1,3:*") # Copies all emails in the INBOX to ARCHIVE folder, except email with UID 2

        References:
            https://datatracker.ietf.org/doc/html/rfc9051#name-formal-syntax (check sequence-set for more information.)
        """
        self._check_folder_names(source_folder, destination_folder)

        self.select(source_folder)

        succes_message = f"Email(s) `{sequence_set}` copied successfully from `{source_folder}` to `{destination_folder}`."
        err_msg = f"Failed to copy email(s) `{sequence_set}` from `{source_folder}` to `{destination_folder}`."

        copy_result = self._parse_command_result(
            self.uid("COPY", sequence_set, self._encode_folder(destination_folder)),
            succes_message,
            err_msg,
        )

        if copy_result[0]:
            return self._parse_command_result(self.expunge(), succes_message, err_msg)

        return copy_result

    @handle_idle
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
            >>> delete_email("INBOX", "1,2,3") # Deletes emails with UID 1,2, 3
            >>> delete_email("INBOX", "1:3") # Deletes emails with UID 1,2,3
            >>> delete_email("INBOX", "1,3:5") # Deletes emails with UID 1 and 3,4,5
            >>> delete_email("INBOX", "1:*") # Deletes all emails in the folder
            >>> delete_email("INBOX", "1,3:*") # Deletes all emails in the folder except email with UID 2

        References:
            https://datatracker.ietf.org/doc/html/rfc9051#name-formal-syntax (check sequence-set for more information.)
        """
        self._check_folder_names(folder)

        try:
            trash_mailbox_name = self.find_matching_folder(Folder.Trash, False)
            if folder != trash_mailbox_name or folder != Folder.Trash:
                status, _ = self.move_email(folder, trash_mailbox_name, sequence_set)
                if not status:
                    raise IMAPManagerException(
                        f"Error while moving email(s) `{sequence_set}` to trash folder for deletion."
                    )
        except Exception as e:
            raise IMAPManagerException(
                f"Error while moving email(s) `{sequence_set}` to trash folder for deletion: `{str(e)}`."
            ) from e

        self.select(self._encode_folder(trash_mailbox_name))

        success_msg = f"Email(s) `{sequence_set}` deleted from `{folder}` successfully."
        err_msg = f"There was an error while deleting the email(s) `{sequence_set}` from `{folder}`."

        delete_result = self._parse_command_result(
            self.uid("STORE", sequence_set, "+FLAGS", "\\Deleted"), success_msg, err_msg
        )

        if delete_result[0]:
            return self._parse_command_result(self.expunge(), success_msg, err_msg)

        return delete_result

    @handle_idle
    def create_folder(
        self, folder_name: str, parent_folder: str | None = None
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
        self._check_folder_names(folder_name, parent_folder)

        if parent_folder:
            if parent_folder not in self.get_folders():
                self.create_folder(parent_folder)

            folder_name = f"{parent_folder}{self._hierarchy_delimiter}{folder_name}"

        return self._parse_command_result(
            self.create(self._encode_folder(folder_name)),
            f"Folder `{folder_name}` created successfully.",
            f"There was an error while creating folder `{folder_name}`.",
        )

    @handle_idle
    def delete_folder(
        self, folder_name: str, delete_subfolders: bool = False
    ) -> IMAPCommandResult:
        """
        Delete an existing email folder.

        Args:
            folder_name (str): Name of the folder to delete.
            subfolders (bool, optional): Whether to also delete subfolders.
                                        Defaults to False.

        Returns:
            IMAPCommandResult: A tuple containing:
                - A bool indicating whether the folder was deleted successfully.
                - A string containing a success message or an error message.

        Example:
            >>> delete_folder("RED") # RED/LIGHTRED, RED/DARKRED wont be deleted.
            (True, "Folder `RED` deleted successfully.")
            >>> delete_folder("RED", true) # RED/LIGHTRED, RED/DARKRED will be deleted.
            (True, "Folder `RED` deleted successfully.")
        """
        self._check_folder_names(folder_name)

        if delete_subfolders:
            for subfolder in self.get_folders(folder_name):
                self.delete_folder(subfolder, True)

        return self._parse_command_result(
            self.delete(self._encode_folder(folder_name)),
            f"Folder `{folder_name}` deleted successfully.",
            f"There was an error while deleting folder `{folder_name}`.",
        )

    @handle_idle
    def move_folder(
        self, folder_name: str, destination_folder: str
    ) -> IMAPCommandResult:
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
            >>> move_folder("RED", "COLORS")
            (True, "Folder `RED` moved to `COLORS` successfully. New location is `COLORS/RED`")
            >>> move_folder("RED", "COLORS/DARK") # Subfolders of `RED` will be also moved under `COLORS/DARK`.
            (True, "Folder `RED` moved to `COLORS/DARK` successfully. New location is `COLORS/DARK/RED`")
            >>> move_folder("RED/DARKRED", "COLORS")
            (True, "Folder `RED/DARKRED` moved to `COLORS` successfully. New location is `COLORS/DARKRED`")
            >>> move_folder("RED/DARKRED", "COLORS/DARK")
            (True, "Folder `RED/DARKRED` moved to `COLORS/DARK` successfully. New location is `COLORS/DARK/DARKRED`")
            >>> move_folder("RED/DARKRED", "")
            (True, "Folder `RED/DARKRED` moved to `` successfully. New location is `DARKRED`")
        """
        self._check_folder_names(folder_name)
        if destination_folder != "":
            self._check_folder_names(destination_folder)
            destination_folder += self._hierarchy_delimiter

        *folder_name_parent, folder_name_target = folder_name.split(
            self._hierarchy_delimiter
        )
        if self._hierarchy_delimiter.join(folder_name_parent) in self.get_folders():
            destination_folder = f"{destination_folder}{folder_name_target}"
        else:
            destination_folder = f"{destination_folder}{folder_name}"

        destination_folder = destination_folder.strip()

        return self._parse_command_result(
            self.rename(
                self._encode_folder(folder_name),
                self._encode_folder(destination_folder),
            ),
            f"Folder `{folder_name}` moved to `{destination_folder}` successfully.",
            f"There was an error while moving folder `{folder_name}` to `{destination_folder}`.",
        )

    @handle_idle
    def rename_folder(
        self, folder_name: str, new_folder_name: str
    ) -> IMAPCommandResult:
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
            >>> rename_folder("BLUE/DARKBLUE", "LIGHTBLUE")
            (True, "Folder `BLUE/DARKBLUE` renamed to `BLUE/LIGHTBLUE` successfully.")
        """
        self._check_folder_names(folder_name, new_folder_name)

        *folder_name_parent, _ = folder_name.split(self._hierarchy_delimiter)
        folder_name_parent = self._hierarchy_delimiter.join(folder_name_parent)
        if folder_name_parent in self.get_folders():
            new_folder_name = (
                f"{folder_name_parent}{self._hierarchy_delimiter}{new_folder_name}"
            )

        return self._parse_command_result(
            self.rename(
                self._encode_folder(folder_name), self._encode_folder(new_folder_name)
            ),
            f"Folder `{folder_name}` renamed to `{new_folder_name}` successfully.",
            f"There was an error while renaming folder `{folder_name}` to `{new_folder_name}`.",
        )


__all__ = [
    "IMAPManager",
    "IMAPCommandResult",
    "IMAPManagerException",
    "IMAPManagerLoggedOutException",
    "Mark",
    "Folder",
]
