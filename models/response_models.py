from pydantic import BaseModel


class LoginResponse(BaseModel):
    message: str
    sessionId: str


class LoginRequest(BaseModel):
    user_id: str
    password: str


class DeleteRequest(LoginRequest):
    sessionId: str


class LogoutRequest(BaseModel):
    sessionId: str


class MessageResponse(BaseModel):
    message: str


class ErrorResponse(BaseModel):
    detail: str
