import imaplib, threading, re, base64, email, time
from typing import List, MappingProxyType
from typing_extensions import override
from datetime import datetime
from enum import Enum

from .utils import extract_domain, choose_positive, truncate_text, contains_non_ascii, convert_date_to_iso, make_size_human_readable
from .types import SearchCriteria, LoginException, Email, Attachment, Inbox

# General consts
IMAP_SERVERS = MappingProxyType({
    "gmail": "imap.gmail.com",
    "yahoo": "imap.mail.yahoo.com",
    "outlook": "outlook.office365.com",
    "hotmail": "outlook.office365.com",
    'yandex': 'imap.yandex.com',
})
IMAP_PORT = 993
FOLDER_FLAG_NAMES = (
    b'\\All', 
    b'\\Archive', 
    b'\\Drafts', 
    b'\\Flagged', 
    b'\\Junk', 
    b'\\Sent', 
    b'\\Trash'
)
# https://datatracker.ietf.org/doc/html/rfc9051#name-flags-message-attribute
MARK_LIST = ('flagged', 'seen', 'answered', 'unflagged', 'unseen', 'unanswered')
MARK_MAP = MappingProxyType({
    "flagged": "\\Flagged",
    "seen": "\\Seen",
    "answered": "\\Answered",
    #"deleted": "\\Deleted",
    #"draft": "\\Draft",
    #"spam": "\\Spam"
})
INBOX = 'INBOX'
ALL = 'ALL'

# Regular expressions
CID_PATTERN = re.compile(r'<img src="cid:([^"]+)"')
FLAG_PATTERN = re.compile(r'\\([a-zA-Z]+)')

# Custom consts
LOGIN_TRY_LIMIT = 3
BODY_SHORT_THRESHOLD = 50
MAX_FOLDER_NAME_LENGTH = 100

# Timeouts (in seconds)
CONN_TIMEOUT = 30 
IDLE_TIMEOUT = 30 * 60
WAIT_RESPONSE_TIMEOUT = 3 * 60

# Types
type CommandResult = tuple[bool, str]

# Enums
class WaitResponse(Enum):
    IDLE = "IDLE"
    EXISTS = "EXISTS"
    DONE = "DONE"
    BYE = "BYE"

class ImapException(Exception):
    pass

