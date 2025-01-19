import asyncio
from datetime import datetime
import difflib
import enum
import os
import tempfile
import typing_extensions as typing
from typing import TypedDict, List, Optional, Dict, Any, Literal
from dataclasses import dataclass
import json
from httpx import AsyncClient
import google.generativeai as genai
from src.api.views.onboarding.repl import MLBPythonREPL
from src.core.settings import settings

@dataclass
class MLBDeps:
    client: AsyncClient
    season: int = 2025
    endpoints: Dict[str, Any] = None

class MLBResponse(TypedDict):
    message: str  # Technical/data summary
    conversation: str  # Friendly AI response
    data_type: str
    data: Dict[str, Any]
    context: Dict[str, Any]
    suggestions: List[str]
    media: Optional[Dict[str, Any]]

class IntentType(enum.Enum):
    TEAM_INFO = "team_info"
    PLAYER_INFO = "player_info"
    GAME_INFO = "game_info"
    STATS = "stats"
    STANDINGS = "standings"
    SCHEDULE = "schedule"
    HIGHLIGHTS = "highlights"
    CONVERSATION = "conversation"

class Specificity(enum.Enum):
    GENERAL = "general"
    SPECIFIC = "specific"
    COMPARATIVE = "comparative"
    ANALYTICAL = "analytical"

class Timeframe(enum.Enum):
    HISTORICAL = "historical"
    CURRENT = "current"
    UPCOMING = "upcoming"
    SEASON = "season"
    CAREER = "career"

class Complexity(enum.Enum):
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"

class StatFocus(enum.Enum):
    NONE = "none"
    OFFENSIVE = "offensive"
    DEFENSIVE = "defensive"
    BOTH = "both"

class Sentiment(enum.Enum):
    NEUTRAL = "neutral"
    POSITIVE = "positive"
    NEGATIVE = "negative"

# TypedDict definitions
class IntentDetails(TypedDict):
    type: IntentType
    description: str
    specificity: Specificity
    timeframe: Timeframe
    complexity: Complexity

class Entities(TypedDict):
    teams: List[str]
    players: List[str]
    dates: List[str]
    stats: List[str]
    locations: List[str]
    events: List[str]

class Context(TypedDict):
    time_frame: Timeframe
    stat_focus: StatFocus
    sentiment: Sentiment
    requires_data: bool
    follow_up: bool
    data_requirements: List[str]

class IntentAnalysis(TypedDict):
    intent: IntentDetails
    entities: Entities
    context: Context
    is_mlb_related: bool

# Data Plan Enums
class PlanType(enum.Enum):
    ENDPOINT = "endpoint"
    FUNCTION = "function"

class StepType(enum.Enum):
    ENDPOINT = "endpoint"
    FUNCTION = "function"

# Data Plan TypedDicts
class ParameterSource(typing.TypedDict):
    value: dict
    source_step: str
    source_path: str
    transform: str

class ExtractConfig(typing.TypedDict):
    fields: dict[str, str]
    filter: str

class PlanStep(typing.TypedDict):
    id: str
    type: StepType
    name: str
    description: str
    parameters: dict[str, ParameterSource]
    extract: ExtractConfig
    depends_on: list[str]
    required_for: list[str]

class FallbackPlan(typing.TypedDict):
    enabled: bool
    strategy: str
    steps: list[PlanStep]

class DataRetrievalPlan(typing.TypedDict):
    plan_type: PlanType
    steps: list[PlanStep]
    fallback: FallbackPlan

