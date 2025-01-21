import asyncio
from datetime import datetime
import os
import tempfile
import traceback
from typing import List, Optional, Dict, Any
import json
import google.generativeai as genai
import pandas as pd
from src.api.models import (
    Specificity,
    MLBResponse,
    MLBDeps,
    IntentAnalysis,
    IntentType,
    Timeframe,
    Complexity,
    ComparisonType,
    StatFocus,
    Sentiment,
    DataRetrievalPlan,
)
from src.api.repl import MLBPythonREPL
from src.core.settings import settings


class MLBAgent:
    def __init__(self, api_key: str, endpoints_json: str, functions_json: str):
        genai.configure(api_key=api_key)

        #Models
        self.model = genai.GenerativeModel("gemini-1.5-flash")
        self.gemini_2_model = genai.GenerativeModel("gemini-2.0-flash-exp")
        self.model_8b = genai.GenerativeModel("gemini-1.5-flash-8b")
        self.code_model = genai.GenerativeModel("gemini-1.5-pro")

        #Data
        self.endpoints = json.loads(endpoints_json)["endpoints"]
        self.functions = json.loads(functions_json)["functions"]
        self.homeruns = pd.read_csv("src/core/constants/mlb_homeruns.csv")
        self.media_source = json.loads(media_json)["sources"]

        self.intent = None
        self.plan = None
        self.repl = MLBPythonREPL(timeout=8)

        self._setup_prompts()
        #print(self.endpoints)

    def _setup_prompts(self):
        """Set up all prompts used by the agent"""
        self.intent_prompt = f"""
        Available MLB Stats API Functions:

            {json.dumps(self.functions, indent=2)}

            Available Endpoints:
            {json.dumps(self.endpoints, indent=2)}

            Current Date: {datetime.now().isoformat()}

        Please analyze the baseball query and return a structured JSON response with detailed intent analysis, and if mlb related.

COMMON MLB QUERIES AND HOW TO UNDERSTAND THEM:

Team Information:
"Tell me about the Yankees"
- Wants: Basic team information
- Focus: Team details, current season performance
- Data needed: Team stats, record, key players

"Show me who's on the Dodgers"
- Wants: Current roster information
- Focus: Active players on team
- Data needed: Full team roster, positions

Player Stats:
"How's Judge doing this season?"
- Wants: Current season performance
- Focus: Key offensive statistics
- Data needed: Player batting stats

"What are Scherzer's career numbers?"
- Wants: Career statistics
- Focus: Historical pitching performance
- Data needed: Career pitching stats

Game Information:
"When do the Cubs play next?"
- Wants: Upcoming game schedule
- Focus: Next scheduled game
- Data needed: Team schedule

"What was the score of yesterday's Red Sox game?"
- Wants: Recent game result
- Focus: Game score and outcome
- Data needed: Game results, box score

Standings & Rankings:
"Show me the AL East standings"
- Wants: Division standings
- Focus: Teams' current positions
- Data needed: Division standings data

"Who leads the league in home runs?"
- Wants: League leaders
- Focus: Specific statistic leaders
- Data needed: League batting stats

Comparative Analysis:
"Compare Ohtani and Trout's numbers"
- Wants: Player comparison
- Focus: Statistical comparison
- Data needed: Both players' stats

Historical Context:
"What were the Braves' stats last season?"
- Wants: Historical team performance
- Focus: Previous season data
- Data needed: Team historical stats

Game Details:
"Show me the box score from the Mets game"
- Wants: Detailed game information
- Focus: Complete game statistics
- Data needed: Full box score, game events

Season Progress:
"How many games are left in the season?"
- Wants: Schedule information
- Focus: Season timeline
- Data needed: Season schedule, current date

    Query to analyze: """

        self.plan_prompt = f"""Create a detailed MLB data retrieval plan optimizing for accuracy and efficiency.

Choose from the given functions/endpoints
Available Functions:
{json.dumps(self.functions, indent=2)}

Available Endpoints:
{json.dumps(self.endpoints, indent=2)}

Current Intent Analysis:
{json.dumps(self.intent, indent=2)}

KNOWN CONTEXT (Use these values directly - DO NOT create steps to fetch them):
- Current Season (seasonId): {datetime.now().year}
- Current Time: {datetime.now().isoformat()}
- Regular Season Status: In Progress
- League IDs: AL=103, NL=104

PLANNING EXAMPLES:

3. Simple Logo Request:
Input: "Show me the Yankees logo"
You should return:
{{
    "plan_type": "endpoint",
    "steps": [
        {{
            "id": "step1",
            "type": "function",
            "name": "lookup_team",
            "description": "Get Yankees team ID",
            "parameters": {{"value": "Yankees"}},
            "extract": {{"fields": {{"team_id": "$.teams[0].id"}}}},
            "depends_on": []
        }},
        {{
            "id": "step2",
            "type": "endpoint",
            "name": "team_logo",
            "description": "Get team logo using ID",
            "parameters": {{
                "teamId": {{"source_step": "step1", "source_path": "team_id"}}
            }},
            "extract": {{"fields": {{"url": "$.url"}}}},
            "depends_on": ["step1"]
        }}
    ]
}}

4. Player Stats Request:
Input: "How's Aaron Judge doing this season?"
Intent: {{
    "type": "PLAYER_STATS",
    "entities": {{"players": ["Judge"]}}
}}
Plan:
{{
    "plan_type": "function",
    "steps": [
        {{
            "id": "step1", 
            "type": "function",
            "name": "lookup_player",
            "description": "Get Aaron Judge's player ID",
            "parameters": {{"value": "Judge"}},
            "extract": {{"fields": {{"player_id": "$.id"}}}},
            "depends_on": []
        }},
        {{
            "id": "step2",
            "type": "function",
            "name": "player_stats",
            "description": "Get current season stats",
            "parameters": {{
                "personId": {{"source_step": "step1", "source_path": "player_id"}},
                "group": {{"value": "[hitting]"}},
                "type": {{"value": "season"}}
            }},
            "extract": {{"fields": {{"stats": "$.stats"}}}},
            "depends_on": ["step1"]
        }}
    ]
}}

PLANNING RULES:

1. Highlight Request Handling:
   • When intent type is HIGHLIGHT, prioritize video search
   • Use highlight_search step type for video lookups
   • Consider entity context (players, teams, dates) for search
   • Include relevant metadata in extraction

2. Data Source Selection:
   • Prefer direct data source if available (highlight database)
   • Fall back to API endpoints if needed
   • Combine sources for mixed requests

3. Input Resolution:
   • team_logo, team_stats need → teamId from lookup_team
   • player_stats, player_info need → personId from lookup_player
   • game endpoints need → gamePk from schedule
   
4. Efficiency:
   • Use direct endpoint if all inputs available
   • Minimize steps - don't fetch unnecessary data
   • Batch related queries when possible
   • Each step must feed required inputs to next step

The plan must follow this exact schema:
{{
    "plan_type": "string",        # Must be one of: "endpoint", "function"
    "steps": [
        {{
            "id": "string",       # Unique step identifier
            "type": "string",     # Must be either "endpoint" or "function" 
            "name": "string",     # Valid endpoint/function name
            "description": "string", # Purpose of this step
            "parameters": {{       # Parameters needed by endpoint/function
                "param_name": {{
                    "source_step": "string?",  # Step ID where value comes from
                    "source_path": "string?",  # JSON path to value in source step result
                    "value": "any"            # Direct value if not from prior step
                }}
            }},
            "extract": {{          # What to extract from step result
                "fields": {{       # Target fields mapped to JSON paths
                    "field_name": "json.path"
                }},
                "filter": "string?" # Optional filter condition
            }},
            "depends_on": ["string"] # Step IDs this step depends on
        }}
    ],
    "fallback": {{
        "enabled": true,         # Whether fallback is enabled
        "strategy": "string",    # Description of fallback approach
        "steps": []             # Same structure as primary steps
    }}
}}"""

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
                    response_mime_type="application/json",
                    response_schema=IntentAnalysis,
                ),
            )

            parsed_result = json.loads(result.text)
            print(parsed_result)
            # Convert enum strings to enum values
            parsed_result["intent"]["type"] = IntentType(
                parsed_result["intent"]["type"]
            )
            parsed_result["intent"]["specificity"] = Specificity(
                parsed_result["intent"]["specificity"]
            )
            parsed_result["intent"]["timeframe"] = Timeframe(
                parsed_result["intent"]["timeframe"]
            )
            parsed_result["intent"]["complexity"] = Complexity(
                parsed_result["intent"]["complexity"]
            )

            parsed_result["context"]["time_frame"] = Timeframe(
                parsed_result["context"]["time_frame"]
            )
            parsed_result["context"]["comparison_type"] = ComparisonType(
                parsed_result["context"]["comparison_type"]
            )
            parsed_result["context"]["stat_focus"] = StatFocus(
                parsed_result["context"]["stat_focus"]
            )
            parsed_result["context"]["sentiment"] = Sentiment(
                parsed_result["context"]["sentiment"]
            )

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
                    "complexity": Complexity.SIMPLE,
                },
                "entities": {
                    "teams": [],
                    "players": [],
                    "dates": [],
                    "stats": [],
                    "locations": [],
                    "events": [],
                },
                "context": {
                    "time_frame": Timeframe.CURRENT,
                    "comparison_type": ComparisonType.NONE,
                    "stat_focus": StatFocus.NONE,
                    "sentiment": Sentiment.NEUTRAL,
                    "requires_data": False,
                    "follow_up": False,
                    "data_requirements": [],
                },
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
                "Check team standings",
            ],
            "media": None,
        }

    def _create_fallback_response(
        self, message: str, intent: IntentAnalysis
    ) -> MLBResponse:
        """Create a response when MLB data processing fails"""
        return {
            "message": "I couldn't retrieve the specific baseball data you requested.",
            "conversation": "I understand you're asking about baseball, but I'm having trouble getting that specific information. Could you try asking in a different way?",
            "data_type": intent.get("intent", {}).get("type", "general").value,
            "data": {},
            "context": {"intent": intent},
            "suggestions": [
                "Try a simpler query",
                "Ask about basic stats",
                "Look up general team info",
            ],
            "media": None,
        }

    async def create_data_plan(self, intent: IntentAnalysis) -> DataRetrievalPlan:
        """Generate structured data retrieval plan with improved schema validation"""
        try:
            # Compile available resources
            available_endpoints = list(self.endpoints.keys())
            available_functions = [f["name"] for f in self.functions]

            # Define valid types and methods statically
            valid_types = {"endpoint": True, "function": True}

            valid_methods = {method: True for method in available_endpoints}
            valid_methods.update({method: True for method in available_functions})

            plan_types = {
                "endpoint": True,
                "function": True,
            }

            # Define response schema
            response_schema = {
                "type": "object",
                "properties": {
                    "plan_type": {"type": "string"},
                    "steps": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "type": {"type": "string"},
                                "name": {"type": "string"},
                                "description": {"type": "string"},
                                "parameters": {
                                    "type": "object",
                                    "properties": {
                                        "source_step": {"type": "string"},
                                        "source_path": {"type": "string"},
                                        "filter": {"type": "string"},
                                        "value": {"type": "string"},
                                    },
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
                                                "scores": {"type": "string"},
                                            },
                                        },
                                        "filter": {"type": "string"},
                                    },
                                    "required": ["fields"],
                                },
                                "depends_on": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                                "required_for": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                            },
                            "required": [
                                "id",
                                "type",
                                "name",
                                "description",
                                "parameters",
                                "extract",
                                "depends_on",
                            ],
                        },
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
                                                "filter": {"type": "string"},
                                            },
                                        },
                                        "extract": {
                                            "type": "object",
                                            "properties": {
                                                "fields": {
                                                    "type": "object",
                                                    "properties": {
                                                        "player_ids": {
                                                            "type": "string"
                                                        },
                                                        "names": {"type": "string"},
                                                        "stats": {"type": "string"},
                                                        "info": {"type": "string"},
                                                    },
                                                },
                                                "filter": {"type": "string"},
                                            },
                                            "required": ["fields"],
                                        },
                                        "depends_on": {
                                            "type": "array",
                                            "items": {"type": "string"},
                                        },
                                    },
                                    "required": [
                                        "id",
                                        "endpoint",
                                        "parameters",
                                        "extract",
                                        "depends_on",
                                    ],
                                },
                            },
                        },
                        "required": ["enabled", "strategy", "steps"],
                    },
                    "dependencies": {
                        "type": "object",
                        "properties": {
                            "step1": {"type": "array", "items": {"type": "string"}},
                            "step2": {"type": "array", "items": {"type": "string"}},
                        },
                    },
                },
                "required": ["plan_type", "steps", "fallback", "dependencies"],
            }

            # Define available methods statically to avoid list concatenation
            valid_methods = {method: True for method in available_endpoints}
            valid_methods.update({method: True for method in available_functions})

            # Generate plan using LLM
            result = await asyncio.to_thread(
                self.model.generate_content,
                self.plan_prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.2,
                    response_mime_type="application/json",
                    response_schema=response_schema,
                ),
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

    async def execute_plan(
        self, deps: MLBDeps, plan: DataRetrievalPlan
    ) -> Dict[str, Any]:
        """Execute the retrieval plan with data filtering and extraction"""
        results = {}

        for step in plan["steps"]:
            # Execute current step
            print(step)
            raw_result = await self._execute_step(deps, step, results)
            if not raw_result:
                continue

            # Apply extraction and filtering if specified
            if "extract" in step:
                filtered_result = self._extract_and_filter(
                    raw_result,
                    step["extract"].get("source_path"),
                    step["extract"].get("filter"),
                )
                results[step["id"]] = filtered_result
            else:
                results[step["id"]] = raw_result
        return results

    async def generate_processing_code(
        self, endpoint_name: str, schema: Dict[str, Any], plan
    ) -> str:
        """Generate Python code to process endpoint data based on schema and intent"""
        current_step = [
            step for step in plan["steps"] if step["endpoint"] == endpoint_name
        ]

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
                response_mime_type="text/plain", candidate_count=1
            ),
        )

        # Default processing code with proper indentation
        default_code = """def process_data(data):
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
"""

        try:
            generated_code = result.text.strip()
            generated_code = generated_code.replace("```python", "").replace("```", "")

            # Validate the generated code has proper function definition and indentation
            if not generated_code.startswith("def process_data(data):"):
                return default_code

            # Basic validation of code structure
            lines = generated_code.split("\n")
            if len(lines) < 2 or not any(
                line.strip().startswith("return") for line in lines
            ):
                return default_code

            return generated_code

        except Exception as e:
            print(f"Error in code generation: {str(e)}")
            return default_code

    async def _execute_step(
        self, deps: MLBDeps, step: Dict[str, Any], prior_results: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Execute step based on method type (function or endpoint)"""
        try:
            # Resolve basic parameters
            method_type = step.get("type", "")
            params = step.get("parameters", {})
            print(method_type)
            print(prior_results)
            # Execute based on method type
            if method_type == "function":
                result = await self._execute_function_step(deps, step, prior_results)
                return result
            elif method_type == "endpoint":
                result = await self._execute_endpoint_step(deps, step, prior_results)
                return result
            else:
                print(f"Unknown method type: {method_type}")
                return None
        except Exception as e:
            print(f"Error executing step {step.get('stepNumber')}: {str(e)}")

            # Try fallback if specified
            if step.get("fallback"):
                try:
                    print(f"Attempting fallback for step {step.get('stepNumber')}")
                    return await self._execute_fallback(deps, step, prior_results)
                except Exception as fallback_error:
                    print(f"Fallback failed: {str(fallback_error)}")

            return None

    async def _execute_function_step(
        self, deps: MLBDeps, step: Dict[str, Any], prior_results: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Execute MLB stats function"""
        try:
            # Get function name from parameters
            function_name = step["name"]  # .get('function')
            if not function_name or function_name.lower() == "none":
                # Handle custom processing functions
                return await self._execute_custom_processing(step, prior_results)
            # print("lj", function_name)
            # Find function info
            function_info = next(
                (f for f in self.functions if f["name"] == function_name), None
            )
            if not function_info:
                raise ValueError(f"Invalid function: {function_name}")

            # Prepare function parameters
            resolved_params = await self._resolve_parameters(
                step, prior_results
            )

            # Generate function execution code
            execution_code = f"""
    import statsapi

    try:
        result = statsapi.{function_name}({resolved_params["value"]})
        if result:
            print(json.dumps(result))
    except Exception as e:
        print(json.dumps({{"error": str(e)}}))
    """

            print(execution_code)
            # Execute function using REPL
            repl_result = await self.repl(code=execution_code)
            print("repl result:", repl_result)

            if repl_result.get("status") == "error":
                raise RuntimeError(
                    f"Function execution failed: {repl_result.get('error')}"
                )

            # Process result
            try:
                output = repl_result.get("output")
                if not output:
                    raise ValueError("No output from function execution")

                result = json.loads(output)
                if isinstance(result, dict) and "error" in result:
                    raise RuntimeError(f"Function error: {result['error']}")

                # TODO: If result is large than a threshold, continue, but if less, route to LLM to extract params for next steps
                # Process data extraction if specified
                """                
                if step.get("extract").get("filter"):
                    result = await self._apply_filtering(result, step["extract"])
                
                # Apply filtering if specified
                if step.get("extract"):
                    result = await self._process_extraction(result, step["extract"])
                """

                return result

            except json.JSONDecodeError as e:
                raise ValueError(f"Failed to parse function result: {repl_result}")

        except Exception as e:
            print(f"Function execution error: {str(e)}")
            return None

    async def _execute_endpoint_step(
        self, deps: MLBDeps, step: Dict[str, Any], prior_results: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Execute MLB API endpoint"""
        try:
            # Get endpoint from parameters
            endpoint_name = step["parameters"].get("value") 
            if not endpoint_name:
                raise ValueError("No endpoint specified")

            # Get endpoint info
            endpoint_info = self.endpoints.get(endpoint_name)
            if not endpoint_info:
                raise ValueError(f"Invalid endpoint: {endpoint_name}")

            # Resolve parameters
            resolved_params = await self._resolve_parameters(
                step, prior_results
            )

            # Get formatted URL
            request_info = await self.get_formatted_url(
                endpoint_name, endpoint_info, resolved_params, prior_results
            )

            if not request_info or "url" not in request_info:
                raise ValueError("Failed to format URL")

            # Make request
            response = await deps.client.get(request_info["url"])
            response.raise_for_status()
            result = response.json()

            # Process data extraction if specified
            if step.get("dataExtraction"):
                result = await self._process_extraction(result, step["dataExtraction"])

            # Apply filtering if specified
            if step.get("filtering") and step["filtering"].lower() != "none":
                result = await self._apply_filtering(result, step["filtering"])

            return result

        except Exception as e:
            print(f"Endpoint execution error: {str(e)}")
            return None

    async def _execute_custom_processing(
        self, step: Dict[str, Any], prior_results: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Execute custom data processing step"""
        try:
            # Generate processing code based on step description and parameters
            processing_code = await self._generate_processing_code(
                step["description"], step["parameters"], prior_results
            )

            # Prepare data for processing
            process_data = {
                "prior_results": prior_results,
                "parameters": step["parameters"],
            }

            # Execute processing
            with tempfile.TemporaryDirectory() as temp_dir:
                data_file = os.path.join(temp_dir, "process_data.json")
                with open(data_file, "w") as f:
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

                if repl_result.get("status") == "error":
                    raise RuntimeError(f"Processing failed: {repl_result.get('error')}")

                try:
                    output = repl_result.get("output")
                    if not output:
                        raise ValueError("No output from function execution")

                    result = json.loads(output)
                    if isinstance(result, dict) and "error" in result:
                        raise RuntimeError(f"Function error: {result['error']}")

                    # Calculate result size
                    result_size = len(json.dumps(result))
                    size_threshold = 10000  # Threshold in characters for routing to LLM

                    if result_size <= size_threshold:
                        # For smaller results, use Gemini for intelligent extraction
                        prompt = f"""Extract specific data from this MLB API response based on requirements.

                Input data:
                {json.dumps(result, indent=2)}

                Requirements:
                - Extract fields specified in: {json.dumps(step.get('extract', {}), indent=2)}
                - Handle missing or null values gracefully
                - Return only the requested fields
                - Maintain original data types (numbers, strings, etc.)
                - Follow specified extraction paths exactly

                Return only the extracted data as valid JSON without any explanation."""

                        try:
                            extraction_result = await asyncio.to_thread(
                                self.code_model.generate_content,
                                prompt,
                                generation_config=genai.GenerationConfig(
                                    temperature=0.1,  # Low temperature for precise extraction
                                    response_mime_type="application/json"
                                ),
                            )
                            
                            # Parse and validate LLM response
                            extracted_data = json.loads(extraction_result.text)
                            
                            # Apply any specified filters
                            if step.get("extract", {}).get("filter"):
                                extracted_data = await self._apply_filtering(
                                    extracted_data, 
                                    step["extract"]["filter"]
                                )
                            
                            return extracted_data

                        except Exception as llm_error:
                            print(f"LLM extraction failed: {str(llm_error)}, falling back to standard processing")
                            # Fall back to standard processing on LLM failure

                    # For larger results or LLM failure, use standard processing
                    if step.get("extract", {}).get("filter"):
                        result = await self._apply_filtering(result, step["extract"])

                    if step.get("extract"):
                        result = await self._process_extraction(result, step["extract"])

                    return result

                except json.JSONDecodeError as e:
                    raise ValueError(f"Failed to parse function result: {repl_result}")
        except Exception as e:
            print(f"Error in result processing: {str(e)}")
            raise

    async def _process_extraction(
        self,
        data: Any,
        extraction_info: str,
        size_threshold: int = 500_000,  # Default threshold in characters, chosen hazardly
    ) -> Any:
        """Process data extraction based on extraction info and data size"""
        data_size = (
            len(json.dumps(data)) if isinstance(data, (dict, list)) else len(str(data))
        )
        print("data size", data_size)
        if data_size <= size_threshold:
            # For small data, use LLM directly
            prompt = f"""Given this data:
            {json.dumps(data) if isinstance(data, (dict, list)) else str(data)}
            
            Extract data given its instruction/schema:
            {extraction_info}
            
            Return only the extracted data in valid JSON format.
            """

            try:
                result = await asyncio.to_thread(
                    self.code_model.generate_content,
                    prompt,
                    generation_config=genai.GenerationConfig(
                        response_mime_type="text/plain",
                    ),
                )
                # print(result)
                dict_result = (
                    result.text.strip()
                    .replace("```json\n", "")
                    .replace("```", "")
                    .replace("\n", "")
                )
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
                        response_mime_type="text/plain"
                    ),
                )

                extraction_code = (
                    result.text.strip().replace("```python", "").replace("```", "")
                )

                with tempfile.TemporaryDirectory() as temp_dir:
                    data_file = os.path.join(temp_dir, "data.json")
                    with open(data_file, "w") as f:
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

                    if repl_result.get("status") == "error":
                        raise RuntimeError(
                            f"Extraction failed: {repl_result.get('error')}"
                        )

                    try:
                        output = repl_result.get("output")
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
        size_threshold: int = 10000,  # Default threshold in characters
    ) -> Any:
        """Apply filtering based on filtering info and data size"""
        if not filtering_info or filtering_info.lower() == "none":
            return data

        data_size = (
            len(json.dumps(data)) if isinstance(data, (dict, list)) else len(str(data))
        )

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
                        response_mime_type="text/plain"
                    ),
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
                        response_mime_type="text/plain"
                    ),
                )

                filtering_code = (
                    result.text.strip().replace("```python", "").replace("```", "")
                )

                with tempfile.TemporaryDirectory() as temp_dir:
                    data_file = os.path.join(temp_dir, "data.json")
                    with open(data_file, "w") as f:
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

                    if repl_result.get("status") == "error":
                        raise RuntimeError(
                            f"Filtering failed: {repl_result.get('error')}"
                        )

                    try:
                        output = repl_result.get("output")
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
        prior_results: Dict[str, Any],
    ) -> Dict[str, Any]:
        print(endpoint_info)
        """Get formatted URL and parameters directly from LLM"""
        prompt = f"""Given this MLB API endpoint and data, return the formatted URL and parameters.

        Endpoint: {endpoint_name}
        Base URL: {endpoint_info["endpoint"]["url"]}
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
            ),
        )
        # print(result.text)
        return json.loads(result.text)

    def _analyze_response_schema(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze and extract schema from API response with improved type handling"""
        schema = {}

        def get_type(value: Any) -> str:
            if isinstance(value, bool):
                return "boolean"
            elif isinstance(value, int):
                return "integer"
            elif isinstance(value, float):
                return "number"
            elif isinstance(value, str):
                return "string"
            elif isinstance(value, (list, tuple)):
                return "array"
            elif isinstance(value, dict):
                return "object"
            elif value is None:
                return "null"
            else:
                return "unknown"

        def extract_schema(obj: Any, current_schema: Dict[str, Any]):
            current_schema["type"] = get_type(obj)

            if isinstance(obj, dict):
                current_schema["properties"] = {}
                for key, value in obj.items():
                    current_schema["properties"][key] = {}
                    extract_schema(value, current_schema["properties"][key])

            elif isinstance(obj, (list, tuple)) and obj:
                current_schema["items"] = {}
                # Get schema of first item as sample
                extract_schema(obj[0], current_schema["items"])

        extract_schema(data, schema)
        return schema

    async def _execute_processing_code(
        self, processing_code: str, data: Dict[str, Any]
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

    async def _resolve_parameters(
        self, 
        step: Dict[str, Any], 
        prior_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve API parameters using Gemini for intelligent parameter formatting"""
        try:
            # Get function/endpoint info
            step_type = step.get("type")
            step_name = step.get("name")
            
            if step_type == "function":
                function_info = next(
                    (f for f in self.functions if f["name"] == step_name), 
                    None
                )
                if not function_info:
                    raise ValueError(f"Invalid function: {step_name}")
                
                prompt = f"""Format MLB Stats API function parameters.

    Function Info:
    {json.dumps(function_info, indent=2)}

    Step Parameters:
    {json.dumps(step["parameters"], indent=2)}

    Prior Results Available:
    {json.dumps(prior_results, indent=2)}

    Requirements:
    1. Return ONLY the parameter string to go between parentheses in: statsapi.{step_name}()
    2. Replace any $referenced values with actual values from prior results
    3. Format according to function signature
    4. Include parameter names for clarity
    5. Handle missing optional parameters appropriately

    Example good outputs:
    "teamId=143, season=2025"
    "personId=12345, group='[hitting,pitching]'"
    "gamePk=123456"

    Return only the parameter string, no explanations or json formatting."""

            else:  # endpoint
                endpoint_info = self.endpoints.get(step_name)
                if not endpoint_info:
                    raise ValueError(f"Invalid endpoint: {step_name}")

                prompt = f"""Format MLB Stats API endpoint parameters.

    Endpoint Info:
    {json.dumps(endpoint_info, indent=2)}

    Step Parameters:
    {json.dumps(step["parameters"], indent=2)}

    Prior Results Available:
    {json.dumps(prior_results, indent=2)}

    Requirements:
    1. Return a dictionary with a single 'parameters' key containing the query parameters
    2. Replace any $referenced values with actual values from prior results
    3. Include all required parameters from endpoint info
    4. Format values according to API expectations
    5. Handle missing optional parameters appropriately

    Example good output:
    {{"parameters": {{"teamId": "143", "season": "2025"}}}}

    Return only the parameters dictionary as valid JSON."""

            # Get parameter resolution from Gemini
            result = await asyncio.to_thread(
                self.model.generate_content,
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.1,  # Low temperature for precise formatting
                    response_mime_type="text/plain" if step_type == "function" else "application/json"
                ),
            )

            if step_type == "function":
                # For functions, return the raw parameter string
                return {"value": result.text.strip()}
            else:
                # For endpoints, parse the JSON response
                try:
                    parsed = json.loads(result.text)
                    return parsed.get("parameters", {})
                except json.JSONDecodeError:
                    print(f"Failed to parse endpoint parameters: {result.text}")
                    # Fall back to basic parameter resolution
                    return self._basic_parameter_resolution(step["parameters"], prior_results)

        except Exception as e:
            print(f"Parameter resolution error: {str(e)}")
            # Fall back to basic parameter resolution
            return self._basic_parameter_resolution(step["parameters"], prior_results)

    def _basic_parameter_resolution(
        self,
        parameters: Dict[str, Any],
        prior_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Basic parameter resolution as fallback"""
        resolved = {}
        for param, value in parameters.items():
            if isinstance(value, str) and value.startswith("$"):
                ref_parts = value[1:].split(".")
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

    async def format_response(self, query: str, data: Dict[str, Any]) -> Any:
        """Get structured response content"""
        try:
            # Construct response schema and default fallback
            default_response = {
                "summary": "Here's what I found about the baseball stats.",
                "details": data,
                "media": None
            }
            
            # Convert Enum values to strings
            sanitized_intent = {
                'context': {k: str(v.value) if hasattr(v, 'value') else v 
                        for k, v in self.intent['context'].items()},
                'intent': {k: str(v.value) if hasattr(v, 'value') else v 
                        for k, v in self.intent['intent'].items()},
                'entities': self.intent['entities']
            }
                
            # Create prompt only after preparing defaults
            prompt = f"""Create a natural, informative response from this MLB data.
                
            Query: {query}
            
            Intent:
            {json.dumps(sanitized_intent)}
            
            Data:
            {json.dumps(data)}
            
            Return JSON with:
            - summary: A brief overview (1-2 sentences)
            - details: The complete data and analysis
            - media: Optional media content (if applicable)"""
            
            try:
                model_response = await asyncio.to_thread(
                    self.gemini_2_model.generate_content,
                    prompt,
                    generation_config=genai.GenerationConfig(
                        response_mime_type="application/json"
                    ),
                )
                
                if not model_response or not hasattr(model_response, 'text'):
                    return default_response
                    
                return json.loads(model_response.text)
                
            except Exception as e:
                print(f"Model generation error: {str(e)}")
                return default_response
                    
        except Exception as e:
            print(f"Error in format_response: {str(e)}")
            return {
                "summary": "Here's the baseball data I found.",
                "details": data,
                "media": None
            }
    async def generate_conversation(
            self,
            message: str,
            response_data: Optional[Any] = None,
        ) -> str:
            """Generate a friendly conversational response"""
            try:
                # First sanitize the response_data if it contains any Enum values
                def sanitize_enum_values(obj):
                    if isinstance(obj, dict):
                        return {k: sanitize_enum_values(v) for k, v in obj.items()}
                    elif isinstance(obj, list):
                        return [sanitize_enum_values(item) for item in obj]
                    elif hasattr(obj, 'value'):  # Check if it's an Enum
                        return str(obj.value)
                    return obj

                # Sanitize both intent and response data
                if self.intent:
                    sanitized_intent = sanitize_enum_values(self.intent)
                else:
                    sanitized_intent = {}

                if response_data:
                    sanitized_response = sanitize_enum_values(response_data)
                else:
                    sanitized_response = {}

                context = ""
                if sanitized_intent and sanitized_response:
                    context = f"""
                    Intent: {json.dumps(sanitized_intent)}
                    Data response: {json.dumps(sanitized_response, indent=2)}
                    """

                result = await asyncio.to_thread(
                    self.code_model.generate_content,
                    f"""{self.conversation_prompt}
                    
                    User query: "{message}"
                    {context}
                    
                    Generate a friendly response:""",
                    generation_config=genai.GenerationConfig(
                        response_mime_type="text/plain"
                    ),
                )
                return result.text.strip()
            except Exception as e:
                print(f"Error generating conversation: {str(e)}")
                traceback.print_exc()
                return "I'd be happy to talk baseball with you! What would you like to know about the game?"

    def _get_default_suggestions(self) -> List[str]:
        """Get default suggestions when no context-specific ones are available"""
        return [
            "Tell me about today's games",
            "Who are the top players this season?",
            "Show me the latest standings",
            "What are some exciting home runs?",
            "Tell me about your favorite baseball moment"
        ]
    async def _generate_suggestions(
        self, response: Any
    ) -> List[str]:
        """Generate contextual suggestions using LLM"""
        sanitized_intent = {
            'context': {k: str(v.value) if hasattr(v, 'value') else v 
                    for k, v in self.intent['context'].items()},
            'intent': {k: str(v.value) if hasattr(v, 'value') else v 
                    for k, v in self.intent['intent'].items()},
            'entities': self.intent['entities']
        }
        result = await asyncio.to_thread(
            self.model.generate_content,
            f"""{self.suggestion_prompt}
            
            Current intent:
            {json.dumps(sanitized_intent)}
            
            Current response:
            {json.dumps(response, indent=2)}""",
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema={
                    "type": "array",
                    "items": {"type": "string"},
                },
            ),
        )
        return json.loads(result.text)


    async def process_message(self, deps: MLBDeps, message: str) -> MLBResponse:
        """Enhanced message processing with media resolution"""
        try:
            # Get intent analysis
            self.intent = await self.analyze_intent(message)

            # MLB-related query path
            if self.intent["is_mlb_related"] and self.intent["context"].get("requires_data", True):
                try:
                    # Execute main data plan
                    plan = await self.create_data_plan(self.intent)
                    data = await self.execute_plan(deps, plan)
                    response_data = await self.format_response(message, data)
                    
                    # Add media resolution step
                    media = await self._resolve_media(
                        data,
                        plan.get("steps", [])
                    )
                    
                    if media:
                        response_data["media"] = media

                    suggestions = await self._generate_suggestions(response_data)
                    conversation = await self.generate_conversation(
                        message, response_data
                    )

                    return {
                        "message": response_data["summary"],
                        "conversation": conversation,
                        "data_type": self.intent["intent"],
                        "data": response_data["details"],
                        "context": {"intent": self.intent},
                        "suggestions": suggestions,
                        "media": response_data.get("media"),
                    }
                    
                except Exception as execution_error:
                    print(f"Execution error: {str(execution_error)}")
                    return self._create_error_response(message, str(execution_error))
            
            # Handle non-MLB queries as before...
            else:
                conversation = await self.generate_conversation(message, self.intent)
                suggestions = self._get_default_suggestions()
                
                return {
                    "message": self.intent.get("intent_description", "Let's talk baseball!"),
                    "conversation": conversation,
                    "data_type": "conversation",
                    "data": {},
                    "context": {"intent": self.intent},
                    "suggestions": suggestions,
                    "media": None
                }

        except Exception as e:
            print(f"Critical error in process_message: {str(e)}")
            return self._create_error_response(message, str(e))

    async def _resolve_media(self, intent: Dict[str, Any], data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Resolve what media to return based on context"""
        try:
            # Only pass titles for selection
            homerun_titles = self.homeruns['title'].tolist()
            
            prompt = f"""Based on this MLB context, determine what media to return.

            Intent: {json.dumps(intent, indent=2)}
            Data: {json.dumps(data, indent=2)}
            
            Available Homerun Titles:
            {json.dumps(homerun_titles, indent=2)}

            Available other media sources:
            {json.dumps(media_json, indent=2)}

            Return JSON array of media to include:
            [
                {{
                    "type": "image" | "video",
                    "source": "headshot" | "logo" | "homerun",
                    "params": {{
                        // For headshots: "player_id"
                        // For logos: "team_id" 
                        // For homeruns: "title" - return the most relevant title from the list
                    }}
                }}
            ]

            Rules:
            - Only return relevant media based on context
            - For homeruns, pick the most relevant title matching the query/context
            - Can return multiple items if appropriate"""

            result = await asyncio.to_thread(
                self.model.generate_content,
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.1,
                    response_mime_type="application/json"
                ),
            )

            media_plan = json.loads(result.text)
            media_results = []

            for item in media_plan:
                if item["source"] == "headshot":
                    # Get description for player headshot
                    headshot_prompt = f"""Describe this MLB player's headshot with baseball passion. Include:
                    1. Their role and notable achievements
                    2. Their playing style and impact
                    3. Any iconic elements or memorable features

                    Make it engaging and highlight their importance to the game.
                    Return only the description, no explanations."""

                    description = await asyncio.to_thread(
                        self.model.generate_content,
                        headshot_prompt,
                        generation_config=genai.GenerationConfig(
                            temperature=0.7,
                            response_mime_type="text/plain"
                        ),
                    )

                    media_results.append({
                        "type": "image",
                        "url": f"https://img.mlbstatic.com/mlb-photos/image/upload/d_people:generic:headshot:67:current.png/w_213,q_auto:best/v1/people/{item['params']['player_id']}/headshot/67/current",
                        "description": description.text
                    })
                    
                elif item["source"] == "logo":
                    # Get description for team logo
                    logo_prompt = f"""Describe this MLB team's logo with baseball passion. Include:
                    1. The team's history and legacy
                    2. Notable championships and eras
                    3. What the logo represents to fans
                    4. The team's impact on baseball

                    Make it engaging and capture the team's spirit.
                    Return only the description, no explanations."""

                    description = await asyncio.to_thread(
                        self.model.generate_content,
                        logo_prompt,
                        generation_config=genai.GenerationConfig(
                            temperature=0.7,
                            response_mime_type="text/plain"
                        ),
                    )

                    media_results.append({
                        "type": "image", 
                        "url": f"https://www.mlbstatic.com/team-logos/{item['params']['team_id']}.svg",
                        "description": description.text
                    })
                    
                elif item["source"] == "homerun":
                    # Get video by exact title match
                    video_data = self.homeruns[self.homeruns['title'] == item['params']['title']].iloc[0]
                    
                    # Get description for homerun highlight
                    highlight_prompt = f"""Describe this MLB homerun highlight with baseball passion:

                    Title: {video_data['title']}
                    Stats:
                    - Exit Velocity: {video_data['ExitVelocity']} mph
                    - Launch Angle: {video_data['LaunchAngle']}°
                    - Distance: {video_data['HitDistance']} ft

                    Include:
                    1. The impact and excitement of the moment
                    2. The impressive stats and what they mean
                    3. The significance for the player/team
                    4. Any dramatic elements or context

                    Make it thrilling and capture the moment's energy.
                    Return only the description, no explanations."""

                    description = await asyncio.to_thread(
                        self.model.generate_content,
                        highlight_prompt,
                        generation_config=genai.GenerationConfig(
                            temperature=0.7,
                            response_mime_type="text/plain"
                        ),
                    )
                    
                    media_results.append({
                        "type": "video",
                        "url": video_data['video'],
                        "title": video_data['title'],
                        "description": description.text,
                        "metadata": {
                            "exit_velocity": float(video_data['ExitVelocity']),
                            "launch_angle": float(video_data['LaunchAngle']),
                            "distance": float(video_data['HitDistance'])
                        }
                    })

            return media_results

        except Exception as e:
            print(f"Media resolution error: {str(e)}")
            traceback.print_exc()
            return []
    def _extract_and_filter(
        self, data: Any, path: Optional[str], filter_condition: Optional[str]
    ) -> Any:
        """Extract and filter data based on specified path and condition"""
        if not path:
            return data

        # Extract data using path
        result = data
        for key in path.split("."):
            if "[" in key:  # Handle array access
                key, index = key.split("[")
                index = int(index.rstrip("]"))
                result = result[key][index]
            else:
                result = result.get(key, {})

        # Apply filter if specified
        if filter_condition and isinstance(result, list):
            try:
                # Create safe evaluation environment
                def evaluate_condition(item, condition):
                    return eval(condition, {"__builtins__": {}}, {"item": item})

                result = [
                    item
                    for item in result
                    if evaluate_condition(item, filter_condition)
                ]
            except Exception as e:
                print(f"Filter evaluation failed: {str(e)}")

        return result

    async def _generate_processing_code(
        self,
        description: str,
        parameters: Dict[str, Any],
        prior_results: Dict[str, Any],
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
                    response_mime_type="text/plain",
                    temperature=0.2,  # Lower temperature for more focused code generation
                    candidate_count=1,
                ),
            )

            # Clean up generated code
            generated_code = result.text.strip()
            generated_code = generated_code.replace("```python", "").replace("```", "")

            # Validate basic structure
            if not generated_code.startswith("def process_data("):
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
with open("src/core/constants/endpoints.json", "r") as f:
    endpoints_json = f.read()

with open("src/core/constants/mlb_functions.json", "r") as f:
    functions_json = f.read()

with open("src/core/constants/media_sources.json", "r") as f:
    media_json = f.read()

mlb_agent = MLBAgent(
    api_key=settings.GEMINI_API_KEY,
    endpoints_json=endpoints_json,
    functions_json=functions_json,
)