class ImapManager(imaplib.IMAP4_SSL):
    def __init__(
        self, 
        email_address: str, 
        password: str, 
        host: str = "", 
        port: int = IMAP_PORT, 
        ssl_context: any = None,
        timeout: int = CONN_TIMEOUT
    ):
        super().__init__(
            host or self.__find_imap_server(email_address),
            port or IMAP_PORT,
            ssl_context=ssl_context,
            timeout=choose_positive(timeout, CONN_TIMEOUT)
        )

        self.login(email_address, password)
        
        self.__current_folder = (INBOX, False)

        self.__is_idle = False
        self.__current_idle_start_time = None
        self.__current_idle_tag = None
        self.__wait_for_response = None
        
        self.__readline_thread_event = None
        self.__readline_thread = None

        self.__idle_thread_event = None
        self.__idle_thread = None

    def __find_imap_server(self, email_address: str) -> str:
        """
        Determines the IMAP server address for a given email address.

        Args:
            email_address (str): The email address for which to find the IMAP server.

        Returns:
            str: The IMAP server address associated with the email's domain.

        Raises:
            ImapException: If the email domain is not supported or not found in the IMAP_SERVERS mapping.

        Example:
            >>> email_address = "user@gmail.com"
            >>> self.__find_imap_server(email_address)
            "imap.gmail.com"

            >>> email_address = "user@unknown.com"
            >>> self.__find_imap_server(email_address)
            ImapException: Unsupported email domain
        """
        try:
            return IMAP_SERVERS[extract_domain(email_address)]
        except KeyError:
            raise ImapException("Unsupported email domain")

    @override
    def login(self, user: str, password: str) -> tuple[str, any]:
        """
        Authenticates the user with the IMAP server using the provided credentials.

        Args:
            user (str): The username or email address of the account.
            password (str): The account's password.

        Returns:
            tuple[str, any]: A tuple containing the status string ("OK", "NO", etc.)
                            and the server's response object.

        Raises:
            ImapException: If the login process fails after exceeding the allowed retry limit.

        Notes:
            - UTF-8 encoding is enabled after successful authentication.
            - Supports both ASCII and non-ASCII credentials.
        """
        try_limit = LOGIN_TRY_LIMIT
        for _ in range(try_limit):
            try:
                status, response = None, None
                if contains_non_ascii(user) or contains_non_ascii(password):
                    status, response = self.authenticate("PLAIN", lambda x: bytes("\x00" + user + "\x00" + password, "utf-8"))
                else:
                    status, response = super().login(user, password)
                self._simple_command('ENABLE', 'UTF8=ACCEPT')
                return status, response
            except Exception as e:
                try_limit -= 1
                if try_limit == 0:
                    raise ImapException("Could not connect to the target imap server. Error: " + str(e))

    @override
    def logout(self) -> tuple[str, any]:
        """
        Logs out from the IMAP server and closes any open mailboxes.

        Returns:
            tuple[str, any]: A tuple containing the status string ("OK", "NO", etc.)
                            and the server's response object.

        Raises:
            ImapException: If an error occurs during the logout process.

        Notes:
            - If the state is "SELECTED," the mailbox is closed before disconnecting.
        """
        try:
            try:
                if self.state == "SELECTED":
                    self.close()
            except Exception as e:
                print("Could not close mailbox: {}".format(str(e)))
                pass

            return super().logout()
        except Exception as e:
            raise ImapException("Could not disconnect from the target imap server: {}".format(str(e)))
    
    @override
    def select(self, mailbox: str = INBOX, readonly: bool = False):
        """
        Selects a mailbox for further operations.

        Args:
            mailbox (str): The name of the mailbox to select. Defaults to "INBOX".
            readonly (bool): If True, opens the mailbox in read-only mode. Defaults to False.

        Raises:
            ImapException: If the mailbox cannot be selected or an invalid mailbox name is provided.

        Notes:
            - Prevents re-selecting the currently active mailbox with the same mode.
            - Ensures the folder name is properly encoded and valid.
        """
        if self.__current_folder[0] != mailbox or self.__current_folder[1] != readonly:
            self.__check_folder_names(mailbox)
            self.__ensure_command(super().select(self.__encode_folder(mailbox), readonly))
            self.__current_folder = (mailbox, readonly)
        
    def __handle_conn(func):
        """
        Decorator to manage the connection state before and after a method call.

        Ensures the connection exits IDLE mode before executing the wrapped method 
        and restores it to IDLE mode afterward if it was previously idling.

        Args:
            func (callable): The method to wrap with connection handling logic.

        Returns:
            callable: The wrapped method with connection management.
        """
        def wrapper(self, *args, **kwargs):
            # TODO: Improve error handling
            try:
                was_idle_before_call = self.__is_idle
                if was_idle_before_call:
                    self.done()
                response = func(self, *args, **kwargs)
                if was_idle_before_call:
                    self.idle()
                return response
            except Exception as e:
                #self.logout()
                return False, str(e)
        return wrapper
    
    def __parse_command_result(self, 
        result: tuple[str, list[bytes | None]], 
        success_message: str = None,
        failure_message: str = None
    ) -> CommandResult:
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
            CommandResult: A tuple containing:
                - A boolean indicating success (True for "OK", False otherwise).
                - The server's response message as a string.

        Raises:
            ImapException: If parsing the command result fails.

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
        """
        try:
            if result[0] == "OK":
                return True, success_message or result[1][0].decode("utf-8")
            else:
                return False, failure_message + ": " + result[1][0].decode("utf-8")
        except Exception as e:
            raise ImapException("There was an error while parsing command result: {}".format(str(e)))

    def __ensure_command(self, response: tuple[str, list[bytes | None]]):
        """
        Ensures an IMAP command was successful.

        Args:
            response (tuple[str, list[bytes | None]]): 
                The command response, where the first element is the status 
                (e.g., "OK") and the second contains additional data.

        Raises:
            ImapException: If the response status is not "OK."
        """
        if response[0] != "OK":
            raise ImapException("IMAP command failed: {}".format(response[1][0].decode("utf-8")))
        
    @override
    @__handle_conn
    def list(self) -> list[str]:
        """
        Retrieve a list of all email folders.

        Returns:
            list[str]: List of folder names in the email account
        """
        try:
            return [self.__decode_folder(i) for i in super().list()[1] if i.find(b'\\NoSelect') == -1]
        except Exception as e:
            raise ImapException("There was an error while listing folders: {}".format(str(e)))
    
    def idle(self) -> None:
        if not self.__is_idle:
            self.select(INBOX)
            self.__current_idle_tag = self._new_tag()
            self.send(b"%s IDLE\r\n" % self.__current_idle_tag)
            print("[{}] ---> __idle() IDLE command sent with tag: {}.".format(datetime.now(), self.__current_idle_tag))
            self.__readline()
            self.__wait_response(WaitResponse.IDLE)

    def done(self) -> None:
        if self.__is_idle:
            self.send(b"DONE\r\n")
            print("[{}] ---> __done() DONE command sent for {}.".format(datetime.now(), self.__current_idle_tag))
            self.__wait_response(WaitResponse.DONE)
            print("[{}] ---> __done() wait_response() finished for DONE command, reidle:.".format(datetime.now()))
    
    def __wait_response(self, wait_response: WaitResponse) -> None:
        counter = 0
        while self.__wait_for_response != wait_response:
            time.sleep(1)
            counter += 1
            if counter > WAIT_RESPONSE_TIMEOUT:
                print("[{}] ---> __wait_response() timeout reached for {}.".format(datetime.now(), wait_response))
                break
        
        self.__wait_for_response = None

    def __handle_idle_response(self) -> None:
        print("[{}] ---> __readline() IDLE response received for {}.".format(datetime.now(), self.__current_idle_tag))
        self.__is_idle = True
        self.__current_idle_start_time = time.time()

        if not self.__idle_thread_event:
            self.__idle_thread_event = threading.Event()
        self.__idle_thread_event.clear()

        if not self.__idle_thread or not self.__idle_thread.is_alive():
            self.__idle_thread = threading.Thread(target=self.__idle)
            self.__idle_thread.start()

        self.__wait_for_response = WaitResponse.IDLE
        print("[{}] ---> __readline() IDLE response handled, IDLE thread started.".format(datetime.now()))

    def __handle_done_response(self) -> None:
        print("[{}] ---> __readline() DONE response received for {}.".format(datetime.now(), self.__current_idle_tag))
        self.__is_idle = False
        self.__current_idle_tag = None

        self.__idle_thread_event.set()        
        self.__readline_thread_event.set()

        self.__wait_for_response = WaitResponse.DONE
        print("[{}] ---> __readline() DONE response handled.".format(datetime.now()))
    
    def __handle_bye_response(self) -> None:
        # BYE response
        print("[{}] ---> __readline() BYE response received.".format(datetime.now()))
        # TODO: Implement reconnect
        self.__wait_for_response = WaitResponse.BYE

    def __handle_exists_response(self, response: bytes) -> None:
        # EXISTS response
        print("[{}] ---> __readline() EXISTS response received.".format(datetime.now()))
        #self.done()
        #self.idle()
        self.__wait_for_response = WaitResponse.EXISTS
    
    def __handle_response(self, response: bytes) -> None:
        if b'idling' in response:
            self.__handle_idle_response()
        elif b'OK' in response and bytes(self.__current_idle_tag) in response:
            self.__handle_done_response()
        elif b'BYE' in response:
            self.__handle_bye_response()
        elif b'EXISTS' in response:
            self.__handle_exists_response(response)
        
    def __idle(self) -> None:
        while not self.__idle_thread_event.is_set():
            print("[{}] ---> IDLING for {}.".format(datetime.now(), self.__current_idle_tag))
            time.sleep(1)
            if time.time() - self.__current_idle_start_time > IDLE_TIMEOUT:
                print("[{}] ---> IDLING timeout reached for {}.".format(datetime.now(), self.__current_idle_tag))
                self.done()
                self.idle()
            
    def __readline(self) -> None:    
        def readline_thread() -> None:
            while not self.__readline_thread_event.is_set():
                print("[{}] ---> __readline() waiting for response, wait response: {}.".format(datetime.now(), self.__wait_for_response))
                response = self.readline()
                print("[{}] ---> __readline() response: {}.".format(datetime.now(), response))
                if response:
                    self.__handle_response(response)
                time.sleep(1)

        if not self.__readline_thread_event:
            self.__readline_thread_event = threading.Event()
        self.__readline_thread_event.clear()

        if not self.__readline_thread or not self.__readline_thread.is_alive():
            self.__readline_thread = threading.Thread(target=readline_thread)
            self.__readline_thread.start()

    def get_folder_name_by_flag_name(self, flag_name: bytes) -> bytes | None:
        """
        Retrieve the folder name corresponding to a specific IMAP flag name.

        This method is useful for handling cases where a client's folder names 
        are localized in a different language. For example:
        - If the client's inbox is named "Gelen Kutusu"(Inbox, turkish) this method will return "INBOX" 
        if the flag name is `b'\\Inbox'`.
        - Similarly, it will return "Çöp Kutusu"(Trash, turkish) for the flag name `b'\\Trash'`.

        Args:
            flag_name (bytes): The IMAP flag name (e.g., `b'\\Inbox'` or `b'\\Trash'`).

        Returns:
            bytes | None: The folder name in bytes if a match is found; otherwise, None.
        """
        if flag_name not in FOLDER_FLAG_NAMES:
            return None

        status, folders_as_bytes = super().list()
        if status == "OK" and folders_as_bytes and isinstance(folders_as_bytes, list):
            for folder_as_bytes in folders_as_bytes:
                if flag_name == folder_as_bytes:
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
            ImapException: If encoding the folder name fails.
        """
        try:
            return ('"' + folder + '"').encode("utf-8")
        except Exception as e:
            raise ImapException("Error while encoding folder name", e)

    def __decode_folder(self, folder: bytes) -> str:
        """
        Decode a folder name from a byte string returned by an IMAP server.

        Args:
            folder (bytes): The byte string containing the folder name.

        Returns:
            str: The decoded and cleaned folder name.

        Raises:
            ImapException: If decoding the folder name fails.
        """
        try:
            # Most of the servers return folder name as b'(\\HasNoChildren) "/" "INBOX"'
            # But some servers like yandex return folder name as b'(\\HasNoChildren) "|" "INBOX"'
            # So we're replacing "|" with "/" to make it consistent
            return folder.decode().replace(' "|" ', ' "/" ').split(' "/" ')[1].replace('"', '')
        except Exception as e:
            raise ImapException("Error while decoding folder name", e)

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
            ImapException: If the folder name is invalid and raise_error is True
        """
        if isinstance(folders, str):
            folders = [folders]
        
        for folder_name in folders:
            folder_name_length = len(folder_name)
            if folder_name is None or folder_name == "" or folder_name_length > MAX_FOLDER_NAME_LENGTH or folder_name_length < 1:
                if raise_error:
                    raise ImapException("Invalid folder name: {}".format(folder_name))
                return False
        
        return True

    @__handle_conn
    def get_email_flags(self, uid: str) -> list:
        """
        Retrieve flags associated with a specific email.

        Args:
            uid (str): Unique identifier of the email

        Returns:
            list: List of email flags
        """
        if self.state != "SELECTED":
            # Since uid's are unique within each mailbox, we can't just select INBOX
            # or something like that if there is no mailbox selected.
            raise ImapException("Folder should be selected before fetching flags")

        try:
            flags = self.uid('FETCH', uid, '(FLAGS)')[1][0]
            if flags:
                flags = flags.decode()
                flags = FLAG_PATTERN.findall(flags)
        except Exception as e:
            raise ImapException("Error while fetching email flags", e)
        
        return flags or []

    def __build_search_criteria_query(self, search_criteria: SearchCriteria) -> str:
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
                Input: criteria="FROM", search_keys=["a@mail.com", "b@mail.com", "c@mail.com"]
                Output: 'OR (FROM "a@mail.com") (OR (FROM "b@mail.com") (FROM "c@mail.com"))'
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
                Input: criteria="FROM", value=["a@mail.com", "b@mail.com"]
                Output: ' (FROM "a@mail.com") (FROM "b@mail.com")'
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
        search_criteria_query += add_criterion("SUBJECT", search_criteria.subject)
        search_criteria_query += add_criterion("SINCE", search_criteria.since)
        search_criteria_query += add_criterion("BEFORE", search_criteria.before)
        search_criteria_query += add_criterion("TEXT", search_criteria.include)
        search_criteria_query += add_criterion("NOT TEXT", search_criteria.exclude)
        search_criteria_query += add_criterion('', search_criteria.flags)
        return search_criteria_query.strip()

    @__handle_conn
    def get_emails(
        self,
        folder: str = INBOX,
        search: str | SearchCriteria = ALL,
        offset: int = 0
    ) -> Inbox:
        """
        Retrieve emails from a specified folder based on search criteria.

        Args:
            folder (str, optional): Folder to search in. Defaults to "inbox".
            search (str | SearchCriteria, optional): Search criteria. Defaults to "ALL".
            offset (int, optional): Starting index for email retrieval. Defaults to 0.

        Returns:
            dict: Dictionary of emails matching the search criteria
        """
        if offset < 0:
            raise ImapException("Invalid offset: {}".format(offset))

        self.select(folder, readonly=True)
        
        # Creating search query
        search_criteria_query = ''
        try:
            search_criteria_query = ''
            must_have_attachment = False
            if isinstance(search, SearchCriteria):
                must_have_attachment = search.has_attachments
                search_criteria_query = self.__build_search_criteria_query(search) or ALL
            else:
                search_criteria_query = search or ALL
        except Exception as e:
            raise ImapException("Error while building search query", e)

        # Getting email uids
        try:
            _, uids = self.uid('search', None, search_criteria_query.encode("utf-8") if search_criteria_query else ALL)
            uids = uids[0].split()[::-1]
        except Exception as e:
            raise ImapException("Error while getting email uids, search query was `{}`".format(search_criteria_query), e)

        if not uids:
            return Inbox(folder=folder, emails=[], total=0)

        # Fetching emails
        emails = []
        try:
            for uid in uids[offset: offset + 10]:
                """
                _, data = M.fetch(num, '(BODY.PEEK[HEADER.FIELDS (CONTENT-TYPE)])')
                if b"multipart/mixed" in data[0][1]:
                    print("Found multipart/mixed: ", num
                """
                _, message = self.uid('fetch', uid, '(RFC822)')
                message = email.message_from_bytes(message[0][1], policy=email.policy.default)

                payload = [message]
                if message.is_multipart():
                    if must_have_attachment and message.get_content_type() != "multipart/mixed":
                        continue
                    payload = message.walk()

                body = ""
                is_body_html = False
                for part in payload:
                    content_type = part.get_content_type()
                    file_name = part.get_filename()

                    is_body_html = content_type == "text/html"
                    if (file_name is None and content_type == "text/plain") or (is_body_html and not body):
                        body = part.get_payload(decode=True)
                        body = body.decode(part.get_content_charset() or "utf-8") if body else ""

                # TODO: Check if this is required
                #body = BeautifulSoup(body, "html.parser").get_text() if is_body_html else body
                #body = re.sub(r'<br\s*/?>', '', body).strip() if body != b'' else ""
                #body = re.sub(r'[\n\r\t]+| +', ' ', body).strip()

                emails.append(Email(
                    uid=uid.decode(),
                    sender=message["From"],
                    receiver=message["To"] if "To" in message else "",
                    subject=message["Subject"],
                    body_short=truncate_text(body, BODY_SHORT_THRESHOLD),
                    date=convert_date_to_iso(message["Date"]),
                    flags=self.get_email_flags(uid) or []
                ))
        except Exception as e:
            raise ImapException("Error while fetching emails, fetched email length was `{}`".format(len(emails)), e)

        return Inbox(folder=folder, emails=emails, total=len(uids))
    
    @__handle_conn
    def get_email_content(
        self,
        uid: str,
        folder: str = INBOX
    ) -> Email:
        """
        Retrieve full content of a specific email.

        Args:
            uid (str): Unique identifier of the email
            folder (str, optional): Folder containing the email. Defaults to "inbox".

        Returns:
            dict: Detailed email content
        """
        self.select(folder, readonly=True)
        
        # Get body and attachments
        body, attachments = "", []
        try:
            _, message = self.uid('fetch', uid, '(RFC822)')
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
            raise ImapException("There was a problem with getting email content: {}".format(e))

        try:
            # Get inline attachments
            if attachments:
                for match in CID_PATTERN.finditer(body):
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
            print("There was a problem with inline attachments: {}".format(e))
            pass
        
        try:
            self.mark_email(uid, "Seen", folder)
        except Exception as e:
            # If there is a problem with marking the email as seen
            # just ignore it.
            print("There was a problem with marking the email as seen: {}".format(e))
            pass

        return Email(
            uid=uid,
            sender=message["From"],
            receiver=message["To"] if "To" in message else "",
            subject=message["Subject"],
            body=body,
            date=convert_date_to_iso(message["Date"]),
            flags=self.get_email_flags(uid) or [],
            attachments=attachments
        )

    @__handle_conn
    def mark_email(
        self,
        uid: str,
        mark: str,
        folder: str = INBOX
    ) -> CommandResult:
        """
        Mark an email with a specific flag.

        Args:
            uid (str): Unique identifier of the email
            mark (str): Flag to apply to the email. Add "un" to negate the flag
                        e.g. "seen" or "unseen" or "flagged" or "unflagged"
            folder (str, optional): Folder containing the email. Defaults to "inbox".

        Returns:
            bool: True if email marked successfully, False otherwise
        """
        self.__check_folder_names(folder)
        
        if not mark or mark not in MARK_LIST:
            raise ImapException(f"Invalid mark: {mark}. Please use one of the following: {', '.join(MARK_LIST)}")

        if mark in self.get_email_flags(uid):
            return CommandResult(success=True, message="Email already marked")
        
        mark = mark.lower()
        mark_type = "-" if mark[0] + mark[1] == "un" else "+"
        mark = mark[2:] if mark_type == "-" else mark
        command = mark_type + "FLAGS"

        self.select(folder)

        success_msg = "Email marked successfully"
        err_msg = "There was an error while marking the email"

        mark_result = self.uid('STORE', uid, command, MARK_MAP[mark])

        if mark_result[0]:
            return self.__parse_command_result(
                self.expunge(),
                success_msg,
                err_msg
            )
        
        return mark_result

    @__handle_conn
    def move_email(self, uid: str, source_folder: str, destination_folder: str) -> CommandResult:
        """
        Move an email from one folder to another.

        Args:
            uid (str): Unique identifier of the email
            source_folder (str): Current folder of the email
            destination_folder (str): Target folder to move the email to

        Returns:
            bool: True if email moved successfully, False otherwise
        """
        self.__check_folder_names([source_folder, destination_folder])
        
        if source_folder == destination_folder:
            return CommandResult(success=True, message="Email already in destination folder")
        
        self.select(source_folder)

        success_msg = "Email moved successfully"
        err_msg = "There was an error while moving the email"

        move_result = self.uid('MOVE', uid, self.__encode_folder(destination_folder))

        if move_result[0]:
            return self.__parse_command_result(
                self.expunge(),
                success_msg,
                err_msg
            )
        
        return move_result
        
    @__handle_conn
    def copy_email(self, uid: str, source_folder: str, destination_folder: str) -> CommandResult:
        """
        Create a copy of an email in another folder.

        Args:
            uid (str): Unique identifier of the email
            source_folder (str): Current folder of the email
            destination_folder (str): Target folder to copy the email to

        Returns:
            bool: True if email copied successfully, False otherwise
        """
        self.__check_folder_names([source_folder, destination_folder])
    
        self.select(source_folder)

        success_msg = "Email copied successfully"
        err_msg = "There was an error while copying the email"

        copy_result = self.uid('COPY', uid, self.__encode_folder(destination_folder))

        if copy_result[0]:
            return self.__parse_command_result(
                self.expunge(),
                success_msg,
                err_msg
            )
        
        return copy_result

    @__handle_conn
    def delete_email(self, uid: str, folder: str) -> CommandResult:
        """
        Delete an email from a specific folder.

        Args:
            uid (str): Unique identifier of the email
            folder (str): Folder containing the email

        Returns:
            bool: True if email deleted successfully, False otherwise
        """
        self.__check_folder_names(folder)

        trash_mailbox_name = self.get_folder_name_by_flag_name(b"\\Trash")

        try:
            if folder != trash_mailbox_name:
                self.move_email(uid, folder, trash_mailbox_name)
        except Exception as e:
            raise ImapException("Error while moving email to trash folder for deletion", e)
        
        self.select(trash_mailbox_name)
    
        success_msg = "Email deleted successfully"
        err_msg = "There was an error while deleting the email"

        delete_result = self.__parse_command_result(
            self.uid('STORE', uid, '+FLAGS', '\\Deleted'),
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

    @__handle_conn
    def create_folder(self, folder_name: str, parent_folder: str | None = None) -> CommandResult:
        """
        Create a new email folder.

        Args:
            folder_name (str): Name of the new folder
            parent_folder (str, optional): Parent folder for nested folder creation. 
                                           Defaults to None.

        Returns:
            bool: True if folder created successfully, False otherwise
        """
        self.__check_folder_names([folder_name, parent_folder])
        
        if parent_folder:
            folder_name = f"{parent_folder}/{folder_name}"

        return self.__parse_command_result(
            self.create(self.__encode_folder(folder_name)),
            "Folder created successfully",
            "There was an error while creating the folder"
        )

    @__handle_conn
    def delete_folder(self, folder_name: str) -> CommandResult:
        """
        Delete an existing email folder.

        Args:
            folder_name (str): Name of the folder to delete

        Returns:
            bool: True if folder deleted successfully, False otherwise
        """
        self.__check_folder_names(folder_name)

        return self.__parse_command_result(
            self.delete(self.__encode_folder(folder_name)),
            "Folder deleted successfully",
            "There was an error while deleting the folder"
        )

    @__handle_conn
    def move_folder(self, folder_name: str, destination_folder: str) -> CommandResult:
        """
        Move a folder to a new location.

        Args:
            folder_name (str): Name of the folder to move
            destination_folder (str): Target location for the folder

        Returns:
            bool: True if folder moved successfully, False otherwise
        """
        self.__check_folder_names([folder_name, destination_folder])
        
        if "/" in folder_name:
            destination_folder = f"{destination_folder}/{folder_name.split("/")[-1]}"

        return self.__parse_command_result(
            self.rename(
                self.__encode_folder(folder_name),
                self.__encode_folder(destination_folder)
            ),
            "Folder moved successfully",
            "There was an error while moving the folder"
        )

    @__handle_conn
    def rename_folder(self, folder_name: str, new_folder_name: str) -> CommandResult:
        """
        Rename an existing email folder.

        Args:
            folder_name (str): Current name of the folder
            new_folder_name (str): New name for the folder

        Returns:
            bool: True if folder renamed successfully, False otherwise
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
            "There was an error while renaming the folder"
        )
    