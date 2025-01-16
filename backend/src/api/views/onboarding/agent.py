from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from typing import Any, List, Optional
from datetime import datetime

from httpx import AsyncClient
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.gemini import GeminiModel

from src.core.settings import settings

class TeamInfo(BaseModel):
    id: int
    name: str
    abbreviation: str
    teamName: str
    locationName: str
    league: dict
    division: dict

class PlayerInfo(BaseModel):
    id: int
    fullName: str
    primaryNumber: Optional[str]
    currentTeam: dict
    primaryPosition: dict
    stats: Optional[dict]

class GameInfo(BaseModel):
    gamePk: int
    gameDate: str
    teams: dict
    venue: dict
    status: dict

class HomeRunInfo(BaseModel):
    play_id: str
    title: str
    exit_velocity: float
    launch_angle: float
    distance: float
    video_url: str
    season: int

@dataclass
class MLBDeps:
    client: AsyncClient
    season: int = 2024

mlb_agent = Agent(
    GeminiModel('gemini-1.5-flash', api_key=settings.GEMINI_API_KEY),
    system_prompt=(
        'You are a baseball-savvy assistant. Analyze user messages for intent about teams, '
        'players, games, or highlights. Use appropriate tools to fetch relevant MLB data. '
        'Keep responses natural but informative. Focus on recent or historical stats based on context.'
    ),
    deps_type=MLBDeps,
    retries=2,
)

@mlb_agent.tool
async def get_team_info(
    ctx: RunContext[MLBDeps], team_name: str = None
) -> List[TeamInfo]:
    """Get information about MLB teams.
    
    Args:
        ctx: The context
        team_name: Optional team name to filter results
    
    Returns:
        List of team information including IDs, names, and divisions
    """
    url = 'https://statsapi.mlb.com/api/v1/teams?sportId=1'
    r = await ctx.deps.client.get(url)
    r.raise_for_status()
    data = r.json()
    
    teams = [TeamInfo(**team) for team in data['teams']]
    if team_name:
        teams = [t for t in teams if team_name.lower() in t.name.lower()]
    return teams

@mlb_agent.tool
async def get_player_info(
    ctx: RunContext[MLBDeps], player_id: int
) -> PlayerInfo:
    """Get detailed information about a specific player.
    
    Args:
        ctx: The context
        player_id: MLB player ID
    
    Returns:
        Player information including stats and current team
    """
    url = f'https://statsapi.mlb.com/api/v1/people/{player_id}?hydrate=stats(group=[batting,pitching],type=[yearByYear])'
    r = await ctx.deps.client.get(url)
    r.raise_for_status()
    data = r.json()
    return PlayerInfo(**data['people'][0])

@mlb_agent.tool
async def get_schedule(
    ctx: RunContext[MLBDeps], 
    start_date: str = None,
    team_id: int = None
) -> List[GameInfo]:
    """Get MLB game schedule information.
    
    Args:
        ctx: The context
        start_date: Optional date in YYYY-MM-DD format
        team_id: Optional team ID to filter games
    
    Returns:
        List of game information including teams and venues
    """
    params = {
        'sportId': 1,
        'season': ctx.deps.season,
    }
    if start_date:
        params['startDate'] = start_date
    if team_id:
        params['teamId'] = team_id
        
    url = 'https://statsapi.mlb.com/api/v1/schedule'
    r = await ctx.deps.client.get(url, params=params)
    r.raise_for_status()
    data = r.json()
    
    games = []
    for date in data['dates']:
        for game in date['games']:
            games.append(GameInfo(**game))
    return games

@mlb_agent.tool
async def get_home_runs(
    ctx: RunContext[MLBDeps],
    season: int = None,
    player_id: int = None
) -> List[HomeRunInfo]:
    """Get home run data and highlights.
    
    Args:
        ctx: The context
        season: Optional season year
        player_id: Optional player ID to filter home runs
    
    Returns:
        List of home run information including video links
    """
    season = season or ctx.deps.season
    base_url = 'https://storage.googleapis.com/gcp-mlb-hackathon-2025/datasets'
    
    # This would need to be adjusted based on actual data availability
    url = f'{base_url}/{season}-mlb-homeruns.csv'
    r = await ctx.deps.client.get(url)
    r.raise_for_status()
    
    # Process CSV data and filter by player if specified
    # This is a simplified example
    home_runs = []
    # Add processing logic here
    return home_runs

@mlb_agent.tool
async def get_player_image(
    ctx: RunContext[MLBDeps],
    player_id: int
) -> str:
    """Get player headshot image URL.
    
    Args:
        ctx: The context
        player_id: MLB player ID
    
    Returns:
        URL to player's headshot image
    """
    return f'https://securea.mlb.com/mlb/images/players/head_shot/{player_id}.jpg'

class MLBResponse(BaseModel):
    """Structure for frontend UI updates."""
    message: str
    data_type: str  # 'team', 'player', 'game', 'highlight'
    data: dict
    suggestions: List[str]
    media: Optional[dict] = None
    actions: List[dict]

async def main():
    async with AsyncClient() as client:
        deps = MLBDeps(client=client)
        
        # Example usage
        result = await mlb_agent.run(
            "Tell me about the Yankees and their recent games", 
            deps=deps
        )
        
        response = MLBResponse(
            message=result.data,
            data_type='team',
            data=result.context.get('team_data', {}),
            suggestions=[
                "Show me their roster",
                "Recent home runs",
                "Upcoming games"
            ],
            actions=[
                {"type": "view_roster", "team_id": 147},
                {"type": "view_schedule", "team_id": 147}
            ]
        )
        print(json.dumps(response.dict(), indent=2))

if __name__ == '__main__':
    asyncio.run(main())