from fastapi import APIRouter

from ..types import Response
from ..utils import err_msg

router = APIRouter(
    tags=["App"]
)

@router.get("/get-preferences")
def get_preferences() -> Response:
    try:

        return Response(success=True, message="Preferences fetched.")
    except Exception as e:
        return Response(success=False, message=err_msg("There was an error while updating preferences.", str(e)))

@router.patch("/save-preferences")
def save_preferences() -> Response:
    try:
        return Response(success=True, message="Preferences saved.")
    except Exception as e:
        return Response(success=False, message=err_msg("There was an error while updating preferences.", str(e)))

@router.patch("/reset-preferences")
def reset_preferences() -> Response:
    try:
        return Response(success=True, message="Preferences reset to default.")
    except Exception as e:
        return Response(success=False, message=err_msg("There was an error while updating preferences.", str(e)))

__all__ = ["router"]
