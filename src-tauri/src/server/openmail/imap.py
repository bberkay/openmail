import imaplib, threading, re, base64, email, time, socket, select
from typing import List, Literal, MappingProxyType
from datetime import datetime

from .utils import extract_domain, choose_positive, truncate_text, contains_non_ascii, convert_date_to_iso, make_size_human_readable
from .types import SearchCriteria, LoginException

# General consts
IMAP_SERVERS = MappingProxyType({
    "gmail": "imap.gmail.com",
    "yahoo": "imap.mail.yahoo.com",
    "outlook": "outlook.office365.com",
    "hotmail": "outlook.office365.com",
    'yandex': 'imap.yandex.com',
})
IMAP_PORT = 993
LOGIN_TRY_LIMIT = 3
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
MARK_MAP = MappingProxyType({
    "flagged": "\\Flagged",
    "seen": "\\Seen",
    "answered": "\\Answered",
    #"deleted": "\\Deleted",
    #"draft": "\\Draft",
    #"spam": "\\Spam"
})
INBOX = "INBOX"
CID_RE_COMPILE = re.compile(r'<img src="cid:([^"]+)"')

# Custom consts
BODY_SHORT_THRESHOLD = 50

# Timeouts (in seconds)
CONN_TIMEOUT = 30 
IDLE_TIMEOUT = 30 * 60 

