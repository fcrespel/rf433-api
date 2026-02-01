from fastapi import APIRouter, Body, Path, Query, Request
from pydantic import BaseModel, Field

from .protocol import transmit

__all__ = ["router"]

router = APIRouter(prefix="/chacon54662", tags=["chacon54662"])


class PutStateRequest(BaseModel):
    word: str = Field(pattern='^[01]{24}$')
    state: int = Field(ge=0, le=1)
    repeat: int = Field(ge=1, default=3)


@router.get("/state/{stateKey}", summary="Get button state")
async def get_state(request: Request, stateKey: str = Path(pattern="[a-z0-9-]")) -> int:
    """Get the current state for a given stateKey"""
    if stateKey in request.app.state.chacon54662:
        return request.app.state.chacon54662[stateKey]
    else:
        return 0


@router.put("/state/{stateKey}", summary="Set button state and send 24-bit code word", status_code=204)
async def put_state(request: Request, stateKey: str = Path(pattern="[a-z0-9-]"), body: PutStateRequest = Body()) -> None:
    """Set the state for a given stateKey and send a 24-bit code word"""
    request.app.state.chacon54662[stateKey] = int(body.state)
    for _ in range(body.repeat):
        transmit(request.app.state.gpio, int(body.word, 2))


@router.put("/word", summary="Send 24-bit code word", status_code=204, deprecated=True)
async def put_word(request: Request, word: str = Body(pattern="[01]{24}"), repeat: int = Query(default=3, ge=1),
                   stateKey: str = Query(default=None, pattern="[a-z0-9-]"), stateValue: int = Query(default=None, ge=0, le=1)) -> None:
    """Send a 24-bit code word and optionally save state in a given stateKey"""
    if stateKey is not None and stateValue is not None:
        request.app.state.chacon54662[stateKey] = stateValue
    for _ in range(repeat):
        transmit(request.app.state.gpio, int(word, 2))
