from typing import List, Optional

class SearchCriteria():
    senders: Optional[List[str]] = []
    receivers: Optional[List[str]] = []
    subject: Optional[str] = ""
    since: Optional[str] = ""
    before: Optional[str] = ""
    flags: Optional[List[str]] = []
    include: Optional[str] = ""
    exclude: Optional[str] = ""
    has_attachments: Optional[bool] = False

class LoginException(Exception):
    pass
