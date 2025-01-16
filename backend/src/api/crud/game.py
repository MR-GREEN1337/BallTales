import pandas as pd
from typing import Dict
import httpx
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.gemini import GeminiModel

from src.core.settings import settings

class GameService:
    def __init__(self):
        self.base_url = "https://statsapi.mlb.com/api/v1.1"
        self.model = GeminiModel('gemini-1.5-flash', api_key=settings.GEMINI_API_KEY)
        self.agent = Agent(
            self.model,
            system_prompt=(
                'Analyze baseball game situations and provide strategic insights. '
                'Be concise and focus on key strategic elements and probabilities.'
            )
        )
        
    async def get_live_game(self, game_pk: str) -> Dict:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/game/{game_pk}/feed/live"
            )
            return response.json()
    
    @property
    def analyze_agent(self):
        return self.agent.tool(self.analyze_situation)
            
    async def analyze_situation(self, ctx: RunContext, game_state: Dict) -> str:
        """Analyze the current baseball game situation.
        
        Args:
            ctx: The run context
            game_state: Dictionary containing current game state information
        """
        prompt = f"""
        Analyze this baseball situation:
        - Inning: {game_state['inning']}
        - Outs: {game_state['outs']}
        - Runners: {game_state.get('runners', [])}
        
        Provide strategic insights and probabilities for the next play.
        """
        return await self.model.generate(prompt)

# Usage example:
async def main():
    service = GameService()
    game_data = await service.get_live_game("game_pk_here")
    analysis = await service.agent.run(game_data)
    print(analysis.data)