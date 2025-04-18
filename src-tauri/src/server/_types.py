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
    En = "En"

    def __str__(self):
        return self.value


class Preferences(BaseModel):
    theme: Optional[Theme] = Theme.System
    language: Optional[Language] = Language.En
