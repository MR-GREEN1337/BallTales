from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import pandas as pd

from src.api.views import agent
from src.api.views.onboarding.router import router as onboarding_agent

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(agent.router, prefix="/api/v1")
app.include_router(onboarding_agent, prefix="/api/v1")


@app.get("/")
async def greet():
    return {"heelo": "there"}