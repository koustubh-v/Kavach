"""WebSocket endpoint.

Primary: /api/v1/ws
Alias:   /ws
"""

from typing import Annotated

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.core.exceptions import UnauthorizedError
from app.database.session import SessionLocal
from app.repositories.user import UserRepository
from app.services.auth import AuthService
from app.websocket.manager import manager

router = APIRouter(prefix="/ws", tags=["websocket"])


@router.websocket("")
async def websocket_endpoint(
    websocket: WebSocket,
    token: Annotated[str | None, Query()] = None,
) -> None:
    """Authenticate a user before accepting real-time websocket updates."""
    if not token:
        await websocket.close(code=1008)
        return

    try:
        async with SessionLocal() as session:
            auth_service = AuthService(UserRepository(session))
            user = await auth_service.get_user_from_token(token)
    except UnauthorizedError:
        await websocket.close(code=1008)
        return

    if not user.is_active:
        await websocket.close(code=1008)
        return

    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and receive messages if needed
            data = await websocket.receive_text()
            # Echo back for testing
            await websocket.send_text(f"Message received: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
