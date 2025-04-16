from fastapi import APIRouter

from ..main import Response
from ..utils import err_msg

router = APIRouter(
    tags=["App"]
)

@router.patch("/save-preferences")
def save_preferences() -> Response:
    try:
        return Response(success=True)
    except Exception as e:
        return Response(success=False, message=err_msg("There was an error while updating preferences.", str(e)))

@router.patch("/reset-preferences")
def reset_preferences() -> Response:
    try:
        return Response(success=True)
    except Exception as e:
        return Response(success=False, message=err_msg("There was an error while updating preferences.", str(e)))

__all__ = ["router"]
