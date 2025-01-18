import asyncio
import os
import tempfile
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
        genai.configure(api_key=api_key)
        
        self.model = genai.GenerativeModel("gemini-1.5-flash")
        self.code_model = genai.GenerativeModel("gemini-1.5-pro")
        self.endpoints = json.loads(endpoints_json)["endpoints"]
        self.intent = None;
        self.plan = None;

        self.repl = MLBPythonREPL(timeout=8)
        
        self._setup_prompts()

    def _setup_prompts(self):
        '''Set up all prompts used by the agent'''
        self.intent_prompt = """You analyze MLB queries to determine intent and data needs.
            Return structured analysis with primary intent, entities, time context,
            and required data types. Ensure all fields match the schema exactly."""
            
        self.plan_prompt = """You create data retrieval plans using MLB API endpoints.
            Available endpoints: {list(self.endpoints.keys())}
            
            IMPORTANT RULES FOR SEQUENTIAL DATA FLOW:
            1. First step MUST use an endpoint with NO required parameters (e.g., teams list, search)
            2. Each step must specify:
               - How to filter/extract data from previous step's response
               - Exact fields needed for next step's parameters
            3. Use this format for parameters:
               "parameters": {
                   "param_name": {
                       "source_step": "step_id",
                       "source_path": "path.to.field",
                       "filter_condition": "optional filter logic"
                   }
               }
            
            Example Plan for "Show me Aaron Judge's stats":
            {
                "steps": [
                    {
                        "id": "step1",
                        "endpoint": "player_search",
                        "parameters": {"name": "Aaron Judge"},
                        "extract": {
                            "player_id": "players[0].id",
                            "filter": "name === 'Judge, Aaron'"
                        }
                    },
                    {
                        "id": "step2", 
                        "endpoint": "person",
                        "parameters": {
                            "personId": {
                                "source_step": "step1",
                                "source_path": "player_id"
                            }
                        },
                        "depends_on": ["step1"]
                    }
                ]
            }"""
            
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
        """Generate structured data retrieval plan using exact endpoint keys with improved error handling"""
        
        # First get available endpoints
        available_endpoints = list(self.endpoints.keys())
        
        # Clean and validate intent entities
        cleaned_entities = {}
        for key, value in intent.get('entities', {}).items():
            if value and value.lower() != 'null':
                cleaned_entities[key] = value
        
        # Create base prompt with sanitized json
        intent_dict = {
            "primary_intent": intent.get('primary_intent', ''),
            "entities": cleaned_entities,
            "time_context": intent.get('time_context', ''),
            "data_requirements": list(intent.get('data_requirements', []))  # Convert to list explicitly
        }
        
        prompt = f"""Create a data retrieval plan using ONLY these exact MLB API endpoint keys:
        {available_endpoints}

        Current Intent: {json.dumps(intent_dict, default=str)}

        IMPORTANT: Only use endpoint names from the list above - they must match exactly.
        Do not modify or make up new endpoint names. Always start with endpoints not requiring any params nor queries.
        
        For general player info queries without a specific player, use these steps:
        1. Get list of top players (based on stats/awards)
        2. Get details for those players
        3. Get their recent achievements
        
        Return a plan as JSON with steps using these exact endpoint keys."""

        try:
            result = await asyncio.to_thread(
                self.model.generate_content,
                prompt,
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
                                        "endpoint": {
                                            "type": "string",
                                            "enum": available_endpoints
                                        },
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
                                                        "player_ids": { "type": "string" },
                                                        "names": { "type": "string" },
                                                        "stats": { "type": "string" },
                                                        "info": { "type": "string" }
                                                    }
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
                                    "required": ["id", "endpoint", "parameters", "extract", "depends_on"]
                                }
                            },
                            "dependencies": {
                                "type": "object",
                                "properties": {
                                    "step1": {
                                        "type": "array",
                                        "items": { "type": "string" }
                                    },
                                    "step2": {
                                        "type": "array",
                                        "items": { "type": "string" }
                                    }
                                }
                            }
                        },
                        "required": ["steps", "dependencies"]
                    }
                )
            )

            parsed_result = json.loads(result.text)
            
            # Validate endpoints
            for step in parsed_result.get('steps', []):
                if step['endpoint'] not in self.endpoints:
                    print(f"Warning: Generated invalid endpoint {step['endpoint']}")
                    # Replace with closest matching endpoint
                    for available in available_endpoints:
                        if step['endpoint'].lower() in available.lower():
                            step['endpoint'] = available
                            break
            
            # Ensure required fields exist
            for step in parsed_result.get('steps', []):
                if 'depends_on' not in step:
                    step['depends_on'] = []
                if 'required_for' not in step:
                    step['required_for'] = []
                if 'extract' not in step:
                    step['extract'] = {
                        "fields": {},
                        "filter": None
                    }
            
            print("Parsed data plan: ", parsed_result)
            return parsed_result

        except Exception as e:
            print(f"Error in create_data_plan: {str(e)}")
            # Return a safe default plan for player info
            return {
                "steps": [
                    {
                        "id": "step1",
                        "endpoint": "stats_leaders",
                        "parameters": {
                            "season": 2024,
                            "leaderCategories": "homeRuns",  # Single category to avoid list issues
                            "statType": "yearByYear",
                            "limit": 5
                        },
                        "extract": {
                            "fields": {
                                "player_ids": "leaders[*].person.id",
                                "names": "leaders[*].person.fullName"
                            },
                            "filter": None
                        },
                        "depends_on": [],
                        "required_for": ["step2"]
                    },
                    {
                        "id": "step2",
                        "endpoint": "people",
                        "parameters": {
                            "personId": {
                                "source_step": "step1",
                                "source_path": "leaders[0].person.id",
                                "filter": None
                            }
                        },
                        "extract": {
                            "fields": {
                                "info": "people[*]",
                                "stats": "stats"
                            },
                            "filter": None
                        },
                        "depends_on": ["step1"],
                        "required_for": []
                    }
                ],
                "dependencies": {
                    "step1": [],
                    "step2": ["step1"]
                }
            }
    async def execute_plan(self, deps: MLBDeps, plan: DataRetrievalPlan) -> Dict[str, Any]:
        '''Execute the retrieval plan with data filtering and extraction'''
        results = {}
        
        for step in plan['steps']:
            # Execute current step
            raw_result = await self._execute_step(deps, step, results)
            
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
        step: APIStep,
        prior_results: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Execute API step with improved error handling and parameter validation"""
        try:
            # Get endpoint info
            endpoint_info = self.endpoints.get(step['endpoint'])
            if not endpoint_info:
                raise ValueError(f"Invalid endpoint: {step['endpoint']}")

            # Validate and resolve parameters
            resolved_params = {}
            for param_name, param_value in step['parameters'].items():
                # Skip null parameters
                if param_value is None or param_value == 'null':
                    continue
                    
                if isinstance(param_value, str) and '_from_step' in param_value:
                    source_step = param_value.split('_from_step')[1]
                    if source_step not in prior_results:
                        continue  # Skip if dependent result not available
                        
                    source_data = prior_results[source_step]
                    if isinstance(source_data, dict):
                        # Try direct key match
                        if param_name.lower() in source_data:
                            resolved_params[param_name] = source_data[param_name.lower()]
                        # Try nested data
                        else:
                            for key, value in source_data.items():
                                if isinstance(value, dict) and param_name.lower() in value:
                                    resolved_params[param_name] = value[param_name.lower()]
                                    break
                else:
                    resolved_params[param_name] = param_value

            # Skip step if required parameters are missing
            if endpoint_info.get('required_params'):
                missing_params = [p for p in endpoint_info['required_params'] 
                                if p not in resolved_params]
                if missing_params:
                    print(f"Skipping step {step['id']} - missing required params: {missing_params}")
                    return None

            # Get formatted URL
            request_info = await self.get_formatted_url(
                step['endpoint'],
                endpoint_info,
                resolved_params,
                prior_results
            )
            
            if not request_info or 'url' not in request_info:
                return None

            # Make request
            try:
                response = await deps.client.get(request_info['url'])
                response.raise_for_status()
                raw_data = response.json()
            except Exception as e:
                print(f"API request failed for step {step['id']}: {str(e)}")
                return None

            # Generate processing code
            schema = self._analyze_response_schema(raw_data)
            processing_code = await self.generate_processing_code(
                step['endpoint'],
                schema,
                self.plan
            )

            # Create temporary directory for code execution
            with tempfile.TemporaryDirectory() as temp_dir:
                # Write raw data to temp file
                data_file_path = os.path.join(temp_dir, "data.json")
                with open(data_file_path, "w", encoding="utf-8") as f:
                    json.dump(raw_data, f)

                # Set up execution environment with temp file loading
                execution_code = f"""
    import json

    try:
        {processing_code}
        
        # Load data from temp file
        with open('{data_file_path}', 'r') as f:
            data = json.load(f)
        
        result = process_data(data)
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({{"error": str(e)}}))
    """

                # Execute code using REPL
                repl_result = await self.repl(code=execution_code)
                
                if repl_result.get('status') == 'error':
                    raise RuntimeError(f"Code execution failed: {repl_result.get('error')}")
                    
                try:
                    output = repl_result.get('output')
                    if not output:
                        raise ValueError("No output from code execution")
                        
                    processed_result = json.loads(output)
                    if isinstance(processed_result, dict) and "error" in processed_result:
                        raise RuntimeError(f"Processing error: {processed_result['error']}")
                        
                    return processed_result
                    
                except json.JSONDecodeError as e:
                    raise ValueError(f"Failed to parse processing result: {repl_result}")

        except Exception as e:
            print(f"Error executing step {step['id']}: {str(e)}")
            return None

    async def get_formatted_url(
        self,
        endpoint_name: str,
        endpoint_info: Dict[str, Any],
        parameters: Dict[str, Any],
        prior_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get formatted URL and parameters directly from LLM"""
        prompt = f"""Given this MLB API endpoint and data, return the formatted URL and parameters.

        Endpoint: {endpoint_name}
        Base URL: {endpoint_info['url']}
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
        """Process message with improved error handling"""
        try:
            # 1. Get intent analysis
            self.intent = await self.analyze_intent(message)
            if not self.intent:
                raise ValueError("Failed to analyze intent")

            # 2. Get retrieval plan
            self.plan = await self.create_data_plan(self.intent)
            if not self.plan:
                raise ValueError("Failed to create data retrieval plan")

            # 3. Execute plan
            data = await self.execute_plan(deps, self.plan)

            # 4. Generate response content
            response_data = await self.format_response(message, self.intent, data)
            
            # 5. Generate suggestions and actions
            suggestions = await self._generate_suggestions(self.intent, response_data)
            actions = await self._generate_actions(self.intent, response_data)
            
            # 6. Generate conversation
            conversation = await self.generate_conversation(
                message, 
                self.intent,
                response_data
            )

            return {
                "message": response_data['summary'],
                "conversation": conversation,
                "data_type": self.intent['primary_intent'],
                "data": response_data['details'],
                "context": {"intent": self.intent},
                "suggestions": suggestions,
                "media": response_data.get('media'),
                "actions": actions
            }

        except Exception as e:
            # Generate a friendly error response
            error_conversation = await self.generate_conversation(
                message,
                {"primary_intent": "unknown", "entities": {}, "time_context": "current", "data_requirements": []},
                {"summary": str(e), "details": {}}
            )

            return {
                "message": f"I encountered an error but I'll try to help: {str(e)}",
                "conversation": error_conversation,
                "data_type": "error",
                "data": {},
                "context": {},
                "suggestions": [
                    "Try asking about a specific team",
                    "Search for a player by name",
                    "Ask about today's games"
                ],
                "media": None,
                "actions": []
            }

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

# Create agent instance
with open('src/core/constants/endpoints.json', 'r') as f:
    endpoints_json = f.read()

mlb_agent = MLBAgent(api_key=settings.GEMINI_API_KEY, endpoints_json=endpoints_json)