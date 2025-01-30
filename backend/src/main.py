from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger
from pathlib import Path

from src.api.router import router as chat_router
from src.api.user.router import router as user_router
from src.core.settings import settings
from src.api.agent import MLBAgent

# Global variables to store loaded JSON data
json_data = {
    "endpoints": None,
    "functions": None,
    "media": None,
    "charts": None
}

# Global MLB agent instance
mlb_agent = None

@asynccontextmanager
async def load_json_data(app: FastAPI):
    """
    Asynchronous context manager to load JSON data when the application starts.
    This ensures resources are properly loaded before handling any requests.
    """
    try:
        # Define the base path for JSON files
        base_path = Path("src/core/constants")
        
        # Load all JSON files
        with open(base_path / "endpoints.json", "r") as f:
            json_data["endpoints"] = f.read()
            
        with open(base_path / "mlb_functions.json", "r") as f:
            json_data["functions"] = f.read()
            
        with open(base_path / "media_sources.json", "r") as f:
            json_data["media"] = f.read()
            
        with open(base_path / "charts_docs.json", "r") as f:
            json_data["charts"] = f.read()
        
        logger.info(f"Loaded JSON data: successfully loaded all files")
        # Initialize MLB agent with loaded data
        global mlb_agent
        mlb_agent = MLBAgent(
            api_key=settings.GEMINI_API_KEY,
            endpoints_json=json_data["endpoints"],
            functions_json=json_data["functions"],
            media_json=json_data["media"],
            charts_json=json_data["charts"]
        )
        
        yield
    finally:
        # Clean up resources if needed
        json_data["endpoints"] = None
        json_data["functions"] = None
        json_data["media"] = None
        json_data["charts"] = None
        mlb_agent = None

# Create FastAPI app with lifespan handler
app = FastAPI(
    description="BallTales Backend",
    lifespan=load_json_data
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat_router, prefix="/api/v1")
app.include_router(user_router, prefix="/api/v1")

# Health check endpoint
@app.get("/")
async def health_check():
    """Health check endpoint to verify the application is running"""
    return {
        "status": "healthy",
        "message": "BallTales API is running"
    }

def get_mlb_agent() -> MLBAgent:
    """
    Get the global MLB agent instance.
    This function should be used by route handlers that need access to the MLB agent.
    """
    if mlb_agent is None:
        raise RuntimeError("MLB agent not initialized")
    return mlb_agent
