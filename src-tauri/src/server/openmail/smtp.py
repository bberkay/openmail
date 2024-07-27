import smtplib
from .utils import choose_positive, extract_domain

class SMTP(smtplib.SMTP):
    def __init__(self, email_address: str, password: str, port: int = 587, try_limit: int = 3, timeout: int = 30):
        self.__try_limit = choose_positive(try_limit, 3) # Number of times to try to connect to the server before giving up
        self.__is_logged_in = False
        super().__init__(
            self.__find_smtp_server(email_address),
            port or 587,
            timeout=choose_positive(timeout, 30)
        )
        self.login(email_address, password)

    def __find_smtp_server(self, email_address: str) -> str:
        try:
            return {
                "gmail": "smtp.gmail.com",
                "yahoo": "smtp.mail.yahoo.com",
                "outlook": "smtp-mail.outlook.com",
                "hotmail": "smtp-mail.outlook.com"
            }[extract_domain(email_address)]
        except KeyError:
            raise Exception("Unsupported email domain")

    def is_logged_in(self) -> bool:
        """
        I couldn't find a way to check if the user is logged in like in the IMAP class.
        If you have better ideas, let me know please.
        """
        return self.__is_logged_in

    def login(self, email_address: str, password: str) -> None:
        try_count = self.__try_limit
        for _ in range(try_count):
            try:
                if not self.is_logged_in():
                    self.ehlo()
                    self.starttls()
                    self.ehlo()
                    super().login(email_address, password)
                    self.__is_logged_in = True
                break
            except Exception as e:
                self.__is_logged_in = False
                try_count -= 1
                if try_count == 0:
                    raise Exception("Could not connect to the target smtp server: {}".format(str(e)))

    def quit(self) -> None:
        try:
            if self.is_logged_in():
                super().quit()
        except Exception as e:
            raise Exception("Could not disconnect from the target smtp server: {}".format(str(e)))
