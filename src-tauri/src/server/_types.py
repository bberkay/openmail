from __future__ import annotations
from enum import Enum
from typing import Generic, Optional, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class Response(BaseModel, Generic[T]):
    success: bool
    message: str
    data: Optional[T] = None


class Theme(str, Enum):
    System = "System"
    Light = "Light"
    Dark = "Dark"

    def __str__(self):
        return self.value


class Language(str, Enum):
    """
    The enum keys are derived from RFC 5646 language tags
    (e.g., "en", "en-US", "en-GB"),but are formatted using
    uppercase letters and underscores (e.g., EN_US).
    Reference: https://datatracker.ietf.org/doc/html/rfc5646
    """
    System = "System"
    EN = "English"
    EN_US = "English (US)"
    EN_GB = "English (GB)"

    def __str__(self):
        return self.value


class Preferences(BaseModel):
    theme: Theme = Theme.System
    language: Language = Language.System
    mailbox_length: int = 10
