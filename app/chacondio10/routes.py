from fastapi import APIRouter, Body, Path, Query, Request

from .protocol import transmit

__all__ = ["router"]

router = APIRouter(prefix="/chacondio10", tags=["chacondio10"])


@router.get("/{sender}/{button}", summary="Get button state")
async def get_button(request: Request, sender: int = Path(ge=0, le=67108863), button: int = Path(ge=0, le=15)) -> int:
    """Get the current state of a button for a given sender"""
    if sender in request.app.state.chacondio10 and button in request.app.state.chacondio10[sender]:
        return request.app.state.chacondio10[sender][button]
    else:
        return 0


@router.put("/{sender}/group", summary="Set group state", status_code=204)
async def put_group(request: Request, sender: int = Path(ge=0, le=67108863), onoff: int = Body(ge=0, le=1), repeat: int = Query(default=5, ge=1)) -> None:
    """Set the state of the entire group (all buttons) for a given sender"""
    if not sender in request.app.state.chacondio10:
        request.app.state.chacondio10[sender] = {}
    for button in range(16):
        request.app.state.chacondio10[sender][button] = onoff
    for _ in range(repeat):
        transmit(request.app.state.gpio, sender, True, 0, bool(onoff))


@router.put("/{sender}/{button}", summary="Set button state", status_code=204)
async def put_button(request: Request, sender: int = Path(ge=0, le=67108863), button: int = Path(ge=0, le=15), onoff: int = Body(ge=0, le=1), repeat: int = Query(default=5, ge=1)) -> None:
    """Set the state of a button for a given sender"""
    if not sender in request.app.state.chacondio10:
        request.app.state.chacondio10[sender] = {}
    request.app.state.chacondio10[sender][button] = onoff
    for _ in range(repeat):
        transmit(request.app.state.gpio, sender, False, button, bool(onoff))
