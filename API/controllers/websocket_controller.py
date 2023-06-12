from fastapi import WebSocket, Depends, APIRouter
import redis
import asyncio
import json
from utils.config import get_settings
from utils.session_manager import get_current_session

settings = get_settings()

redis_client = redis.Redis.from_url(settings.redis_url, decode_responses=True)
pubsub = redis_client.pubsub()
pubsub.subscribe("notifications")
router = APIRouter()

# WebSocket 연결 관리
active_connections = {}


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket, current_user: str = Depends(get_current_session)
):
    await websocket.accept()
    active_connections[current_user] = websocket

    # Redis로부터 알림 받기
    async def listen_for_notifications():
        for message in pubsub.listen():
            if message["type"] == "message":
                notification = json.loads(message["data"])
                target_user_id = notification["user_id"]
                if target_user_id in active_connections:
                    target_websocket = active_connections[target_user_id]
                    await target_websocket.send_text(notification["message"])

    # 별도의 스레드에서 Redis 알림 수신 시작
    asyncio.create_task(listen_for_notifications())

    # WebSocket 연결 유지
    try:
        while True:
            await websocket.receive_text()
    except:
        active_connections.pop(current_user)
