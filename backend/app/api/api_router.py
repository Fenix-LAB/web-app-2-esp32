from fastapi import APIRouter, status

from .routes import (
    recive_data,
    websocket,
)

router = APIRouter()

router.include_router(recive_data.router, tags=["recive_data"])
router.include_router(websocket.ws_router, tags=["websocket"])


