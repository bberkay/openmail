import imaplib
from .utils import choose_positive, extract_domain, contains_non_ascii

class IMAP(imaplib.IMAP4_SSL):
    def __init__(self, email_address: str, password: str, port: int = 993, try_limit: int = 3, timeout: int = 30):
        self.__try_limit = choose_positive(try_limit, 3) # Number of times to try to connect to the server before giving up
        super().__init__(
            self.__find_imap_server(email_address),
            port or 993,
            timeout=choose_positive(timeout, 30)
        )
        self.login(email_address, password)

    def __find_imap_server(self, email_address: str) -> str:
        try:
            return {
                "gmail": "imap.gmail.com",
                "yahoo": "imap.mail.yahoo.com",
                "outlook": "outlook.office365.com",
                "hotmail": "outlook.office365.com"
            }[extract_domain(email_address)]
        except KeyError:
            raise Exception("Unsupported email domain")

    def is_logged_in(self) -> bool:
        return self.state == "AUTH"

    def login(self, email_address: str, password: str) -> None:
        try_count = self.__try_limit
        for _ in range(try_count):
            try:
                if not self.is_logged_in():
                    if contains_non_ascii(email_address) or contains_non_ascii(password):
                        self.authenticate("PLAIN", lambda x: bytes("\x00" + email_address + "\x00" + password, "utf-8"))
                    else:
                        super().login(email_address, password)
                    self._simple_command('ENABLE', 'UTF8=ACCEPT')
                break
            except Exception as e:
                try_count -= 1
                if try_count == 0:
                    raise Exception("Could not connect to the target imap server: {}".format(str(e)))

    def logout(self) -> None:
        try:
            if self.is_logged_in():
                super().logout()
        except Exception as e:
            raise Exception("Could not logout from the target imap server: {}".format(str(e)))
