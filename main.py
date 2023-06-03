from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from API.routes.api_routes import api_router

import sys


app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "*",
    "https://matissue.onrender.com",
    # 필요한 출처를 추가하십시오.
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")
