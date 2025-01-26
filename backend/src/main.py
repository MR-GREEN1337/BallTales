from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.router import router as chat_router
from src.api.user.router import router as user_router

app = FastAPI(description="BallTales Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/api/v1")
app.include_router(user_router, prefix="/api/v1")


@app.get("/")
async def greet():
    return {"hello": "there"}
