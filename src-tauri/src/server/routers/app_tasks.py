import json
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from ..internal.file_system import FileSystem

from ..types import Response, Preferences
from ..utils import err_msg

router = APIRouter(tags=["App"])


@router.get("/get-preferences")
def get_preferences() -> Response:
    try:
        return Response(
            success=True,
            message="Preferences loaded.",
            data=json.loads(FileSystem().get_preferences().read()),
        )
    except Exception as e:
        return Response(
            success=False,
            message=err_msg("There was an error while updating preferences.", str(e)),
        )


@router.put("/save-preferences")
def save_preferences(request: Preferences) -> Response:
    try:
        preferences_file = FileSystem().get_preferences()
        preferences = json.loads(preferences_file.read())
        preferences.update(request.model_dump())
        preferences_file.write(json.dumps(preferences, indent=4))
        return Response(success=True, message="Preferences saved.")
    except Exception as e:
        return Response(
            success=False,
            message=err_msg("There was an error while updating preferences.", str(e)),
        )


@router.patch("/reset-preferences")
def reset_preferences() -> Response:
    try:
        preferences_file = FileSystem().get_preferences()
        preferences_file.write(json.dumps(Preferences().dict(), indent=4))
        return Response(success=True, message="Preferences reset to default.")
    except Exception as e:
        return Response(
            success=False,
            message=err_msg("There was an error while updating preferences.", str(e)),
        )


__all__ = ["router"]
