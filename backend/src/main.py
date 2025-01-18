from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.views.onboarding.router import router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")

@app.get("/")
async def greet():
    return {"heelo": "there"}