import asyncio
from typing import List, Optional, Dict, Any, Literal
from dataclasses import dataclass
import json
from datetime import datetime
from httpx import AsyncClient
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.gemini import GeminiModel

from src.api.views.onboarding.models import MLBResponse
from src.core.settings import settings
import logfire

@dataclass
class MLBDeps:
    client: AsyncClient
    season: int = 2025
    endpoints: Dict[str, Any] = None

class IntentAnalysis(BaseModel):
    """Structured analysis of user intent"""
    primary_intent: Literal[
        'team_info', 'player_info', 'game_info', 'stats', 
        'standings', 'schedule', 'highlights'
    ]
    entities: Dict[str, Any] = Field(..., description="Identified entities", example={
        "team": "Yankees",
        "player": "Aaron Judge",
        "date": "2025-04-01"
    })
    time_context: Optional[Literal['recent', 'historical', 'upcoming', 'current', 'season']] = 'current'
    data_requirements: List[str] = Field(..., description="Required data types", example=[
        "team_stats", "player_roster", "recent_games"
    ])

class APIStep(BaseModel):
    """Single API call in the data retrieval plan"""
    id: str
    endpoint: str
    parameters: Dict[str, Any]
    depends_on: Optional[List[str]] = None
    required_for: Optional[List[str]] = None

class DataRetrievalPlan(BaseModel):
    """Structured plan for API calls"""
    steps: List[APIStep]
    dependencies: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Map of step ID to dependent step IDs"
    )

class ResponseData(BaseModel):
    """Structured response content"""
    summary: str = Field(..., description="Natural language summary")
    details: Dict[str, Any] = Field(..., description="Detailed data")
    stats: Optional[Dict[str, Any]] = Field(None, description="Relevant statistics")
    media: Optional[Dict[str, Any]] = Field(None, description="Related media content")
    
