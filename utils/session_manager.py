from fastapi import Depends, HTTPException, status, Header
from pydantic import BaseModel
from typing import Optional
import uuid
import redis
from .config import get_settings

settings = get_settings()

r = redis.Redis.from_url(settings.redis_url, decode_responses=True)


class Session(BaseModel):
    id: Optional[str] = Header(None)


class SessionManager:
    def create_session(self, data: str):
        session_id = str(uuid.uuid4())
        r.set(session_id, data)
        return session_id

    def get_session(self, session_id: str, expiration: int = 3600):
        data = r.get(session_id)
        if data is None:
            raise HTTPException(status_code=401, detail="Invalid session id")
        r.expire(session_id, expiration)
        return data

    def delete_session(self, session_id: str):
        r.delete(session_id)


def get_current_session(session: Session = Depends()) -> str:
    session_manager = SessionManager()
    current_user = session_manager.get_session(session.id)
    if current_user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid session ID",
        )
    return current_user


async def get_current_user(session: Session = Depends(), session_manager: SessionManager = Depends(SessionManager)):
    if session.id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesssion ID가 없습니다."
        )
    user_id = session_manager.get_session(session.id)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session ID",
        )
    return user_id
