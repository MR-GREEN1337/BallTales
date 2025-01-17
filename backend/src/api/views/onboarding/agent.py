import asyncio
from typing import TypedDict, List, Optional, Dict, Any, Literal
from dataclasses import dataclass
import json
from httpx import AsyncClient
import google.generativeai as genai
import logfire
from src.core.settings import settings

@dataclass
class MLBDeps:
    client: AsyncClient
    season: int = 2025
    endpoints: Dict[str, Any] = None

class EntityDict(TypedDict, total=False):
    team: Optional[str]
    player: Optional[str]
    date: Optional[str]
    season: Optional[int]
    game_id: Optional[str]

class IntentAnalysis(TypedDict):
    primary_intent: Literal['team_info', 'player_info', 'game_info', 'stats', 
                          'standings', 'schedule', 'highlights']
    entities: EntityDict
    time_context: Literal['recent', 'historical', 'upcoming', 'current', 'season']
    data_requirements: List[str]

class APIStep(TypedDict):
    id: str
    endpoint: str
    parameters: Dict[str, Any]
    depends_on: List[str]
    required_for: List[str]

class DataRetrievalPlan(TypedDict):
    steps: List[APIStep]
    dependencies: Dict[str, List[str]]

class Stats(TypedDict, total=False):
    batting: Optional[Dict[str, Any]]
    pitching: Optional[Dict[str, Any]]
    fielding: Optional[Dict[str, Any]]
    team: Optional[Dict[str, Any]]

class MediaContent(TypedDict, total=False):
    type: str
    url: Optional[str]
    thumbnail: Optional[str]
    description: Optional[str]

class ResponseData(TypedDict):
    summary: str
    details: Dict[str, Any]
    stats: Optional[Stats]
    media: Optional[MediaContent]

class Action(TypedDict):
    type: str
    label: str
    data: Dict[str, Any]

class MLBResponse(TypedDict):
    message: str  # Technical/data summary
    conversation: str  # Friendly AI response
    data_type: str
    data: Dict[str, Any]
    context: Dict[str, Any]
    suggestions: List[str]
    media: Optional[Dict[str, Any]]
    actions: List[Action]

