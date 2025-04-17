from typing import Generic, Optional, TypeVar
from pydantic import BaseModel

T = TypeVar("T")

class Response(BaseModel, Generic[T]):
    success: bool
    message: str
    data: Optional[T] = None

__all__ = ["Response"]
