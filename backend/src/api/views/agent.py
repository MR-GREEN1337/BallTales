from fastapi import APIRouter, HTTPException
import httpx
from ..models.schemas import GameState, GameAnalysis
from ..crud.game import GameService
from typing import Optional

router = APIRouter(
    prefix="/games",
    tags=["games"],
    responses={404: {"description": "Not found"}}
)
game_service = GameService()

@router.get("/live/{game_pk}",
    summary="Get Live Game Data",
    description="""
    Retrieves real-time GUMBO (Grand Unified Master Baseball Object) data for a specific game.
    
    The endpoint provides complete game information including:
    - Current game state
    - Play-by-play information
    - Player statistics
    - Team information
    - Scoring plays
    
    Parameters:
    - game_pk: Unique identifier for the MLB game
    """,
    response_description="Complete GUMBO data object for the specified game"
)
async def get_live_game(game_pk: str):
    try:
        return await game_service.get_live_game(game_pk)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze",
    summary="Analyze Game Situation",
    description="""
    Provides AI-powered analysis of the current game situation using Gemini.
    
    Returns:
    - Detailed situation analysis
    - Probability predictions for next plays
    - Strategic recommendations
    - Historical comparisons
    
    The analysis takes into account:
    - Current inning and score
    - Number of outs
    - Runner positions
    - Player matchups
    - Historical statistics
    """,
    response_description="Detailed analysis of the current game situation with predictions"
)
async def analyze_game(game_state: GameState) -> GameAnalysis:
    try:
        game_data = await game_service.get_live_game(game_state.game_pk)
        analysis = await game_service.analyze_situation(game_data)
        
        return GameAnalysis(
            situation=f"Inning: {game_state.inning}, Outs: {game_state.outs}",
            analysis=analysis,
            probability={"hit": 0.300, "out": 0.600, "walk": 0.100},
            suggested_strategies=["Pitch outside", "Defensive shift"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/schedule",
    summary="Get MLB Game Schedule",
    description="""
    Retrieves the MLB game schedule for a specified date.
    
    Features:
    - Returns all MLB games scheduled for the given date
    - Includes game status, teams, and venue information
    - Provides game_pk identifiers needed for live game data
    
    Parameters:
    - date (optional): Date in YYYY-MM-DD format. If not provided, returns today's schedule
    """,
    response_description="List of scheduled MLB games with detailed information"
)
async def get_schedule(date: Optional[str] = None):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://statsapi.mlb.com/api/v1/schedule",
                params={"sportId": 1, "date": date}
            )
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))