class MLBAgent:
    def __init__(self, api_key: str, endpoints_json: str, functions_json: str):
        genai.configure(api_key=api_key)
        
        self.model = genai.GenerativeModel("gemini-1.5-flash")
        self.code_model = genai.GenerativeModel("gemini-1.5-pro")
        self.endpoints = json.loads(endpoints_json)["endpoints"]
        self.functions = json.loads(functions_json)["functions"]
        self.intent = None;
        self.plan = None;
        self.state: Dict[str, Any] = {}
        self.repl = MLBPythonREPL(timeout=8)
        
        self._setup_prompts()

    def _setup_prompts(self):
        '''Set up all prompts used by the agent'''
        self.intent_prompt = """Please analyze the baseball query and return a structured JSON response with detailed intent analysis, and if mlb related.

        Query to analyze: """
            
        self.plan_prompt=f"""Create a detailed MLB data retrieval plan optimizing for accuracy and efficiency.

KNOWN CONTEXT (Use these values directly - DO NOT create steps to fetch them):
- Current Season (seasonId): 2025
- Current Year: 2025
- Regular Season Status: In Progress
- League IDs: AL=103, NL=104

Available MLB Stats API Functions:
{json.dumps(self.functions, indent=2)}

Available Endpoints:
{json.dumps(self.endpoints, indent=2)}

Current Intent Analysis:
{json.dumps(self.intent, indent=2)}

Current Date: {datetime.now().isoformat()}

Planning Guidelines:

1. Data Flow Architecture:
   - Design steps that build logically on each other
   - Ensure each step's output feeds into subsequent steps
   - Handle data dependencies explicitly
   - Consider parallel execution where possible

2. Resource Optimization:
   - Use provided context values (seasonId, year, etc.) directly - DO NOT create steps to fetch them
   - Prioritize functions over endpoints for efficiency
   - Batch related queries when possible
   - Minimize redundant data fetches
   - Consider data caching opportunities
   - Never create a step to fetch data that's provided in the known context

3. Data Transformation:
   - Plan necessary data cleaning steps
   - Identify required calculations
   - Handle missing data scenarios
   - Consider aggregation needs

4. Error Handling:
   - Include fallback strategies
   - Handle partial data scenarios
   - Plan for rate limiting
   - Consider timeout scenarios

5. Parameter Resolution:
   - Resolve all required parameters
   - Handle dynamic parameter generation
   - Validate parameter types
   - Consider parameter dependencies

Your plan must follow this exact schema:
{{
    "plan_type": "string",        # Must be one of: "endpoint", "function"
    "steps": [
        {{
            "id": "string",       # Unique step identifier
            "type": "string",     # Must be either "endpoint" or "function"
            "name": "string",     # Valid endpoint/function name from available endpoints/functions
            "description": "string", # Purpose of this step
            "parameters": {{
                "param_name": {{   # Parameter name matches API/function spec
                    "source_step": "string?",  # Optional reference to prior step
                    "source_path": "string?",  # Optional JSON path to value
                    "value": "any"            # Direct value if not from prior step
                }}
            }},
            "extract": {{
                "fields": {{        # Mapping of target fields to source paths
                    "field_name": "json.path"
                }},
                "filter": "string?" # Optional filter condition
            }},
            "depends_on": ["string"] # Array of step IDs this depends on
        }}
    ],
    "fallback": {{
        "enabled": true,         # Whether fallback is enabled
        "strategy": "string",    # Description of fallback strategy
        "steps": []             # Same structure as primary steps
    }}
}}

Focus on:
1. Logical data flow
2. Efficient resource use
3. Error handling
4. Data transformation
5. Parameter resolution"""
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
            """Enhanced intent analysis with structured schema"""
            try:
                result = await asyncio.to_thread(
                    self.model.generate_content,
                    f"{self.intent_prompt}\n{query}",
                    generation_config=genai.GenerationConfig(
                        response_mime_type='application/json',
                        response_schema=IntentAnalysis
                    )
                )

                parsed_result = json.loads(result.text)
                print(parsed_result)
                # Convert enum strings to enum values
                parsed_result["intent"]["type"] = IntentType(parsed_result["intent"]["type"])
                parsed_result["intent"]["specificity"] = Specificity(parsed_result["intent"]["specificity"])
                parsed_result["intent"]["timeframe"] = Timeframe(parsed_result["intent"]["timeframe"])
                parsed_result["intent"]["complexity"] = Complexity(parsed_result["intent"]["complexity"])
                
                parsed_result["context"]["time_frame"] = Timeframe(parsed_result["context"]["time_frame"])
                parsed_result["context"]["stat_focus"] = StatFocus(parsed_result["context"]["stat_focus"])
                parsed_result["context"]["sentiment"] = Sentiment(parsed_result["context"]["sentiment"])

                # Validate and clean entities
                entities = parsed_result.get("entities", {})
                for key in entities:
                    if not isinstance(entities[key], list):
                        entities[key] = [entities[key]] if entities[key] else []

                return parsed_result

            except Exception as e:
                print(f"Error in analyze_intent: {str(e)}")
                # Return default fallback intent
                return {
                    "mlb_query": False,
                    "intent": {
                        "type": IntentType.CONVERSATION,
                        "description": "General conversation",
                        "specificity": Specificity.GENERAL,
                        "timeframe": Timeframe.CURRENT,
                        "complexity": Complexity.SIMPLE
                    },
                    "entities": {
                        "teams": [], "players": [], "dates": [],
                        "stats": [], "locations": [], "events": []
                    },
                    "context": {
                        "time_frame": Timeframe.CURRENT,
                        "stat_focus": StatFocus.NONE,
                        "sentiment": Sentiment.NEUTRAL,
                        "requires_data": False,
                        "follow_up": False,
                        "data_requirements": []
                    }
                }

    def _create_error_response(self, message: str, error: str) -> MLBResponse:
        """Create a graceful error response"""
        return {
            "message": "I encountered an issue processing your request.",
            "conversation": "I apologize, but I ran into a technical issue. Could you try rephrasing your question?",
            "data_type": "error",
            "data": {"error": error},
            "context": {},
            "suggestions": [
                "Try asking about today's games",
                "Look up a specific player",
                "Check team standings"
            ],
            "media": None
        }

    def _create_fallback_response(self, message: str, intent: IntentAnalysis) -> MLBResponse:
        """Create a response when MLB data processing fails"""
        return {
            "message": "I couldn't retrieve the specific baseball data you requested.",
            "conversation": "I understand you're asking about baseball, but I'm having trouble getting that specific information. Could you try asking in a different way?",
            "data_type": intent.get('intent', {}).get('type', 'general').value,
            "data": {},
            "context": {"intent": intent},
            "suggestions": [
                "Try a simpler query",
                "Ask about basic stats",
                "Look up general team info"
            ],
            "media": None
        }
    async def create_data_plan(self, intent: IntentAnalysis) -> DataRetrievalPlan:
        """Generate structured data retrieval plan with improved schema validation"""
        try:
            # Compile available resources
            available_endpoints = list(self.endpoints.keys())
            available_functions = [f["name"] for f in self.functions]

            # Define valid types and methods statically
            valid_types = {
                "endpoint": True,
                "function": True
            }
            
            valid_methods = {
                method: True for method in available_endpoints
            }
            valid_methods.update({
                method: True for method in available_functions
            })
            
            plan_types = {
                "endpoint": True,
                "function": True,
            }

            # Define response schema
            response_schema = {
            "type": "object",
            "properties": {
                "plan_type": {
                    "type": "string"
                },
                "steps": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "type": {
                                "type": "string"
                            },
                            "name": {"type": "string"},
                            "description": {"type": "string"},
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "source_step": {"type": "string"},
                                    "source_path": {"type": "string"},
                                    "filter": {"type": "string"},
                                    "value": {
                                        "type": "string"
                                    }
                                }
                            },
                            "extract": {
                                "type": "object",
                                "properties": {
                                    "fields": {
                                        "type": "object",
                                        "properties": {
                                            "player_ids": {"type": "string"},
                                            "names": {"type": "string"},
                                            "stats": {"type": "string"},
                                            "info": {"type": "string"},
                                            "team_ids": {"type": "string"},
                                            "game_ids": {"type": "string"},
                                            "dates": {"type": "string"},
                                            "scores": {"type": "string"}
                                        },
                                    },
                                    "filter": {"type": "string"}
                                },
                                "required": ["fields"]
                            },
                            "depends_on": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "required_for": {
                                "type": "array",
                                "items": {"type": "string"}
                            }
                        },
                        "required": ["id", "type", "name", "description", "parameters", "extract", "depends_on"]
                    }
                },