class MLBAgent(Agent):
    def __init__(self, model: GeminiModel, endpoints_json: str):
        logfire.configure(send_to_logfire='if-token-present')
        self.intent_agent = Agent(
            model, 
            result_type=IntentAnalysis,
            system_prompt="""You analyze MLB queries to determine intent and data needs.
            Return structured IntentAnalysis with primary intent, entities, time context,
            and required data types."""
        )
        
        self.plan_agent = Agent(
            model,
            result_type=DataRetrievalPlan,
            system_prompt=f"""You create data retrieval plans using MLB API endpoints.
            Available endpoints: {endpoints_json}
            Return structured DataRetrievalPlan with ordered steps and dependencies."""
        )
        
        self.response_agent = Agent(
            model,
            result_type=ResponseData,
            system_prompt="""You create natural, informative responses from MLB data.
            Return structured ResponseData with summary, details, stats, and media."""
        )
        
        self.endpoints = json.loads(endpoints_json)

    async def analyze_intent(self, query: str) -> IntentAnalysis:
        """Get structured intent analysis"""
        result = await self.intent_agent.run(
            f"""Analyze this MLB query: "{query}"
            Identify the primary intent, entities mentioned, time context,
            and required data types."""
        )
        print(result)
        return result.data

    async def create_data_plan(self, intent: IntentAnalysis) -> DataRetrievalPlan:
        """Get structured data retrieval plan"""
        result = await self.plan_agent.run(
            f"""Create a data retrieval plan for this intent:
            {json.dumps(intent.dict(), indent=2)}
            
            Consider:
            1. Required endpoints to fulfill data needs
            2. Parameter values from entities
            3. Dependencies between calls
            4. Optimal ordering of requests"""
        )
        return result.data

    async def execute_plan(self, ctx: RunContext[MLBDeps], plan: DataRetrievalPlan) -> Dict[str, Any]:
        """Execute the retrieval plan"""
        results = {}
        
        # Group steps by dependency level
        dependency_levels: Dict[int, List[APIStep]] = {}
        visited = set()
        
        def get_dependency_level(step: APIStep) -> int:
            if step.id in visited:
                return dependency_levels[step.id]
            
            if not step.depends_on:
                level = 0
            else:
                level = 1 + max(
                    get_dependency_level(next(s for s in plan.steps if s.id == dep))
                    for dep in step.depends_on
                )
            
            visited.add(step.id)
            dependency_levels[step.id] = level
            return level
        
        # Calculate dependency levels for all steps
        for step in plan.steps:
            level = get_dependency_level(step)
            if level not in dependency_levels:
                dependency_levels[level] = []
            dependency_levels[level].append(step)
        
        # Execute steps level by level
        for level in sorted(dependency_levels.keys()):
            level_steps = dependency_levels[level]
            level_results = await asyncio.gather(*[
                self._execute_step(ctx, step, results) 
                for step in level_steps
            ])
            
            for step, result in zip(level_steps, level_results):
                if result is not None:
                    results[step.id] = result
                    
        return results

    async def _execute_step(
        self, 
        ctx: RunContext[MLBDeps], 
        step: APIStep,
        prior_results: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Execute a single API step"""
        endpoint = self.endpoints.get(step.endpoint)
        if not endpoint:
            return None
            
        # Build URL and parameters
        url = endpoint['url']
        
        # Interpolate URL parameters
        for param, value in step.parameters.items():
            if isinstance(value, str) and value.startswith('$'):
                # Reference to prior result
                ref_parts = value[1:].split('.')
                ref_data = prior_results
                for part in ref_parts:
                    ref_data = ref_data.get(part, {})
                step.parameters[param] = ref_data
                
        params = {
            param: step.parameters.get(param)
            for param in endpoint.get('required_params', [])
            if param in step.parameters
        }
        
        optional_params = {
            param: step.parameters.get(param)
            for param in endpoint.get('optional_params', [])
            if param in step.parameters
        }
        params.update(optional_params)
        
        try:
            response = await ctx.deps.client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error executing step {step.id}: {str(e)}")
            return None

    async def format_response(
        self, 
        query: str, 
        intent: IntentAnalysis, 
        data: Dict[str, Any]
    ) -> ResponseData:
        """Get structured response content"""
        result = await self.response_agent.run(
            f"""Create a response for query: "{query}"
            
            Using this data:
            {json.dumps(data, indent=2)}
            
            Based on this intent:
            {json.dumps(intent.dict(), indent=2)}
            
            Provide a natural summary and structure the data appropriately."""
        )
        return result.data

    async def process_message(self, ctx: RunContext[MLBDeps], message: str) -> MLBResponse:
        """Process message with typed responses at each step"""
        try:
            # 1. Get typed intent analysis
            intent: IntentAnalysis = await self.analyze_intent(message)
            print(intent)
            
            # 2. Get typed retrieval plan
            plan: DataRetrievalPlan = await self.create_data_plan(intent)
            
            # 3. Execute plan
            data: Dict[str, Any] = await self.execute_plan(ctx, plan)
            
            # 4. Get typed response content
            response_data: ResponseData = await self.format_response(message, intent, data)
            
            # 5. Convert to MLBResponse
            return MLBResponse(
                message=response_data.summary,
                data_type=intent.primary_intent,
                data=response_data.details,
                context={"intent": intent.dict()},
                suggestions=self._generate_suggestions(intent, response_data),
                media=response_data.media,
                actions=self._generate_actions(intent, response_data)
            )
            
        except Exception as e:
            return MLBResponse(
                message=f"I encountered an error: {str(e)}",
                data_type="error",
                data={},
                suggestions=["Try asking about a specific team", "Search for a player", "View today's games"]
            )

    def _generate_suggestions(
        self, 
        intent: IntentAnalysis, 
        response: ResponseData
    ) -> List[str]:
        """Generate contextual suggestions based on intent and response"""
        suggestions = []
        if intent.primary_intent == 'team_info':
            suggestions.extend([
                f"Show {intent.entities['team']} roster",
                f"Recent {intent.entities['team']} highlights",
                f"{intent.entities['team']} upcoming games"
            ])
        elif intent.primary_intent == 'player_info':
            suggestions.extend([
                f"Show {intent.entities['player']}'s career stats",
                f"{intent.entities['player']}'s recent highlights",
                "Compare with similar players"
            ])
        return suggestions

    def _generate_actions(
        self,
        intent: IntentAnalysis,
        response: ResponseData
    ) -> List[Dict[str, Any]]:
        """Generate available actions based on intent and response"""
        actions = []
        if 'team' in intent.entities:
            actions.append({
                "type": "view_team",
                "label": f"View {intent.entities['team']} Details",
                "data": {"team_id": response.details.get("team", {}).get("id")}
            })
        if 'player' in intent.entities:
            actions.append({
                "type": "view_player",
                "label": f"View {intent.entities['player']} Profile",
                "data": {"player_id": response.details.get("player", {}).get("id")}
            })
        return actions

# Create typed agent instance
with open('src/core/constants/endpoints.json', 'r') as f:
    endpoints_json = f.read()

mlb_agent = MLBAgent(
    GeminiModel('gemini-2.0-flash-exp', api_key=settings.GEMINI_API_KEY),
    endpoints_json=endpoints_json
)