class IMAPManager():
    def __init__(
        self, 
        email_address: str, 
        password: str, 
        host: str = "", 
        port: int = IMAP_PORT, 
        ssl_context: any = None,
        timeout: int = CONN_TIMEOUT
    ):
        self.__imap = imaplib.IMAP4_SSL(
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
        try:
            return IMAP_SERVERS[extract_domain(email_address)]
        except KeyError:
            raise Exception("Unsupported email domain")

    def login(self, user: str, password: str) -> tuple[str, any]:
        try_limit = LOGIN_TRY_LIMIT
        for _ in range(try_limit):
            try:
                status, response = None, None
                if contains_non_ascii(user) or contains_non_ascii(password):
                    status, response = self.authenticate("PLAIN", lambda x: bytes("\x00" + user + "\x00" + password, "utf-8"))
                else:
                    status, response = self.__imap.login(user, password)
                self.__imap._simple_command('ENABLE', 'UTF8=ACCEPT')
                return status, response
            except Exception as e:
                try_limit -= 1
                if try_limit == 0:
                    raise Exception("3 failed login attempts. Error: " + str(e))

    def logout(self) -> tuple[str, any]:
        if self.__imap.state == "SELECTED":
            self.__imap.close()
        return self.__imap.logout()

    def __handle_conn(func):
        def wrapper(self, *args, **kwargs):
            try:
                was_idle_before_call = self.__is_idle
                if was_idle_before_call:
                    self.done()
                response = func(self, *args, **kwargs)
                if was_idle_before_call:
                    self.idle()
                return response
            except Exception as e:
                #self.__imap.logout()
                return False, str(e)
        return wrapper

    def idle(self) -> None:
        if not self.__is_idle:
            self.select(INBOX)
            self.__current_idle_tag = self._new_tag()
            self.send(b"%s IDLE\r\n" % self.__current_idle_tag)
            print("[{}] ---> __idle() IDLE command sent with tag: {}.".format(datetime.now(), self.__current_idle_tag))
            self.__readline()
            self.__wait_response("IDLE")

    def done(self) -> None:
        if self.__is_idle:
            self.send(b"DONE\r\n")
            print("[{}] ---> __done() DONE command sent for {}.".format(datetime.now(), self.__current_idle_tag))
            self.__wait_response("DONE")
            print("[{}] ---> __done() wait_response() finished for DONE command, reidle:.".format(datetime.now()))
    
    def __wait_response(self, wait_key: str) -> None:
        while self.__wait_for_response != wait_key:
            time.sleep(1)
        
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

        self.__wait_for_response = "IDLE"
        print("[{}] ---> __readline() IDLE response handled, IDLE thread started.".format(datetime.now()))

    def __handle_done_response(self) -> None:
        print("[{}] ---> __readline() DONE response received for {}.".format(datetime.now(), self.__current_idle_tag))
        self.__is_idle = False
        self.__current_idle_tag = None

        self.__idle_thread_event.set()        
        self.__readline_thread_event.set()

        self.__wait_for_response = "DONE"
        print("[{}] ---> __readline() DONE response handled.".format(datetime.now()))
    
    def __handle_bye_response(self) -> None:
        # BYE response
        print("[{}] ---> __readline() BYE response received.".format(datetime.now()))
        # TODO: Implement reconnect
        self.__wait_for_response = "BYE"

    def __handle_exists_response(self, response: bytes) -> None:
        # EXISTS response
        print("[{}] ---> __readline() EXISTS response received.".format(datetime.now()))
        #self.done()
        #self.idle()
        self.__wait_for_response = "EXISTS"
    
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
        Returns folder name by its flag name.
        This method is useful when the client's folder name is in a different language.
        For example, if the client's inbox's name is "Gelen Kutusu" this method will return
        "INBOX" if the flag name is b'\\Inbox' or "Çöp Kutusu" if the flag name is b'\\Trash'
        """
        if flag_name not in FOLDER_FLAG_NAMES:
            return None

        status, folders_as_bytes = self.list()
        if status == "OK":
            for folder_as_bytes in folders_as_bytes:
                if flag_name == folder_as_bytes:
                    return folder_as_bytes
        return None

    def __encode_folder(self, folder: str) -> bytes:
        return ('"' + folder + '"').encode("utf-8")

    def __decode_folder(self, folder: bytes) -> str:
        # Most of the servers return folder name as b'(\\HasNoChildren) "/" "INBOX"'
        # But some servers like yandex return folder name as b'(\\HasNoChildren) "|" "INBOX"'
        # So we're replacing "|" with "/" to make it consistent
        return folder.decode().replace(' "|" ', ' "/" ').split(' "/" ')[1].replace('"', '')

    def select(self, mailbox: str = "INBOX", readonly: bool = False) -> tuple[str, list[bytes | None]]:
        if self.__current_folder[0] != mailbox or self.__current_folder[1] != readonly:
            self.__current_folder = (mailbox, readonly)
            return self.__imap.select(self.__encode_folder(mailbox), readonly)
        return "OK", [None]

    @__handle_conn
    def get_capabilities(self) -> list:
        """
        Retrieve a list of all email folders.

        Returns:
            list: List of folder names in the email account
        """
        return self.capability()

    @__handle_conn
    def get_folders(self) -> list:
        """
        Retrieve a list of all email folders.

        Returns:
            list: List of folder names in the email account
        """
        return [self.__decode_folder(i) for i in self.list()[1] if i.find(b'\\NoSelect') == -1]

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
            raise Exception("Folder should be selected before fetching flags")

        flags = self.uid('FETCH', uid, '(FLAGS)')[1][0]
        if flags:
            flags = flags.decode()
            flags = re.findall(r'\\([a-zA-Z]+)', flags)
        return flags or []

    def __build_search_criteria_query(self, search_criteria: SearchCriteria) -> str:
        """
            Preparing to convert search_json to search_criteria string:
            https://datatracker.ietf.org/doc/html/rfc9051#name-search-command
        """

        def recursive_or_query(criteria: str, search_keys: List[str]) -> str:
            """
            Example:
            recursive_or_query("FROM", ["johndoe@mail.com", "janedoe@mail.com", "person@mail.com"])
            Return:
            'OR (FROM "johndoe@mail.com") (OR (FROM "janedoe@mail.com") (FROM "person@mail.com"))'
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
        search: str | SearchCriteria = "ALL",
        offset: int = 0
    ) -> dict:
        """
        Retrieve emails from a specified folder based on search criteria.

        Args:
            folder (str, optional): Folder to search in. Defaults to "inbox".
            search (str | SearchCriteria, optional): Search criteria. Defaults to "ALL".
            offset (int, optional): Starting index for email retrieval. Defaults to 0.

        Returns:
            dict: Dictionary of emails matching the search criteria
        """
        self.select(folder, readonly=True)

        search_criteria_query = ''
        must_have_attachment = False
        if isinstance(search, SearchCriteria):
            must_have_attachment = search.has_attachments
            search_criteria_query = self.__build_search_criteria_query(search) or 'ALL'
        else:
            search_criteria_query = search or 'ALL'

        _, uids = self.uid('search', None, search_criteria_query.encode("utf-8") if search_criteria_query else 'ALL')
        uids = uids[0].split()[::-1]

        if len(uids) == 0:
            return {"folder": folder, "emails": [], "total": 0}

        emails = []
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

            emails.append({
                "uid": uid.decode(),
                "from": message["From"],
                "to": message["To"] if "To" in message else "",
                "subject": message["Subject"],
                "body_short": truncate_text(body, BODY_SHORT_THRESHOLD),
                "date": convert_date_to_iso(message["Date"]),
                "flags": self.get_email_flags(uid) or []
            })

        return {"folder": folder, "emails": emails, "total": len(uids)}

    @__handle_conn
    def get_email_content(
        self,
        uid: str,
        folder: str = INBOX
    ) -> dict: # TODO: Make a custom type
        """
        Retrieve full content of a specific email.

        Args:
            uid (str): Unique identifier of the email
            folder (str, optional): Folder containing the email. Defaults to "inbox".

        Returns:
            dict: Detailed email content
        """
        self.select(folder, readonly=True)

        _, message = self.uid('fetch', uid, '(RFC822)')
        message = email.message_from_bytes(message[0][1], policy=email.policy.default)

        body, attachments = "", []
        for part in (message.walk() if message.is_multipart() else [message]):
            content_type = part.get_content_type()
            file_name = part.get_filename()
            if file_name:
                attachments.append({
                    "cid": part.get("X-Attachment-Id"),
                    "name": file_name,
                    "data": base64.b64encode(
                        part.get_payload(decode=True)
                    ).decode("utf-8", errors="ignore"),
                    "size": make_size_human_readable(len(part.get_payload(decode=True))),
                    "type": content_type
                })
            elif content_type == "text/html" or (content_type == "text/plain" and not body):
                body = part.get_payload(decode=True)
                if body:
                    body = body.decode(part.get_content_charset())

        if attachments:
            for match in CID_RE_COMPILE.finditer(body):
                cid = match.group(1)
                for attachment in attachments:
                    if cid in attachment["name"] or cid in attachment["cid"]:
                        body = body.replace(
                            f'cid:{cid}',
                            f'data:{attachment["type"]};base64,{attachment["data"]}'
                        )

        # TODO: Look into this
        if "Seen" not in self.get_email_flags(uid):
            self.mark_email(uid, "seen", folder)

        return {
            "uid": uid,
            "from": message["From"],
            "to": message["To"] if "To" in message else "",
            "subject": message["Subject"],
            "body": body,
            "date": convert_date_to_iso(message["Date"]),
            "flags": self.get_email_flags(uid) or [],
            "attachments": attachments
        }

    @__handle_conn
    def mark_email(
        self,
        uid: str,
        mark: str,
        folder: str = INBOX
    ) -> bool:
        """
        Mark an email with a specific flag.

        Args:
            uid (str): Unique identifier of the email
            mark (str): Flag to apply to the email
            folder (str, optional): Folder containing the email. Defaults to "inbox".

        Returns:
            bool: True if email marked successfully, False otherwise
        """
        self.select(folder)

        mark = mark.lower()
        # TODO: Look into this
        mark_type = "-" if mark[0] + mark[1] == "un" else "+"
        mark = mark[2:] if mark_type == "-" else mark
        command = mark_type + "FLAGS"

        if mark not in MARK_MAP:
            raise ValueError(f"Invalid mark: {mark}")

        self.__imap.uid('STORE', uid, command, MARK_MAP[mark])
        self.__imap.expunge()
        return True

    @__handle_conn
    def move_email(self, uid: str, source_folder: str, destination_folder: str) -> bool:
        """
        Move an email from one folder to another.

        Args:
            uid (str): Unique identifier of the email
            source_folder (str): Current folder of the email
            destination_folder (str): Target folder to move the email to

        Returns:
            bool: True if email moved successfully, False otherwise
        """
        self.select(source_folder)
        self.__imap.uid('MOVE', uid, self.__encode_folder(destination_folder))
        self.__imap.expunge()
        return True

    @__handle_conn
    def copy_email(self, uid: str, source_folder: str, destination_folder: str) -> bool:
        """
        Create a copy of an email in another folder.

        Args:
            uid (str): Unique identifier of the email
            source_folder (str): Current folder of the email
            destination_folder (str): Target folder to copy the email to

        Returns:
            bool: True if email copied successfully, False otherwise
        """
        self.select(source_folder)
        self.__imap.uid('COPY', uid, self.__encode_folder(destination_folder))
        self.__imap.expunge()
        return True

    @__handle_conn
    def delete_email(self, uid: str, folder: str) -> bool:
        """
        Delete an email from a specific folder.

        Args:
            uid (str): Unique identifier of the email
            folder (str): Folder containing the email

        Returns:
            bool: True if email deleted successfully, False otherwise
        """
        trash_mailbox_name = self.__decode_folder(
            self.get_folder_name_by_flag_name(b"\\Trash")
        )

        if folder != trash_mailbox_name:
            self.move_email(uid, folder, trash_mailbox_name)

        self.select(trash_mailbox_name)
        self.__imap.uid('STORE', uid, '+FLAGS', '\\Deleted')
        self.__imap.expunge()
        return True

    @__handle_conn
    def create_folder(self, folder_name: str, parent_folder: str | None = None) -> bool:
        """
        Create a new email folder.

        Args:
            folder_name (str): Name of the new folder
            parent_folder (str, optional): Parent folder for nested folder creation. 
                                           Defaults to None.

        Returns:
            bool: True if folder created successfully, False otherwise
        """
        if parent_folder:
            folder_name = f"{parent_folder}/{folder_name}"
        return self.__imap.create(self.__encode_folder(folder_name))

    @__handle_conn
    def delete_folder(self, folder_name: str) -> bool:
        """
        Delete an existing email folder.

        Args:
            folder_name (str): Name of the folder to delete

        Returns:
            bool: True if folder deleted successfully, False otherwise
        """
        return self.__imap.delete(self.__encode_folder(folder_name))

    @__handle_conn
    def move_folder(self, folder_name: str, destination_folder: str) -> bool:
        """
        Move a folder to a new location.

        Args:
            folder_name (str): Name of the folder to move
            destination_folder (str): Target location for the folder

        Returns:
            bool: True if folder moved successfully, False otherwise
        """
        if "/" in folder_name:
            destination_folder = f"{destination_folder}/{folder_name.split("/")[-1]}"
        return self.__imap.rename(
            self.__encode_folder(folder_name),
            self.__encode_folder(destination_folder)
        )

    @__handle_conn
    def rename_folder(self, folder_name: str, new_folder_name: str) -> bool:
        """
        Rename an existing email folder.

        Args:
            folder_name (str): Current name of the folder
            new_folder_name (str): New name for the folder

        Returns:
            bool: True if folder renamed successfully, False otherwise
        """
        if "/" in folder_name:
            new_folder_name = folder_name.replace(
                folder_name.split("/")[-1],
                new_folder_name
            )

        return self.__imap.rename(
            self.__encode_folder(folder_name),
            self.__encode_folder(new_folder_name)
        )