"fallback": {
                    "type": "object",
                    "properties": {
                        "enabled": {"type": "boolean"},
                        "strategy": {"type": "string"},
                        "steps": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string"},
                                    "endpoint": {"type": "string"},
                                    "parameters": {
                                        "type": "object",
                                        "properties": {
                                            "source_step": {"type": "string"},
                                            "source_path": {"type": "string"},
                                            "filter": {"type": "string"}
                                        }
                                    },
                                    "extract": {
                                        "type": "object",
                                        "properties": {
                                            "fields": {
                                                "type": "object",
                                                "properties": {
                                                    "player_ids": {"type": "string"},
                                                    "names": {"type": "string"},
                                                    "stats": {"type": "string"},
                                                    "info": {"type": "string"}
                                                }
                                            },
                                            "filter": {"type": "string"}
                                        },
                                        "required": ["fields"]
                                    },
                                    "depends_on": {
                                        "type": "array",
                                        "items": {"type": "string"}
                                    }
                                },
                                "required": ["id", "endpoint", "parameters", "extract", "depends_on"]
                            }
                        }
                    },
                    "required": ["enabled", "strategy", "steps"]
                },
                "dependencies": {
                    "type": "object",
                    "properties": {
                        "step1": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "step2": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    }
                }
            },
            "required": ["plan_type", "steps", "fallback", "dependencies"]
        }
    
            # Define available methods statically to avoid list concatenation
            valid_methods = {
                method: True for method in available_endpoints
            }
            valid_methods.update({
                method: True for method in available_functions
            })

            # Generate plan using LLM
            result = await asyncio.to_thread(
                self.model.generate_content,
                self.plan_prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.2,
                    response_mime_type="application/json",
                    response_schema=response_schema
                )
            )

            parsed_result = json.loads(result.text)
            print(parsed_result)
            # Validate plan type
            if parsed_result["plan_type"] not in plan_types:
                raise ValueError(f"Invalid plan type: {parsed_result['plan_type']}")
            
            # Process steps
            for step in parsed_result["steps"]:
                if step["type"] not in valid_types:
                    raise ValueError(f"Invalid step type: {step['type']}")
                if step["name"] not in valid_methods:
                    raise ValueError(f"Invalid step name: {step['name']}")
                
            # Process fallback steps
            if parsed_result["fallback"]["steps"]:
                for step in parsed_result["fallback"]["steps"]:
                    if step["type"] not in valid_types:
                        raise ValueError(f"Invalid fallback step type: {step['type']}")
                    if step["name"] not in valid_methods:
                        raise ValueError(f"Invalid fallback step name: {step['name']}")
                    
            # Validate dependencies
            step_ids = {step["id"]: True for step in parsed_result["steps"]}
            for step_deps in parsed_result["dependencies"].values():
                for dep_id in step_deps:
                    if dep_id not in step_ids:
                        raise ValueError(f"Invalid dependency ID: {dep_id}")
            
            return parsed_result
            
        except Exception as e:
            print(f"Error in create_data_plan: {str(e)}")
            # Return simplified fallback plan
            return self._create_fallback_plan(intent)

    async def execute_plan(self, deps: MLBDeps, plan: DataRetrievalPlan) -> Dict[str, Any]:
        '''Execute the retrieval plan with data filtering and extraction'''
        results = {}
        
        for step in plan['steps']:
            # Execute current step
            print(step)
            raw_result = await self._execute_step(deps, step, results)
            #print(f"State at {step["id"]} is {self.state}")
            if not raw_result:
                continue
                
            # Apply extraction and filtering if specified
            if 'extract' in step:
                filtered_result = self._extract_and_filter(
                    raw_result,
                    step['extract'].get('source_path'),
                    step['extract'].get('filter')
                )
                results[step['id']] = filtered_result
            else:
                results[step['id']] = raw_result
                
        return results

    async def generate_processing_code(
        self,
        endpoint_name: str,
        schema: Dict[str, Any],
        plan
    ) -> str:
        """Generate Python code to process endpoint data based on schema and intent"""
        current_step = [step for step in plan["steps"] if step["endpoint"] == endpoint_name]
        
        prompt = f"""Write a Python function named process_data that processes MLB API data.
        The function should handle null/empty data gracefully.
        
        Process this endpoint: {endpoint_name}
        Schema: {json.dumps(schema, indent=2)}
        Step: {json.dumps(current_step, indent=2)}
        
        Return properly indented Python code that handles the data processing.
        Include error handling and return a dictionary with processed data.
        """

        result = await asyncio.to_thread(
            self.code_model.generate_content,
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="text/plain",
                candidate_count=1
            )
        )
        
        # Default processing code with proper indentation
        default_code = '''def process_data(data):
    if not data:
        return {}
        
    try:
        # Basic data validation
        if isinstance(data, dict):
            return data
        elif isinstance(data, list) and data:
            return data[0] if len(data) == 1 else data
        else:
            return {}
            
    except Exception as e:
        print(f"Error processing data: {str(e)}")
        return {}
'''

        try:
            generated_code = result.text.strip()
            generated_code = generated_code.replace('```python', '').replace('```', '')
            
            # Validate the generated code has proper function definition and indentation
            if not generated_code.startswith('def process_data(data):'):
                return default_code
            
            # Basic validation of code structure
            lines = generated_code.split('\n')
            if len(lines) < 2 or not any(line.strip().startswith('return') for line in lines):
                return default_code
            
            return generated_code
            
        except Exception as e:
            print(f"Error in code generation: {str(e)}")
            return default_code

    async def _execute_step(
        self, 
        deps: MLBDeps, 
        step: Dict[str, Any],
        prior_results: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Execute step based on method type (function or endpoint)"""
        try:
            # Resolve basic parameters
            method_type = step.get('type', '')
            params = step.get('parameters', {})
            print(method_type)
            print(params)
            # Execute based on method type
            if method_type == "function":
                result = await self._execute_function_step(deps, step, prior_results)
                self.state |= step | (result if isinstance(result, dict) else {})
                return result
            elif method_type == "endpoint":
                result = await self._execute_endpoint_step(deps, step, prior_results)
                self.state |= step | (result if isinstance(result, dict) else {})
                return result
            else:
                print(f"Unknown method type: {method_type}")
                return None
        except Exception as e:
            print(f"Error executing step {step.get('stepNumber')}: {str(e)}")
            
            # Try fallback if specified
            if step.get('fallback'):
                try:
                    print(f"Attempting fallback for step {step.get('stepNumber')}")
                    return await self._execute_fallback(deps, step, prior_results)
                except Exception as fallback_error:
                    print(f"Fallback failed: {str(fallback_error)}")
                    
            return None

    async def _execute_function_step(
        self,
        deps: MLBDeps, 
        step: Dict[str, Any],
        prior_results: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Execute MLB stats function"""
        try:
            # Get function name from parameters
            function_name = step['name'] #.get('function')
            if not function_name or function_name.lower() == 'none':
                # Handle custom processing functions
                return await self._execute_custom_processing(step, prior_results)
            #print("lj", function_name)
            # Find function info
            function_info = next((f for f in self.functions if f['name'] == function_name), None)
            if not function_info:
                raise ValueError(f"Invalid function: {function_name}")

            # Prepare function parameters
            resolved_params = self._resolve_parameters(step['parameters'], prior_results)
            
            # Generate function execution code
            execution_code = f"""
    import statsapi

    try:
        result = statsapi.{function_name}({resolved_params["value"]})
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({{"error": str(e)}}))
    """

            print(execution_code)
            # Execute function using REPL
            repl_result = await self.repl(code=execution_code)
            print("repl result:", repl_result)
            
            if repl_result.get('status') == 'error':
                raise RuntimeError(f"Function execution failed: {repl_result.get('error')}")
                
            # Process result
            try:
                output = repl_result.get('output')
                if not output:
                    raise ValueError("No output from function execution")
                    
                result = json.loads(output)
                if isinstance(result, dict) and "error" in result:
                    raise RuntimeError(f"Function error: {result['error']}")
                
                #TODO: If result is large than a threshold, continue, but if less, route to LLM to extract params for next steps
                # Process data extraction if specified
                if step.get('extract').get("filter"):
                    result = await self._apply_filtering(result, step['extract'])
                    
                    
                # Apply filtering if specified
                if step.get('extract'):
                    result = await self._process_extraction(result, step['extract'])
                
                return result
                
            except json.JSONDecodeError as e:
                raise ValueError(f"Failed to parse function result: {repl_result}")
                
        except Exception as e:
            print(f"Function execution error: {str(e)}")
            return None

    async def _execute_endpoint_step(
        self,
        deps: MLBDeps,
        step: Dict[str, Any],
        prior_results: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Execute MLB API endpoint"""
        try:
            # Get endpoint from parameters
            endpoint_name = step['parameters'].get('endpoint')
            if not endpoint_name:
                raise ValueError("No endpoint specified")
                
            # Get endpoint info
            endpoint_info = self.endpoints.get(endpoint_name)
            if not endpoint_info:
                raise ValueError(f"Invalid endpoint: {endpoint_name}")

            # Resolve parameters
            resolved_params = await self._resolve_parameters(step['parameters'], prior_results)
            
            # Get formatted URL
            request_info = await self.get_formatted_url(
                endpoint_name,
                endpoint_info,
                resolved_params,
                prior_results
            )
            
            if not request_info or 'url' not in request_info:
                raise ValueError("Failed to format URL")

            # Make request
            response = await deps.client.get(request_info['url'])
            response.raise_for_status()
            result = response.json()
            
            # Process data extraction if specified
            if step.get('dataExtraction'):
                result = await self._process_extraction(result, step['dataExtraction'])
                
            # Apply filtering if specified
            if step.get('filtering') and step['filtering'].lower() != 'none':
                result = await self._apply_filtering(result, step['filtering'])
                
            return result
            
        except Exception as e:
            print(f"Endpoint execution error: {str(e)}")
            return None

    async def _execute_custom_processing(
        self,
        step: Dict[str, Any],
        prior_results: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Execute custom data processing step"""
        try:
            # Generate processing code based on step description and parameters
            processing_code = await self._generate_processing_code(
                step['description'],
                step['parameters'],
   
             prior_results
            )
            
            # Prepare data for processing
            process_data = {
                'prior_results': prior_results,
                'parameters': step['parameters']
            }
            
            # Execute processing
            with tempfile.TemporaryDirectory() as temp_dir:
                data_file = os.path.join(temp_dir, 'process_data.json')
                with open(data_file, 'w') as f:
                    json.dump(process_data, f)
                    
                execution_code = f"""
    import json

    {processing_code}

    try:
        with open('{data_file}', 'r') as f:
            data = json.load(f)
        
        result = process_data(data['prior_results'], data['parameters'])
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({{"error": str(e)}}))
    """

                repl_result = await self.repl(code=execution_code)
                
                if repl_result.get('status') == 'error':
                    raise RuntimeError(f"Processing failed: {repl_result.get('error')}")
                    
                try:
                    output = repl_result.get('output')
                    if not output:
                        raise ValueError("No output from processing")
                        
                    result = json.loads(output)
                    if isinstance(result, dict) and "error" in result:
                        raise RuntimeError(f"Processing error: {result['error']}")
                        
                    return result
                    
                except json.JSONDecodeError as e:
                    raise ValueError(f"Failed to parse processing result: {repl_result}")
                    
        except Exception as e:
            print(f"Custom processing error: {str(e)}")
            return None

    async def _process_extraction(
        self, 
        data: Any, 
        extraction_info: str,
        size_threshold: int = 500_000  # Default threshold in characters, chosen hazardly
    ) -> Any:
        """Process data extraction based on extraction info and data size"""
        data_size = len(json.dumps(data)) if isinstance(data, (dict, list)) else len(str(data))
        print("data size", data_size)
        if data_size <= size_threshold:
            # For small data, use LLM directly
            prompt = f"""Given this data:
            {json.dumps(data) if isinstance(data, (dict, list)) else str(data)}
            
            Extract the following:
            {extraction_info}
            
            Return only the extracted data in valid JSON format.
            """
            
            try:
                result = await asyncio.to_thread(
                    self.code_model.generate_content,
                    prompt,
                    generation_config=genai.GenerationConfig(
                        response_mime_type='text/plain',
                    )
                )
                #print(result)
                dict_result = result.text.strip().replace('```json\n', '').replace('```', '').replace('\n', '')
                result = json.loads(dict_result)
                print("extracted result is: ", result)
                return result
            except (json.JSONDecodeError, Exception) as e:
                print(f"Direct extraction error: {str(e)}")
                return data
        else:
            # For large data, use REPL approach
            prompt = f"""Generate Python code to extract data according to this specification:
            
            Data structure:
            {json.dumps(data)[:10000] if isinstance(data, (dict, list)) else str(data)[:10000]}
            
            Extraction needed:
            {extraction_info}
            
            Return a Python function named extract_data that takes the data as input and returns the extracted result.
            """
            
            try:
                result = await asyncio.to_thread(
                    self.code_model.generate_content,
                    prompt,
                    generation_config=genai.GenerationConfig(
                        response_mime_type='text/plain'
                    )
                )
                
                extraction_code = result.text.strip().replace('```python', '').replace('```', '')
                
                with tempfile.TemporaryDirectory() as temp_dir:
                    data_file = os.path.join(temp_dir, 'data.json')
                    with open(data_file, 'w') as f:
                        json.dump(data, f)
                        
                    execution_code = f"""
    import json

    {extraction_code}

    try:
        with open('{data_file}', 'r') as f:
            data = json.load(f)
        
        result = extract_data(data)
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({{"error": str(e)}}))
    """
                    repl_result = await self.repl(code=execution_code)
                    
                    if repl_result.get('status') == 'error':
                        raise RuntimeError(f"Extraction failed: {repl_result.get('error')}")
                        
                    try:
                        output = repl_result.get('output')
                        if not output:
                            raise ValueError("No output from extraction")
                            
                        result = json.loads(output)
                        if isinstance(result, dict) and "error" in result:
                            raise RuntimeError(f"Extraction error: {result['error']}")
                            
                        return result
                        
                    except json.JSONDecodeError:
                        return data
                        
            except Exception as e:
                print(f"Extraction error: {str(e)}")
                return data

    async def _apply_filtering(
        self, 
        data: Any, 
        filtering_info: str,
        size_threshold: int = 10000  # Default threshold in characters
    ) -> Any:
        """Apply filtering based on filtering info and data size"""
        if not filtering_info or filtering_info.lower() == 'none':
            return data
            
        data_size = len(json.dumps(data)) if isinstance(data, (dict, list)) else len(str(data))
        
        if data_size <= size_threshold:
            # For small data, use LLM directly
            prompt = f"""Given this data:
            {json.dumps(data) if isinstance(data, (dict, list)) else str(data)}
            
            Apply this filtering:
            {filtering_info}
            
            Return only the filtered data in valid JSON format."""
            
            try:
                result = await asyncio.to_thread(
                    self.code_model.generate_content,
                    prompt,
                    generation_config=genai.GenerationConfig(
                        response_mime_type='text/plain'
                    )
                )
                return json.loads(result.text.strip())
            except (json.JSONDecodeError, Exception) as e:
                print(f"Direct filtering error: {str(e)}")
                return data
        else:
            # For large data, use REPL approach
            prompt = f"""Generate Python code to filter data according to this specification:
            
            Data structure:
            {json.dumps(data)[:1000] if isinstance(data, (dict, list)) else str(data)[:1000]}
            
            Filtering needed:
            {filtering_info}
            
            Return a Python function named filter_data that takes the data as input and returns the filtered result.
            """
            
            try:
                result = await asyncio.to_thread(
                    self.code_model.generate_content,
                    prompt,
                    generation_config=genai.GenerationConfig(
                        response_mime_type='text/plain'
                    )
                )
                
                filtering_code = result.text.strip().replace('```python', '').replace('```', '')
                
                with tempfile.TemporaryDirectory() as temp_dir:
                    data_file = os.path.join(temp_dir, 'data.json')
                    with open(data_file, 'w') as f:
                        json.dump(data, f)
                        
                    execution_code = f"""
    import json

    {filtering_code}

    try:
        with open('{data_file}', 'r') as f:
            data = json.load(f)
            
        result = filter_data(data)
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({{"error": str(e)}}))
    """

                    repl_result = await self.repl(code=execution_code)
                    
                    if repl_result.get('status') == 'error':
                        raise RuntimeError(f"Filtering failed: {repl_result.get('error')}")
                        
                    try:
                        output = repl_result.get('output')
                        if not output:
                            raise ValueError("No output from filtering")
                            
                        result = json.loads(output)
                        if isinstance(result, dict) and "error" in result:
                            raise RuntimeError(f"Filtering error: {result['error']}")
                            
                        return result
                        
                    except json.JSONDecodeError:
                        return data
                        
            except Exception as e:
                print(f"Filtering error: {str(e)}")
                return data
    async def get_formatted_url(
        self,
        endpoint_name: str,
        endpoint_info: Dict[str, Any],
        parameters: Dict[str, Any],
        prior_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        print(endpoint_info)
        """Get formatted URL and parameters directly from LLM"""
        prompt = f"""Given this MLB API endpoint and data, return the formatted URL and parameters.

        Endpoint: {endpoint_name}
        Base URL: {endpoint_info['endpoint']['url']}
        Paramteres: {parameters}
        Prior Results: {json.dumps(prior_results)}

        Return ONLY a JSON object with exactly one field:
        1. 'url': the complete formatted URL with path parameters filled in

        Example:
        {{
            "url": "https://url",
        }}
        """

        result = await asyncio.to_thread(
            self.model.generate_content,
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json"
            )
        )
        #print(result.text)
        return json.loads(result.text)

    def _analyze_response_schema(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze and extract schema from API response with improved type handling"""
        schema = {}
        
        def get_type(value: Any) -> str:
            if isinstance(value, bool):
                return 'boolean'
            elif isinstance(value, int):
                return 'integer'
            elif isinstance(value, float):
                return 'number'
            elif isinstance(value, str):
                return 'string'
            elif isinstance(value, (list, tuple)):
                return 'array'
            elif isinstance(value, dict):
                return 'object'
            elif value is None:
                return 'null'
            else:
                return 'unknown'
        
        def extract_schema(obj: Any, current_schema: Dict[str, Any]):
            current_schema['type'] = get_type(obj)
            
            if isinstance(obj, dict):
                current_schema['properties'] = {}
                for key, value in obj.items():
                    current_schema['properties'][key] = {}
                    extract_schema(value, current_schema['properties'][key])
                    
            elif isinstance(obj, (list, tuple)) and obj:
                current_schema['items'] = {}
                # Get schema of first item as sample
                extract_schema(obj[0], current_schema['items'])
        
        extract_schema(data, schema)
        return schema

    async def _execute_processing_code(
        self,
        processing_code: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute generated processing code using the analysis tool"""
        
        # Prepare the code to execute
        execution_code = f"""
    import json
    {processing_code}

    # Input data
    data = {json.dumps(data)}

    # Execute processing function
    result = process_data(data)
    print(json.dumps(result))
    """
        print("hihoo", execution_code)

        # Use the analysis tool to execute the code
        result = await self.repl.execute(execution_code)
        
        # Parse and return the processed result
        try:
            return json.loads(result.output)
        except json.JSONDecodeError:
            print(f"Error parsing processing result: {result.output}")
            return data  # Return original data if processing fails

    def _resolve_parameters(
        self,
        parameters: Dict[str, Any],
        prior_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve API parameters, including references to prior results"""
        resolved = {}
        for param, value in parameters.items():
            if isinstance(value, str) and value.startswith('$'):
                ref_parts = value[1:].split('.')
                ref_data = prior_results
                for part in ref_parts:
                    if isinstance(ref_data, dict):
                        ref_data = ref_data.get(part, {})
                    else:
                        print(f"Warning: Cannot resolve reference {value}")
                        ref_data = {}
                resolved[param] = ref_data
            else:
                resolved[param] = value
        return resolved

    async def format_response(
        self, 
        query: str, 
        intent: IntentAnalysis, 
        data: Dict[str, Any]
    ) -> Any:
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
        response_data: Optional[Any] = None
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
        response: Any
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

    async def process_message(self, deps: MLBDeps, message: str) -> MLBResponse:
        """Process message with Gemini-powered error handling"""
        try:
            # Get intent analysis
            intent = await self.analyze_intent(message)
            
            # MLB-related query path
            if intent["is_mlb_related"] and intent.get("requires_data", True):
                try:
                    # Full MLB processing path
                    plan = await self.create_data_plan(intent)
                    self.state = plan
                    data = await self.execute_plan(deps, plan)
                    response_data = await self.format_response(message, intent, data)
                    suggestions = await self._generate_suggestions(intent, response_data)
                    conversation = await self.generate_conversation(message, intent, response_data)
                    
                    return {
                        "message": response_data['summary'],
                        "conversation": conversation,
                        "data_type": intent['primary_intent'],
                        "data": response_data['details'],
                        "context": {"intent": intent},
                        "suggestions": suggestions,
                        "media": response_data.get('media'),
                    }
                except Exception as execution_error:
                    print(f"Execution error: {str(execution_error)}")
                    
                    # Use Gemini to analyze error and generate helpful response
                    error_prompt = f"""You are an MLB query assistant handling an execution error.
                    Generate a helpful, baseball-focused response explaining the issue and suggesting alternatives.

                    User Query: {message}

                    Intent Analysis:
                    {json.dumps(intent, indent=2)}

                    Execution State:
                    {json.dumps(self.state, indent=2)}

                    Error: {str(execution_error)}

                    Return response as JSON with this structure:
                    {{
                        "message": "Technical summary of the issue",
                        "conversation": "Natural, baseball-focused response explaining the issue and offering alternatives",
                        "suggestions": ["3-5 relevant alternative queries based on the original intent and available state"]
                    }}"""

                    try:
                        error_response = await asyncio.to_thread(
                            self.model.generate_content,
                            error_prompt,
                            generation_config=genai.GenerationConfig(
                                temperature=0.2,
                                response_mime_type="application/json"
                            )
                        )
                        
                        parsed_error = json.loads(error_response.text)
                        print(error_response)
                        return {
                            "message": parsed_error['message'],
                            "conversation": parsed_error['conversation'],
                            "data_type": "error",
                            "data": {"error": str(execution_error), "state": self.state},
                            "context": {"intent": intent},
                            "suggestions": parsed_error['suggestions'],
                            "media": None
                        }
                    except Exception as gemini_error:
                        print(f"Failed to generate Gemini error response: {str(gemini_error)}")
                        # Fall back to basic error response
                        return self._create_error_response(message, str(execution_error))
            
            # Non-MLB or simple MLB conversation path  
            else:
                conversation = await self.generate_conversation(message, intent)
                suggestions = await self._generate_suggestions(intent, {})
                print(conversation)
                print(suggestions)
                return {
                    "message": intent.get("intent_description", "Let's talk baseball!"),
                    "conversation": conversation,
                    "data_type": "conversation",
                    "data": {},
                    "context": {"intent": intent},
                    "suggestions": suggestions,
                    "media": None,
                    "actions": []
                }

        except Exception as e:
            print(f"Critical error in process_message: {str(e)}")
            return self._create_error_response(message, str(e))

    def _extract_and_filter(
        self,
        data: Any,
        path: Optional[str],
        filter_condition: Optional[str]
    ) -> Any:
        '''Extract and filter data based on specified path and condition'''
        if not path:
            return data
            
        # Extract data using path
        result = data
        for key in path.split('.'):
            if '[' in key:  # Handle array access
                key, index = key.split('[')
                index = int(index.rstrip(']'))
                result = result[key][index]
            else:
                result = result.get(key, {})
                
        # Apply filter if specified
        if filter_condition and isinstance(result, list):
            try:
                # Create safe evaluation environment
                def evaluate_condition(item, condition):
                    return eval(
                        condition,
                        {"__builtins__": {}},
                        {"item": item}
                    )
                    
                result = [
                    item for item in result 
                    if evaluate_condition(item, filter_condition)
                ]
            except Exception as e:
                print(f"Filter evaluation failed: {str(e)}")
                
        return result

    async def _generate_processing_code(
        self,
        description: str,
        parameters: Dict[str, Any],
        prior_results: Dict[str, Any]
    ) -> str:
        """Generate Python code for custom data processing steps"""
        
        # Create prompt for code generation
        prompt = f"""Generate a Python function that processes MLB data according to this specification:
        
        Task Description: {description}
        
        Parameters: {json.dumps(parameters, indent=2)}
        
        Available Prior Results Keys: {list(prior_results.keys())}
        
        Requirements:
        1. Function name must be 'process_data'
        2. Takes two parameters: prior_results (dict) and parameters (dict)
        3. Must handle missing or invalid data gracefully
        4. Return processed data in JSON-serializable format
        5. Include error handling and logging
        
        Example structure:
        def process_data(prior_results: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
            try:
                # Processing logic here
                return processed_data
            except Exception as e:
                print(f"Processing error: {{str(e)}}")
                return {{"error": str(e)}}
        
        Generate ONLY the Python function code, no explanations or markdown."""
        
        try:
            # Get code from LLM
            result = await asyncio.to_thread(
                self.code_model.generate_content,
                prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type='text/plain',
                    temperature=0.2,  # Lower temperature for more focused code generation
                    candidate_count=1
                )
            )
            
            # Clean up generated code
            generated_code = result.text.strip()
            generated_code = generated_code.replace('```python', '').replace('```', '')
            
            # Validate basic structure
            if not generated_code.startswith('def process_data('):
                # Fall back to default processing function if generation fails
                return self._get_default_processing_code(description)
                
            # Add necessary imports
            imports = """
    import json
    from typing import Dict, Any, List, Union
    import statistics
    from datetime import datetime
    """
            
            return f"{imports}\n\n{generated_code}"
            
        except Exception as e:
            print(f"Error generating processing code: {str(e)}")
            return self._get_default_processing_code(description)
            
    def _get_default_processing_code(self, description: str) -> str:
        """Get default processing code template"""
        return """
    import json
    from typing import Dict, Any, List, Union

    def process_data(prior_results: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # Basic validation
            if not prior_results or not parameters:
                return {"error": "Missing required data"}
                
            processed_data = {}
            
            # Extract relevant data from prior results
            for key, value in prior_results.items():
                if isinstance(value, (dict, list)):
                    processed_data[key] = value
                    
            # Apply any specified transformations
            if parameters.get('transformations'):
                for transform in parameters['transformations']:
                    if transform == 'aggregate':
                        processed_data = self._aggregate_data(processed_data)
                    elif transform == 'sort':
                        processed_data = self._sort_data(processed_data, parameters.get('sort_key'))
                    elif transform == 'filter':
                        processed_data = self._filter_data(processed_data, parameters.get('filter_condition'))
                        
            return processed_data
            
        except Exception as e:
            print(f"Error in default processing: {str(e)}")
            return {"error": str(e)}
            
    def _aggregate_data(data: Dict[str, Any]) -> Dict[str, Any]:
        '''Basic data aggregation'''
        aggregated = {}
        for key, value in data.items():
            if isinstance(value, list):
                # Calculate basic statistics for numeric values
                numeric_values = [v for v in value if isinstance(v, (int, float))]
                if numeric_values:
                    aggregated[f"{key}_stats"] = {
                        "count": len(numeric_values),
                        "sum": sum(numeric_values),
                        "mean": statistics.mean(numeric_values),
                        "median": statistics.median(numeric_values)
                    }
        return aggregated
        
    def _sort_data(data: Dict[str, Any], sort_key: str = None) -> Dict[str, Any]:
        '''Basic data sorting'''
        sorted_data = {}
        for key, value in data.items():
            if isinstance(value, list):
                if sort_key and all(isinstance(item, dict) and sort_key in item for item in value):
                    sorted_data[key] = sorted(value, key=lambda x: x[sort_key])
                else:
                    sorted_data[key] = sorted(value)
            else:
                sorted_data[key] = value
        return sorted_data
        
    def _filter_data(data: Dict[str, Any], condition: str = None) -> Dict[str, Any]:
        '''Basic data filtering'''
        filtered_data = {}
        for key, value in data.items():
            if isinstance(value, list):
                if condition and all(isinstance(item, dict) for item in value):
                    filtered_data[key] = [
                        item for item in value 
                        if all(k in item for k in condition.split('=')[0].strip())
                    ]
                else:
                    filtered_data[key] = value
            else:
                filtered_data[key] = value
        return filtered_data
    """

# Create agent instance
with open('src/core/constants/endpoints.json', 'r') as f:
    endpoints_json = f.read()

with open('src/core/constants/mlb_functions.json', 'r') as f:
    functions_json = f.read()

mlb_agent = MLBAgent(api_key=settings.GEMINI_API_KEY, endpoints_json=endpoints_json, functions_json=functions_json)