class MLBAgent:
    def __init__(self, api_key: str, endpoints_json: str):
        logfire.configure(send_to_logfire='if-token-present')
        genai.configure(api_key=api_key)
        
        self.model = genai.GenerativeModel("gemini-1.5-pro-latest")
        self.endpoints = json.loads(endpoints_json)["endpoints"]
        
        self._setup_prompts()

    def _setup_prompts(self):
        '''Set up all prompts used by the agent'''
        self.intent_prompt = """You analyze MLB queries to determine intent and data needs.
            Return structured analysis with primary intent, entities, time context,
            and required data types. Ensure all fields match the schema exactly."""
            
        self.plan_prompt = f"""You create data retrieval plans using MLB API endpoints.
            Available endpoints: {self.endpoints}
            Return structured plan with ordered steps and dependencies.
            Each step must include all required fields."""
            
        self.response_prompt = """You create natural, informative responses from MLB data.
            Return structured response with summary, details, and optional stats and media.
            Follow the schema exactly for all fields."""
            
        self.suggestion_prompt = """Generate 3-5 natural follow-up suggestions for an MLB query.
            Suggestions should be relevant to the current context and encourage exploration.
            Return exactly as a JSON array of strings."""
            
        self.action_prompt = """Generate 1-3 clickable actions for an MLB query response.
            Actions should help users navigate to related content.
            Each action must have:
            - type: The action type (e.g., view_team, view_player)
            - label: User-friendly text
            - data: Required parameters with IDs
            Return as a JSON array of action objects."""
            
        self.conversation_prompt = """You are a friendly baseball-loving AI assistant.
            Generate a warm, conversational response to the user's query.
            Even if the query isn't baseball-related, respond in a helpful and engaging way,
            while gently steering the conversation back to baseball when appropriate.
            Keep responses concise but personable.
            
            Examples:
            Query: "I'm feeling sad today"
            Response: "I'm sorry to hear you're feeling down today. Sometimes watching a great baseball game can lift our spirits! Would you like me to share some exciting highlights from recent games?"
            
            Query: "What's the weather like?"
            Response: "While I can't check the weather, I can tell you it's always a perfect day for baseball! Would you like to know which games are scheduled today?" """
            
        self.conversation_prompt = """You are a friendly baseball-loving AI assistant. 
            Generate a warm, conversational response to the user's query.
            Even if the query isn't baseball-related, respond in a helpful and engaging way,
            while gently steering the conversation back to baseball when appropriate.
            Keep responses concise but personable.
            
            Examples:
            Query: "I'm feeling sad today"
            Response: "I'm sorry to hear you're feeling down today. Sometimes watching a great baseball game can lift our spirits - there's nothing quite like the excitement of a close game! Would you like me to show you some of today's most thrilling moments?"
            
            Query: "What's the weather like?"
            Response: "While I can't check the current weather, I can tell you it's always a perfect day for baseball! Would you like to know if there are any games scheduled today?"
            
            Return a string with your conversational response."""

    async def analyze_intent(self, query: str) -> IntentAnalysis:
        '''Get structured intent analysis'''
        try:
            result = await asyncio.to_thread(
                self.model.generate_content,
                f"{self.intent_prompt}\n\nAnalyze this MLB query: '{query}'",
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    response_schema={
                    "type": "object",
                    "properties": {
                        "primary_intent": {
                            "type": "string",
                            "enum": ["team_info", "player_info", "game_info", "stats", 
                                   "standings", "schedule", "highlights"]
                        },
                        "entities": {
                            "type": "object",
                            "properties": {
                                "team": {"type": "string"},
                                "player": {"type": "string"},
                                "date": {"type": "string"},
                                "season": {"type": "integer"},
                                "game_id": {"type": "string"}
                            }
                        },
                        "time_context": {
                            "type": "string",
                            "enum": ["recent", "historical", "upcoming", "current", "season"]
                        },
                        "data_requirements": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    },
                    "required": ["primary_intent", "entities", "time_context", "data_requirements"]
                }
            )
        )
            parsed_result = json.loads(result.text)
            print(f"Parsed intent result: {parsed_result}")  # Debug log
            return parsed_result
        except Exception as e:
            print(f"Error in analyze_intent: {str(e)}, Response: {result.text if hasattr(result, 'text') else 'No text'}")
            raise

    async def create_data_plan(self, intent: IntentAnalysis) -> DataRetrievalPlan:
        '''Get structured data retrieval plan'''
        try:
            result = await asyncio.to_thread(
                self.model.generate_content,
                f"""{self.plan_prompt}
                
                Create a data retrieval plan for this intent:
                {json.dumps(intent, indent=2)}""",
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema={
                    "type": "object",
                    "properties": {
                        "steps": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string"},
                                    "endpoint": {"type": "string"},
                                    "parameters": {"type": "object", "properties": {"param": {"type": "string"}}},
                                    "depends_on": {"type": "array", "items": {"type": "string"}},
                                    "required_for": {"type": "array", "items": {"type": "string"}}
                                },
                                "required": ["id", "endpoint", "parameters"]
                            }
                        },
                        "dependencies": {
                            "type": "object",
                            "properties": {
                                "step_dependencies": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                }
                            }
                        }
                    },
                    "required": ["steps"]
                }
            )
        )
            parsed_result = json.loads(result.text)
            print(f"Parsed plan result: {parsed_result}")  # Debug log
            
            # Ensure dependencies are properly initialized
            if 'steps' in parsed_result:
                for step in parsed_result['steps']:
                    if 'depends_on' not in step:
                        step['depends_on'] = []
                    if 'required_for' not in step:
                        step['required_for'] = []
                        
            return parsed_result
        except Exception as e:
            print(f"Error in create_data_plan: {str(e)}, Response: {result.text if hasattr(result, 'text') else 'No text'}")
            raise

    async def execute_plan(self, deps: MLBDeps, plan: DataRetrievalPlan) -> Dict[str, Any]:
        '''Execute the retrieval plan'''
        if not plan.get('steps'):
            return {}
        results = {}
        dependency_levels = {}
        visited = set()
        
        def get_dependency_level(step: APIStep) -> int:
            if step['id'] in visited:
                return dependency_levels[step['id']]
            
            if not step.get('depends_on'):
                level = 0
            else:
                max_dep_level = 0
                for dep_id in step['depends_on']:
                    dep_step = next((s for s in plan['steps'] if s['id'] == dep_id), None)
                    if dep_step:
                        dep_level = get_dependency_level(dep_step)
                        max_dep_level = max(max_dep_level, dep_level)
                level = 1 + max_dep_level
            
            visited.add(step['id'])
            dependency_levels[step['id']] = level
            return level

        # First, calculate dependency levels for all steps
        step_levels: Dict[int, List[APIStep]] = {}
        for step in plan['steps']:
            level = get_dependency_level(step)
            if level not in step_levels:
                step_levels[level] = []
            step_levels[level].append(step)
        
        # Execute steps level by level
        for level in sorted(step_levels.keys()):
            level_steps = step_levels[level]
            level_results = await asyncio.gather(*[
                self._execute_step(deps, step, results) 
                for step in level_steps
            ])
            
            for step, result in zip(level_steps, level_results):
                if result is not None:
                    results[step['id']] = result
                    
        return results

    async def _execute_step(
        self, 
        deps: MLBDeps, 
        step: APIStep,
        prior_results: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        '''Execute a single API step'''
        endpoint = self.endpoints.get(step['endpoint'])
        print(endpoint)
        if not endpoint:
            print(f"Warning: Endpoint {step['endpoint']} not found")
            return None
            
        url = endpoint['endpoint']['url']
        print(url, "hhh")
        params = {}
        
        # Process parameters, resolving any references
        for param, value in step['parameters'].items():
            if isinstance(value, str) and value.startswith('$'):
                # Handle reference to previous results
                ref_parts = value[1:].split('.')
                ref_data = prior_results
                for part in ref_parts:
                    if isinstance(ref_data, dict):
                        ref_data = ref_data.get(part, {})
                    else:
                        print(f"Warning: Cannot resolve reference {value} - invalid path")
                        ref_data = {}
                params[param] = ref_data
            else:
                params[param] = value

        try:
            print(f"Executing request to {url} with params: {params}")  # Debug log
            response = await deps.client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error executing step {step['id']}: {str(e)}")
            return None

    async def format_response(
        self, 
        query: str, 
        intent: IntentAnalysis, 
        data: Dict[str, Any]
    ) -> ResponseData:
        """Get structured response content"""
        try:
            result = await asyncio.to_thread(
                self.model.generate_content,
                f"""{self.response_prompt}
            
            Query: "{query}"
            
            Data:
            {json.dumps(data, indent=2)}
            
            Intent:
            {json.dumps(intent, indent=2)}""",
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema={
                    "type": "object",
                    "properties": {
                        "summary": {"type": "string"},
                        "details": {"type": "object"},
                        "stats": {
                            "type": "object",
                            "properties": {
                                "batting": {"type": "object"},
                                "pitching": {"type": "object"},
                                "fielding": {"type": "object"},
                                "team": {"type": "object"}
                            }
                        },
                        "media": {
                            "type": "object",
                            "properties": {
                                "type": {"type": "string"},
                                "url": {"type": "string"},
                                "thumbnail": {"type": "string"},
                                "description": {"type": "string"}
                            }
                        }
                    },
                    "required": ["summary", "details"]
                }
            )
        )
            parsed_result = json.loads(result.text)
            print(f"Parsed response result: {parsed_result}")  # Debug log
            return parsed_result
        except Exception as e:
            print(f"Error in format_response: {str(e)}, Response: {result.text if hasattr(result, 'text') else 'No text'}")
            raise

    async def generate_conversation(
        self,
        message: str,
        intent: Optional[IntentAnalysis] = None,
        response_data: Optional[ResponseData] = None
    ) -> str:
        """Generate a friendly conversational response"""
        try:
            context = ""
            if intent and response_data:
                context = f"""
                Intent: {json.dumps(intent, indent=2)}
                Data response: {json.dumps(response_data, indent=2)}
                """
            
            result = await asyncio.to_thread(
                self.model.generate_content,
                f"""{self.conversation_prompt}
                
                User query: "{message}"
                {context}
                
                Generate a friendly response:""",
                generation_config=genai.GenerationConfig(
                    response_mime_type="text/plain"
                )
            )
            return result.text.strip()
        except Exception as e:
            print(f"Error generating conversation: {str(e)}")
            return "I'd be happy to talk baseball with you! What would you like to know about the game?"
    
    async def _generate_suggestions(
        self, 
        intent: IntentAnalysis, 
        response: ResponseData
    ) -> List[str]:
        """Generate contextual suggestions using LLM"""
        result = await asyncio.to_thread(
            self.model.generate_content,
            f"""{self.suggestion_prompt}
            
            Current intent:
            {json.dumps(intent, indent=2)}
            
            Current response:
            {json.dumps(response, indent=2)}""",
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema={
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 3,
                    "maxItems": 5
                }
            )
        )
        return json.loads(result.text)

    async def _generate_actions(
        self,
        intent: IntentAnalysis,
        response: ResponseData
    ) -> List[Action]:
        '''Generate available actions using LLM'''
        result = await asyncio.to_thread(
            self.model.generate_content,
            f"""{self.action_prompt}
            
            Current intent:
            {json.dumps(intent, indent=2)}
            
            Current response:
            {json.dumps(response, indent=2)}""",
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema={
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string"},
                            "label": {"type": "string"},
                            "data": {"type": "object"}
                        },
                        "required": ["type", "label", "data"]
                    },
                    "minItems": 1,
                    "maxItems": 3
                }
            )
        )
        return json.loads(result.text)

    async def process_message(self, deps: MLBDeps, message: str) -> MLBResponse:
        """Process message with typed responses at each step"""
        try:
            # 1. Get typed intent analysis
            intent: IntentAnalysis = await self.analyze_intent(message)
            
            # 2. Get typed retrieval plan
            plan: DataRetrievalPlan = await self.create_data_plan(intent)
            
            # 3. Execute plan
            data: Dict[str, Any] = await self.execute_plan(deps, plan)
            
            # 4. Get typed response content
            response_data: ResponseData = await self.format_response(message, intent, data)
            
            # 5. Generate suggestions and actions using LLM
            suggestions = await self._generate_suggestions(intent, response_data)
            actions = await self._generate_actions(intent, response_data)
            
            # 6. Generate conversational response
            conversation = await self.generate_conversation(message, intent, response_data)
            
            # 7. Return MLBResponse
            return {
                "message": response_data['summary'],
                "conversation": conversation,
                "data_type": intent['primary_intent'],
                "data": response_data['details'],
                "context": {"intent": intent},
                "suggestions": suggestions,
                "media": response_data.get('media'),
                "actions": actions
            }
            
        except Exception as e:
            # Generate a friendly error response
            error_conversation = await self.generate_conversation(
                message, 
                {"primary_intent": "unknown", "entities": {}, "time_context": "current", "data_requirements": []}
            )
            
            return {
                "message": f"I encountered an error: {str(e)}",
                "conversation": error_conversation,
                "data_type": "error",
                "data": {},
                "suggestions": [
                    "Try asking about a specific team",
                    "Search for a player",
                    "View today's games"
                ],
                "media": None,
                "actions": []
            }

# Create agent instance
with open('src/core/constants/mlb_api_responses.json', 'r') as f:
    endpoints_json = f.read()

mlb_agent = MLBAgent(api_key=settings.GEMINI_API_KEY, endpoints_json=endpoints_json)