import asyncio
import base64
from datetime import datetime
import difflib
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
from src.api.utils import sanitize_code
from src.api.gemini_solid import GeminiSolid

class MLBAgent:
    def __init__(
        self,
        api_key: str,
        endpoints_json: str,
        functions_json: str,
        media_json: str,
        charts_json: str,
    ):
        genai.configure(api_key=api_key)

        # Models
        self.gemini = GeminiSolid()

        # Data
        self.endpoints = json.loads(endpoints_json)["endpoints"]
        self.functions = json.loads(functions_json)["functions"]
        self.homeruns = pd.read_csv("src/core/constants/mlb_homeruns.csv")
        self.media_source = json.loads(media_json)["sources"]
        self.charts_docs = json.loads(charts_json)["charts"]

        self.user_query = ""
        self.intent = None
        self.plan = None
        self.repl = MLBPythonREPL(timeout=8)

        self._setup_prompts()
        # print(self.endpoints)

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
        self.plan_prompt = f"""Create an optimized MLB data retrieval plan that leverages data flow relationships.

Available Resources:
Functions: {json.dumps(self.functions, indent=2)}
Endpoints: {json.dumps(self.endpoints, indent=2)}

PLANNING PRINCIPLES:
1. Data Flow Optimization
- Follow recommended next steps from endpoints/functions
- Use established data pipelines for common scenarios
- Leverage output-input relationships between steps
- Batch related requests when possible

2. Error Handling
- Include fallback options for each critical step

3. Context Preservation
- Maintain relationships between data points
- Track data lineage through transformations
- Preserve metadata for context
- Ensure entity relationships remain clear

COMPREHENSIVE EXAMPLE PATTERNS:

1. Advanced Judge's Career Analysis:
{{
    "steps": [
        {{
            "id": "player_lookup",
            "type": "function",
            "name": "lookup_player",
            "description": "Get player ID and basic info",
            "parameters": {{
                "value": "names=Judge"
            }},
            "extract": {{
                "fields": {{
                    "player_ids": "$.players[*].id",
                    "names": "$.players[*].fullName",
                    "team_ids": "$.players[*].currentTeam.id"
                }}
            }},
            "depends_on": []
        }},
        {{
            "id": "career_stats",
            "type": "function",
            "name": "player_stat_data",
            "description": "Get career statistics",
            "parameters": {{
                "value": "personIds=${{player_lookup.player_ids}}&group=hitting,pitching&type=yearByYear"
            }},
            "extract": {{
                "fields": {{
                    "stats": "$.stats[*].splits[*]",
                    "info": "$.stats[*].group"
                }}
            }},
            "depends_on": ["player_lookup"]
        }},
        {{
            "id": "league_context",
            "type": "function",
            "name": "league_leader_data",
            "description": "Get league context for performance",
            "parameters": {{
                "value": "leaderCategories=homeRuns,battingAverage&season=2024"
            }},
            "extract": {{
                "fields": {{
                    "stats": "$.leagueLeaders[*]",
                    "info": "$.leagueLeaders[*].person"
                }}
            }},
            "depends_on": ["career_stats"]
        }}
    ],
    "dependencies": {{
        "career_stats": ["player_lookup"],
        "league_context": ["career_stats"]
    }}
}}

2. Team Performance Analysis:
{{
    "steps": [
        {{
            "id": "team_lookup",
            "type": "function",
            "name": "lookup_team",
            "description": "Get team ID and basic info",
            "parameters": {{
                "value": "teamId=143"
            }},
            "extract": {{
                "fields": {{
                    "team_ids": "$.teams[0].id",
                    "names": "$.teams[0].name",
                    "info": "$.teams[0].league"
                }}
            }},
            "depends_on": []
        }},
        {{
            "id": "team_stats",
            "type": "function",
            "name": "team_stats",
            "description": "Get detailed team statistics",
            "parameters": {{
                "value": "teamId=${{team_lookup.team_ids}}&stats=season&group=hitting,pitching,fielding"
            }},
            "extract": {{
                "fields": {{
                    "stats": "$.stats[*].splits[*]",
                    "info": "$.stats[*].group"
                }}
            }},
            "depends_on": ["team_lookup"]
        }},
        {{
            "id": "roster_info",
            "type": "function",
            "name": "roster",
            "description": "Get current team roster",
            "parameters": {{
                "value": "teamId=${{team_lookup.team_ids}}&rosterType=active"
            }},
            "extract": {{
                "fields": {{
                    "player_ids": "$.roster[*].person.id",
                    "names": "$.roster[*].person.fullName",
                    "info": "$.roster[*].position"
                }}
            }},
            "depends_on": ["team_lookup"]
        }}
    ],
    "dependencies": {{
        "team_stats": ["team_lookup"],
        "roster_info": ["team_lookup"]
    }}
}}

3. Game Analysis with Play-by-Play:
{{
    "steps": [
        {{
            "id": "schedule_lookup",
            "type": "function",
            "name": "schedule",
            "description": "Get game schedule and identifiers",
            "parameters": {{
                "value": "date=2024-01-24&teamId=143"
            }},
            "extract": {{
                "fields": {{
                    "game_ids": "$.dates[0].games[*].gamePk",
                    "dates": "$.dates[0].date",
                    "team_ids": "$.dates[0].games[*].teams.home.team.id"
                }}
            }},
            "depends_on": []
        }},
        {{
            "id": "game_playbyplay",
            "type": "function",
            "name": "game_playByPlay",
            "description": "Get detailed play-by-play data",
            "parameters": {{
                "value": "gamePk=${{schedule_lookup.game_ids}}"
            }},
            "extract": {{
                "fields": {{
                    "stats": "$.allPlays[*].matchup",
                    "info": "$.allPlays[*].result",
                    "scores": "$.allPlays[?(@.about.isScoringPlay==true)].result"
                }}
            }},
            "depends_on": ["schedule_lookup"]
        }},
        {{
            "id": "game_boxscore",
            "type": "function",
            "name": "game_boxscore",
            "description": "Get game statistics and boxscore",
            "parameters": {{
                "value": "gamePk=${{schedule_lookup.game_ids}}&fields=teams,pitchers,batters"
            }},
            "extract": {{
                "fields": {{
                    "stats": "$.teams[*].players[*].stats",
                    "info": "$.info",
                    "scores": "$.teams[*].runs"
                }}
            }},
            "depends_on": ["schedule_lookup"]
        }}
    ],
    "dependencies": {{
        "game_playbyplay": ["schedule_lookup"],
        "game_boxscore": ["schedule_lookup"]
    }}
}}

4. League Standings and Statistics:
{{
    "steps": [
        {{
            "id": "standings",
            "type": "function",
            "name": "standings",
            "description": "Get current league standings",
            "parameters": {{
                "value": "leagueId=103,104&season=2024"
            }},
            "extract": {{
                "fields": {{
                    "stats": "$.records[*].teamRecords[*]",
                    "team_ids": "$.records[*].teamRecords[*].team.id",
                    "info": "$.records[*].division"
                }}
            }},
            "depends_on": []
        }},
        {{
            "id": "league_leaders",
            "type": "function",
            "name": "league_leader_data",
            "description": "Get league statistical leaders",
            "parameters": {{
                "value": "leaderCategories=homeRuns,battingAverage,era,strikeouts&season=2024"
            }},
            "extract": {{
                "fields": {{
                    "player_ids": "$.leagueLeaders[*].person.id",
                    "names": "$.leagueLeaders[*].person.fullName",
                    "stats": "$.leagueLeaders[*]",
                    "team_ids": "$.leagueLeaders[*].team.id"
                }}
            }},
            "depends_on": []
        }},
        {{
            "id": "division_stats",
            "type": "function",
            "name": "division_stats",
            "description": "Get division-level statistics",
            "parameters": {{
                "value": "divisionId=${{standings.info[0].id}}&season=2024"
            }},
            "extract": {{
                "fields": {{
                    "stats": "$.teams[*].stats[*]",
                    "info": "$.division"
                }}
            }},
            "depends_on": ["standings"]
        }}
    ],
    "dependencies": {{
        "division_stats": ["standings"]
    }}
}}

5. Player Comparison Analysis:
{{
    "steps": [
        {{
            "id": "players_lookup",
            "type": "function",
            "name": "lookup_player",
            "description": "Get player IDs and basic info",
            "parameters": {{
                "value": "names=Ohtani,Judge,Trout"
            }},
            "extract": {{
                "fields": {{
                    "player_ids": "$.players[*].id",
                    "names": "$.players[*].fullName",
                    "team_ids": "$.players[*].currentTeam.id"
                }}
            }},
            "depends_on": []
        }},
        {{
            "id": "comparison_stats",
            "type": "function",
            "name": "player_stat_data",
            "description": "Get detailed statistics for comparison",
            "parameters": {{
                "value": "personIds=${{players_lookup.player_ids}}&group=hitting&type=season"
            }},
            "extract": {{
                "fields": {{
                    "stats": "$.stats[*].splits[*]",
                    "info": "$.stats[*].group"
                }}
            }},
            "depends_on": ["players_lookup"]
        }},
        {{
            "id": "stat_percentiles",
            "type": "function",
            "name": "player_percentiles",
            "description": "Get statistical percentiles for context",
            "parameters": {{
                "value": "personIds=${{players_lookup.player_ids}}&stats=batting_exit_velocity,batting_average,ops"
            }},
            "extract": {{
                "fields": {{
                    "stats": "$.stats[*].percentiles",
                    "info": "$.stats[*].group"
                }}
            }},
            "depends_on": ["players_lookup", "comparison_stats"]
        }}
    ],
    "dependencies": {{
        "stat_percentiles": ["players_lookup", "comparison_stats"]
    }}
}}

Return a complete plan following this schema with appropriate data flows and dependencies:
{{
    'steps': [
        {{
            'id': 'step_id',
            'type': 'function',  # Must always be either 'function' or 'endpoint'
            'name': 'function_name', # From available functions/endpoints
            'description': 'what this step does',
            'parameters': {{
                'value': 'parameter string that can reference prior results with ${{step.field}}'
            }},
            'extract': {{
                'fields': {{
                    'player_ids': 'jsonpath for player ids',
                    'names': 'jsonpath for names',
                    'stats': 'jsonpath for statistics',
                    'info': 'jsonpath for additional info',
                    'team_ids': 'jsonpath for team ids',
                    'game_ids': 'jsonpath for game ids',
                    'dates': 'jsonpath for dates',
                    'scores': 'jsonpath for scores'
                }}
            }},
            'depends_on': ['list of step ids that must complete first']
        }}
    ],
    'fallback': {{
        'enabled': true,
        'strategy': 'fallback approach name',
        'steps': [
            {{
                'id': 'fallback_step_id',
                'type': 'function',
                'name': 'fallback_function_name',
                'parameters': {{
                    'value': 'parameter string'
                }},
                'extract': {{
                    'fields': {{
                        'info': 'jsonpath for basic info',
                        'stats': 'jsonpath for basic stats'
                    }}
                }},
                'depends_on': []
            }}
        ]
    }},
    'dependencies': {{
        'step2': ['step1'],
        'step3': ['step1', 'step2']
    }}
}}

SCHEMA VALIDATION REQUIREMENTS:

1. Type Field
- Must be exactly "function" for all steps
- No other values are allowed
- This applies to both main steps and fallback steps

2. Step IDs
- Must be unique across all steps
- Must be referenced correctly in depends_on and dependencies
- Should be descriptive of the step's purpose

3. Parameters
- Must use proper reference syntax: ${{step_id.field}}
- All referenced steps must exist
- All referenced fields must be defined in the extract.fields of the referenced step

4. Extract Fields
- Must use valid JSONPath syntax
- Should extract only necessary data
- Common patterns:
  - player_ids: "$.players[*].id"
  - names: "$.players[*].fullName"
  - stats: "$.stats[*].splits[*]"
  - info: For metadata and additional information
  - team_ids: "$.teams[*].id"
  - game_ids: "$.games[*].gamePk"
  - dates: For date-related fields
  - scores: For scoring information

5. Dependencies
- Must be properly mapped in the dependencies object
- Must only reference existing step IDs
- Must form a valid directed acyclic graph (no circular dependencies)
- Each dependency must have corresponding depends_on entries

6. Fallback Plan
- Must follow the same schema as main steps
- Must be properly structured with enabled flag and strategy
- Should provide simpler alternative when main plan fails
- Must maintain proper dependencies even in fallback

Choose the most relevant example pattern based on the current intent and modify it accordingly:

Make sure the returned plan:
1. Follows the schema exactly
2. Uses appropriate functions for the intent
3. Maintains proper data flow between steps
4. Includes comprehensive error handling
5. Preserves context through transformations
6. Uses correct reference syntax
7. Has valid JSONPath expressions
8. Contains all required fields
9. Maps dependencies correctly
10. Provides appropriate fallback options

Return the complete plan as a single valid JSON object strictly following this schema."""

        self.response_prompt = """You create natural, informative responses from MLB data.
            Return structured response with summary, details, and optional stats and media.
            Follow the schema exactly for all fields."""

        self.suggestion_prompt = """Generate 3-5 natural follow-up suggestions for an MLB query.
            Suggestions should be relevant to the current context and encourage exploration.
            Return exactly as a JSON array of strings."""

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

    async def analyze_intent(self, query: str) -> IntentAnalysis:
        """Enhanced intent analysis with structured schema"""
        try:
            result = await self.gemini.generate_with_fallback(
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
            valid_types = {"function": True, "endpoint": True}

            valid_methods = {method: True for method in available_endpoints}
            valid_methods.update({method: True for method in available_functions})

            # Define response schema
            response_schema = {
                "type": "object",
                "properties": {
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
                    "dependencies": {
                        "type": "object",
                        "properties": {
                            "step1": {"type": "array", "items": {"type": "string"}},
                            "step2": {"type": "array", "items": {"type": "string"}},
                        },
                    },
                },
                "required": ["steps", "dependencies"],
            }
            # Generate plan using LLM
            result = await self.gemini.generate_with_fallback(
                f"""{self.plan_prompt}\nCurrent Intent:\n{json.dumps(self.intent, indent=2)}""",
                generation_config=genai.GenerationConfig(
                    temperature=0.2,
                    response_mime_type="application/json",
                    response_schema=response_schema,
                ),
            )
            parsed_result = json.loads(result.text)
            print(parsed_result)

            # Process steps
            for step in parsed_result["steps"]:
                if step["type"] not in valid_types:
                    raise ValueError(f"Invalid step type: {step['type']}")
                if step["name"] not in valid_methods:
                    raise ValueError(f"Invalid step name: {step['name']}")

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

    def _create_fallback_plan(self, intent: IntentAnalysis) -> DataRetrievalPlan:
        """Create a simplified fallback plan when main plan creation fails"""

        # Basic fallback plan structure
        return {
            "steps": [
                {
                    "id": "basic_data",
                    "type": "function",
                    "name": "standings"
                    if intent["intent"]["type"] == "standings"
                    else "schedule",
                    "description": "Get basic MLB data",
                    "parameters": {
                        "value": "leagueId=103,104"
                        if intent["intent"]["type"] == "standings"
                        else "sportId=1"
                    },
                    "extract": {
                        "fields": {
                            "stats": "$.records[*].teamRecords[*]"
                            if intent["intent"]["type"] == "standings"
                            else "$.dates[*].games[*]",
                            "info": "$.records[*].division"
                            if intent["intent"]["type"] == "standings"
                            else "$.dates[*].date",
                        }
                    },
                    "depends_on": [],
                }
            ],
            "dependencies": {},
        }

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

            # Apply extraction if specified
            if "extract" in step:
                filtered_result = await self._process_extraction(
                    raw_result, step["extract"]
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

        result = await self.gemini.generate_with_fallback(
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
            print(params)
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
        """Execute MLB stats function with dynamic handling of parameters"""
        try:
            # Get function name and info
            function_name = step["name"]
            function_info = next(
                (f for f in self.functions if f["name"] == function_name), None
            )
            if not function_info:
                raise ValueError(f"Invalid function: {function_name}")

            # Resolve parameters
            resolved_params = await self._resolve_parameters(step, prior_results)

            # Generate execution code using LLM
            execution_code = await self._generate_execution_code(
                function_name=function_name,
                function_info=function_info,
                parameters=resolved_params,
            )
            sanitized_code = sanitize_code(execution_code)
            # print("sanitized code:", sanitized_code)

            repl_result = await self.repl(code=sanitized_code)
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

                return result

            except json.JSONDecodeError as e:
                raise ValueError(f"Failed to parse function result: {repl_result}")

        except Exception as e:
            print(f"Function execution error: {str(e)}")
            return None

    async def _generate_execution_code(
        self,
        function_name: str,
        function_info: Dict[str, Any],
        parameters: Dict[str, Any],
    ) -> str:
        """Generate Python code to execute the MLB stats function based on parameter analysis"""

        prompt = f"""Analyze these MLB Stats API function parameters and generate appropriate Python execution code.

    Function Information:
    {json.dumps(function_info, indent=2)}

    Resolved Parameters:
    {json.dumps(parameters, indent=2)}

    Requirements:
    1. Return Python code that executes statsapi.{function_name} with the given parameters
    2. If any parameter contains multiple values that should be processed separately:
    - Generate code that handles each value appropriately
    - Include logic to aggregate the results
    3. Include proper error handling for both single and multiple executions
    4. Return results in JSON format via print(json.dumps(result))
    5. Handle any parameter patterns found in the input
    6. Structure the code to work with the analysis tool environment

    Return only the Python code without any explanation or markdown.
    The code must be complete and runnable as is.

    Example of basic single-value execution:
        import statsapi
        import json

        try:
            result = statsapi.{function_name}(param1="value1")
            if result:
                print(json.dumps(result))
        except Exception as e:
            print(json.dumps({{"error": str(e)}}))

    Example of multi-value execution:
        import statsapi
        import json
        from concurrent.futures import ThreadPoolExecutor, as_completed

        def process_param(value):
            try:
                result = statsapi.{function_name}(param1=value)
                return {{"success": True, "value": value, "result": result}}
            except Exception as e:
                return {{"success": False, "value": value, "error": str(e)}}

    values = ["value1", "value2", "value3"]
    results = []

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(process_param, v) for v in values]
        for future in as_completed(futures):
            results.append(future.result())

    print(json.dumps(results))
    
    I want the returned code to be all indented one tab to the right
    """

        result = await self.gemini.generate_with_fallback(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.2, response_mime_type="text/plain"
            ),
        )

        # Clean and validate the generated code
        generated_code = result.text
        generated_code = generated_code.replace("```python", "").replace("```", "")
        #print("generated code:", generated_code)
        # Ensure the code has proper imports
        if "import statsapi" not in generated_code:
            generated_code = "import statsapi\nimport json\n" + generated_code

        return generated_code

    async def _execute_endpoint_step(
        self, deps: MLBDeps, step: Dict[str, Any], prior_results: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Execute MLB API endpoint"""
        try:
            # Get endpoint from parameters
            endpoint_name = step["name"] #["parameters"].get("value")
            endpoint_url = (await self._resolve_parameters(step, prior_results))["url"]
            if not endpoint_name:
                raise ValueError("No endpoint specified")

            """# Get endpoint info
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
            """
            # Make request
            print(endpoint_url)
            response = await deps.client.get(endpoint_url)  # request_info["url"]
            response.raise_for_status()
            result = response.json()

            # Process data extraction if specified
            if step.get("extract"):
                result = await self._process_extraction(result, step["extract"])

            """# Apply filtering if specified
            if step.get("filtering") and step["filtering"].lower() != "none":
                result = await self._apply_filtering(result, step["filtering"])"""

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
                - Extract fields specified in: {json.dumps(step.get("extract", {}), indent=2)}
                - Handle missing or null values gracefully
                - Return only the requested fields
                - Maintain original data types (numbers, strings, etc.)
                - Follow specified extraction paths exactly

                Return only the extracted data as valid JSON without any explanation."""

                        try:
                            extraction_result = await self.gemini.generate_with_fallback(
                                generation_config=genai.GenerationConfig(
                                    temperature=0.1,  # Low temperature for precise extraction
                                    response_mime_type="application/json",
                                ),
                            )

                            # Parse and validate LLM response
                            extracted_data = json.loads(extraction_result.text)

                            # Apply any specified filters
                            if step.get("extract", {}).get("filter"):
                                extracted_data = await self._apply_filtering(
                                    extracted_data, step["extract"]["filter"]
                                )

                            return extracted_data

                        except Exception as llm_error:
                            print(
                                f"LLM extraction failed: {str(llm_error)}, falling back to standard processing"
                            )
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
                result = await self.gemini.generate_with_fallback(
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
                result = await self.gemini.generate_with_fallback(
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
                {extraction_code}

                try:
                    with open('{data_file}', 'r') as f:
                        data = json.load(f)
                    
                    result = extract_data(data)
                    print(json.dumps(result))
                except Exception as e:
                    print(json.dumps({{"error": str(e)}}))
                    """
                    print("extraction code: ", execution_code)
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
        size_threshold: int = 100_000,  # Default threshold in characters
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
                result = await self.gemini.generate_with_fallback(
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
                result = await self.gemini.generate_with_fallback(
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

        result = await self.gemini.generate_with_fallback(
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
        self, step: Dict[str, Any], prior_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve API parameters and return complete URL for endpoints"""
        try:
            # Get function/endpoint info
            step_type = step.get("type")
            step_name = step.get("name")
            step_description = step.get("description")

            if step_type == "function":
                function_info = next(
                    (f for f in self.functions if f["name"] == step_name), None
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

    Step Description:
    {step_description}

    Requirements:
    1. Return ONLY the parameter string to go between parentheses in: statsapi.{step_name}()
    2. Replace any $referenced values with actual values from prior results
    3. Format according to function signature
    4. Include parameter names for clarity
    5. Handle missing optional parameters appropriately

    Example outputs:
    "teamId=143, season=2025"
    "personId=12345, group='[hitting,pitching]'"
    "gamePk=123456"

    Current date: {datetime.now().isoformat()}"""

            else:  # endpoint
                endpoint_info = self.endpoints.get(step_name)
                if not endpoint_info:
                    raise ValueError(f"Invalid endpoint: {step_name}")

                base_url = endpoint_info["url"]
                
                prompt = f"""Format MLB Stats API endpoint URL.

    Endpoint Info:
    {json.dumps(endpoint_info, indent=2)}

    Base URL:
    {base_url}

    Step Parameters:
    {json.dumps(step["parameters"], indent=2)}

    Prior Results Available:
    {json.dumps(prior_results, indent=2)}

    Step Description:
    {step_description}

    Current date: {datetime.now().isoformat()}

    Requirements:
    1. Return a complete, properly formatted URL with all parameters
    2. Replace any path parameters in URL (e.g. {{gamePk}})
    3. Add query parameters with proper encoding
    4. Replace any $referenced values with actual values from prior results
    5. Include all required parameters
    6. Format values according to API expectations
    7. Handle optional parameters appropriately

    Example good outputs:
    "https://statsapi.mlb.com/api/v1/teams/147/stats?stats=statSplits&statGroup=hitting&season=2024"
    "https://statsapi.mlb.com/api/v1/game/531060/feed/live?timecode=20240401_182458"

    Return only the complete URL as a string, no JSON formatting or explanations."""

            # Get resolution from Gemini
            result = await self.gemini.generate_with_fallback(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.1,  # Low temperature for precise formatting
                    response_mime_type="text/plain",
                ),
            )

            if step_type == "function":
                # For functions, return the raw parameter string
                return {"value": result.text.strip()}
            else:
                # For endpoints, return the complete URL
                return {"url": result.text.strip()}

        except Exception as e:
            print(f"Resolution error: {str(e)}")
            # Fall back to basic resolution
            if step_type == "function":
                return self._basic_parameter_resolution(step["parameters"], prior_results)
            else:
                # Basic URL construction for endpoints
                params = self._basic_parameter_resolution(step["parameters"], prior_results)
                endpoint_info = self.endpoints.get(step_name, {})
                base_url = endpoint_info.get("url", "")
                
                # Replace path parameters
                for key, value in params.items():
                    if f"{{{key}}}" in base_url:
                        base_url = base_url.replace(f"{{{key}}}", str(value))
                        del params[key]
                
                # Add remaining params as query parameters
                if params:
                    query_string = "&".join(f"{k}={v}" for k, v in params.items())
                    return {"url": f"{base_url}?{query_string}"}
                return {"url": base_url}
    def _basic_parameter_resolution(
        self, parameters: Dict[str, Any], prior_results: Dict[str, Any]
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
                "media": None,
            }
            # Create prompt only after preparing defaults
            prompt = f"""Create a natural, informative response from this MLB data.
                
            Query: {query}
            
            Intent:
            {json.dumps(self.intent)}
            
            Data:
            {json.dumps(data)}
            
            Return JSON with:
            - summary: A brief overview (1-2 sentences)
            - details: The complete data and analysis
            - media: Optional media content (if applicable)"""

            try:
                model_response = await self.gemini.generate_with_fallback(
                    prompt,
                    generation_config=genai.GenerationConfig(
                        response_mime_type="application/json"
                    ),
                )

                if not model_response or not hasattr(model_response, "text"):
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
                "media": None,
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
                elif hasattr(obj, "value"):  # Check if it's an Enum
                    return str(obj.value)
                return obj

            if response_data:
                sanitized_response = sanitize_enum_values(response_data)
            else:
                sanitized_response = {}

            context = ""
            if self.intent and sanitized_response:
                context = f"""
                    Intent: {json.dumps(self.intent)}
                    Data response: {json.dumps(sanitized_response, indent=2)}
                    """

            result = await self.gemini.generate_with_fallback(
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
            "Tell me about your favorite baseball moment",
        ]

    async def _generate_suggestions(self, response: Any) -> List[str]:
        """Generate contextual suggestions using LLM"""
        result = await self.gemini.generate_with_fallback(
            f"""{self.suggestion_prompt}
            
            Current intent:
            {json.dumps(self.intent)}
            
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

    async def process_message(
        self, deps: MLBDeps, message: str, context: Dict[str, Any]
    ) -> MLBResponse:
        """Enhanced message processing with media resolution"""
        try:
            # Get intent analysis
            self.intent = await self.analyze_intent(message)
            self.user_query = message
            # MLB-related query path
            if self.intent["is_mlb_related"] and self.intent["context"].get(
                "requires_data", True
            ):
                try:
                    # Execute main data plan
                    plan = await self.create_data_plan(self.intent)
                    data = await self.execute_plan(deps, plan)
                    response_data = await self.format_response(message, data)

                    # Add media resolution step
                    media = await self._resolve_media(deps, data, plan.get("steps", []))

                    if media:
                        response_data["media"] = media

                    chart = await self._resolve_chart(deps, data, plan.get("steps", []))

                    suggestions = await self._generate_suggestions(response_data)
                    conversation = await self.generate_conversation(
                        message, response_data
                    )

                    result = {
                        "message": response_data["summary"],
                        "conversation": conversation,
                        "data_type": self.intent["intent"],
                        "data": response_data["details"],
                        "context": {"intent": self.intent, "steps": plan.get("steps", [])},
                        "suggestions": suggestions,
                        "media": response_data.get("media"),
                        "chart": chart,
                    }
                    translated_result = await self.translate_response(
                        response=result,
                        target_language=context["user_info"]["language"],
                    )

                    return translated_result

                except Exception as execution_error:
                    print(f"Execution error: {str(execution_error)}")
                    return self._create_error_response(message, str(execution_error))

            else:
                conversation = await self.generate_conversation(message, self.intent)
                suggestions = self._get_default_suggestions()

                result = {
                    "message": self.intent.get(
                        "intent_description", "Let's talk baseball!"
                    ),
                    "conversation": conversation,
                    "data_type": "conversation",
                    "data": {},
                    "context": {"intent": self.intent},
                    "suggestions": suggestions,
                    "media": None,
                }

                translated_result = await self.translate_response(
                    response=result, target_language=context["user_info"]["language"]
                )

                return translated_result

        except Exception as e:
            print(f"Critical error in process_message: {str(e)}")
            return self._create_error_response(message, str(e))

    async def _get_search_parameters(
        self, intent: Dict[str, Any], data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get ready-to-use media URLs and relevant homerun keywords, with enhanced search capabilities
        that consider multiple fields beyond just the title.
        
        The function now considers:
        - Title text
        - Exit velocity ranges
        - Launch angle ranges
        - Distance thresholds
        - Player names extracted from titles
        """
        try:
            # Get a small sample of homerun data for context
            sample_homerun = self.homeruns.head(15).to_dict()

            # Enhanced prompt focusing on specific, meaningful search parameters
            media_prompt = """Based on this MLB context, generate a complete media plan with ready-to-use URLs and detailed, specific search parameters that capture the distinctive aspects of each home run.

            User query: {user_query}
            Intent: {intent}
            Data: {data}
            Sample Homerun Data: {homerun_sample}
            Available Media Sources: {media_sources}

            Return a JSON object with:
            1. direct_media: Array of ready-to-use media items with:
            - type: "image" or "video"
            - url: Complete URL (use templates below)
            - description: Natural description
            - metadata: Additional info (esp. for homeruns)

            2. homerun_search: Object containing:
            - keywords: Array of specific, distinctive search terms such as:
                * Situational context (e.g., "walk-off", "grand slam", "leadoff", "pinch-hit")
                * Game situation (e.g., "ties game", "takes lead", "extends lead")
                * Hit description (e.g., "line drive", "deep drive", "crushed", "monster shot")
                * Field location (e.g., "center field", "upper deck", "opposite field")
                * Notable achievements (e.g., "milestone", "career first", "record breaking")
                Do NOT include generic terms like "homerun", "homer", "hits", as these are implied
            - stats_criteria: Object with:
                - min_exit_velocity: Optional minimum exit velocity
                - max_exit_velocity: Optional maximum exit velocity
                - min_launch_angle: Optional minimum launch angle
                - max_launch_angle: Optional maximum launch angle
                - min_distance: Optional minimum distance
                - max_distance: Optional maximum distance
            - player_names: Array containing:
                * Batter's full name
                * Batter's common nicknames
                * Any other players mentioned in the context (e.g., runners who scored)

            URL Templates:
            - Player headshots: https://img.mlbstatic.com/mlb-photos/image/upload/d_people:generic:headshot:67:current.png/w_213,q_auto:best/v1/people/[player_id]/headshot/67/current
            - Team logos: https://www.mlbstatic.com/team-logos/[team_id].svg"""

            # Format prompt with actual data
            formatted_prompt = media_prompt.format(
                intent=json.dumps(intent, indent=2),
                data=json.dumps(data, indent=2),
                homerun_sample=json.dumps(sample_homerun, indent=2),
                media_sources=json.dumps(self.media_source, indent=2),
                user_query=self.user_query,
            )

            # Get media plan from LLM with enhanced schema
            result = await self.gemini.generate_with_fallback(
                formatted_prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.1,
                    response_mime_type="application/json",
                    response_schema={
                        "type": "object",
                        "properties": {
                            "direct_media": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "type": {"type": "string", "enum": ["image", "video"]},
                                        "url": {"type": "string"},
                                        "description": {"type": "string"},
                                        "metadata": {
                                            "type": "object",
                                            "properties": {
                                                "exit_velocity": {"type": "number"},
                                                "launch_angle": {"type": "number"},
                                                "distance": {"type": "number"},
                                                "player_id": {"type": "string"},
                                                "team_id": {"type": "string"},
                                                "game_date": {"type": "string"},
                                                "venue": {"type": "string"},
                                            },
                                        },
                                    },
                                    "required": ["type", "url", "description"],
                                },
                            },
                            "homerun_search": {
                                "type": "object",
                                "properties": {
                                    "keywords": {"type": "array", "items": {"type": "string"}},
                                    "stats_criteria": {
                                        "type": "object",
                                        "properties": {
                                            "min_exit_velocity": {"type": "number"},
                                            "max_exit_velocity": {"type": "number"},
                                            "min_launch_angle": {"type": "number"},
                                            "max_launch_angle": {"type": "number"},
                                            "min_distance": {"type": "number"},
                                            "max_distance": {"type": "number"},
                                        },
                                    },
                                    "player_names": {"type": "array", "items": {"type": "string"}},
                                },
                                "required": ["keywords", "stats_criteria", "player_names"],
                            },
                        },
                        "required": ["direct_media", "homerun_search"],
                    },
                ),
            )

            media_plan = json.loads(result.text)

            # Process homerun matches with enhanced criteria
            if media_plan["homerun_search"]:
                homerun_matches = []
                search_criteria = media_plan["homerun_search"]["stats_criteria"]
                
                for _, row in self.homeruns.iterrows():
                    # Check if the homerun meets all statistical criteria
                    if search_criteria:
                        if (
                            ("min_exit_velocity" in search_criteria and 
                            float(row["ExitVelocity"]) < search_criteria["min_exit_velocity"]) or
                            ("max_exit_velocity" in search_criteria and 
                            float(row["ExitVelocity"]) > search_criteria["max_exit_velocity"]) or
                            ("min_launch_angle" in search_criteria and 
                            float(row["LaunchAngle"]) < search_criteria["min_launch_angle"]) or
                            ("max_launch_angle" in search_criteria and 
                            float(row["LaunchAngle"]) > search_criteria["max_launch_angle"]) or
                            ("min_distance" in search_criteria and 
                            float(row["HitDistance"]) < search_criteria["min_distance"]) or
                            ("max_distance" in search_criteria and 
                            float(row["HitDistance"]) > search_criteria["max_distance"])
                        ):
                            continue

                    # Calculate text similarity scores
                    title_scores = [
                        difflib.SequenceMatcher(
                            None, str(row["title"]).lower(), keyword.lower()
                        ).ratio()
                        for keyword in media_plan["homerun_search"]["keywords"]
                    ]
                    
                    player_scores = [
                        difflib.SequenceMatcher(
                            None, str(row["title"]).lower(), player.lower()
                        ).ratio()
                        for player in media_plan["homerun_search"]["player_names"]
                    ]

                    # Use the best match from either keywords or player names
                    best_score = max(title_scores + player_scores) if player_scores else max(title_scores)

                    if best_score >= 0.55:  # Threshold for good matches
                        homerun_matches.append({
                            "type": "video",
                            "url": row["video"],
                            "title": row["title"],
                            "description": (
                                f"Incredible home run by {row['title'].split(' homers')[0]} with "
                                f"{row['ExitVelocity']} mph exit velocity, {row['LaunchAngle']}° "
                                f"launch angle, traveling {row['HitDistance']} feet!"
                            ),
                            "metadata": {
                                "exit_velocity": float(row["ExitVelocity"]),
                                "launch_angle": float(row["LaunchAngle"]),
                                "distance": float(row["HitDistance"]),
                                "year": int(row["season"]),
                            },
                        })

                # Sort matches by relevance and statistical impressiveness
                homerun_matches.sort(
                    key=lambda x: (
                        x["metadata"]["exit_velocity"] * 0.4 +  # Weight exit velocity
                        x["metadata"]["distance"] * 0.4 +      # Weight distance
                        x["metadata"]["launch_angle"] * 0.2    # Weight launch angle
                    ),
                    reverse=True
                )
                
                # Add top matches to media plan
                media_plan["direct_media"].extend(homerun_matches[:80])

            return media_plan

        except Exception as e:
            print(f"Error in media resolution: {str(e)}")
            return {"direct_media": [], "homerun_search": []}

    async def _resolve_chart(
        self, deps: MLBDeps, data: Dict[str, Any], steps: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze if data can be visualized as a chart and return appropriate chart configuration"""
        try:
            # Get chart documentation
            chart_specs = self.charts_docs

            # Create prompt for chart analysis
            chart_prompt = f"""Analyze this MLB data and determine if it can be visualized as a chart.

            Data:
            {json.dumps(data, indent=2)}

            Available Chart Types:
            {json.dumps(chart_specs, indent=2)}

            Return a JSON object with:
            1. requires_chart (boolean): Whether data should be displayed as a chart
            2. chart_type (string): One of: "area", "bar", "pie", "radar", "radial" (if requires_chart is true)
            3. variant (string): Specific variant of the chart type (if requires_chart is true)
            4. formatted_data (array): Data formatted according to chart's inputSchema (if requires_chart is true)
            5. title (string): Chart title (if requires_chart is true)
            6. description (string): Brief description of what the chart shows (if requires_chart is true)

            Focus on:
            - Only suggest chart if data structure matches a chart type's schema
            - Choose most appropriate chart type for data visualization
            - Format data to match exact schema requirements
            - Return null for chart-specific fields if requires_chart is false"""

            # Get chart recommendation from LLM
            result = await self.gemini.generate_with_fallback(
                chart_prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.2,
                    response_mime_type="application/json",
                    response_schema={
                        "type": "object",
                        "properties": {
                            "requires_chart": {"type": "boolean"},
                            "chart_type": {"type": "string"},
                            "variant": {"type": "string"},
                            "formatted_data": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "value": {"type": "number"},
                                        "label": {"type": "string"},
                                        "category": {"type": "string"},
                                        "date": {"type": "string"},
                                        "fill": {"type": "string"},
                                    },
                                },
                            },
                            "title": {"type": "string"},
                            "description": {"type": "string"},
                        },
                        "required": [
                            "requires_chart",
                            "title",
                            "description",
                            "formatted_data",
                            "variant",
                            "chart_type",
                        ],
                    },
                ),
            )

            chart_plan = json.loads(result.text)
            print("chart plan: ", chart_plan)
            # Validate chart data if chart is required
            if chart_plan.get("requires_chart", False):
                # Get chart type specs
                chart_type = chart_plan.get("chart_type")
                variant = chart_plan.get("variant")

                if not chart_type or not variant:
                    raise ValueError("Missing chart type or variant")

                chart_specs = self.charts_docs.get(chart_type, {})
                variant_specs = chart_specs.get("variants", {}).get(variant, {})

                if not variant_specs:
                    raise ValueError(
                        f"Invalid chart type {chart_type} or variant {variant}"
                    )

                # Validate data against schema
                input_schema = variant_specs.get("inputSchema", {})
                formatted_data = chart_plan.get("formatted_data", [])

                """if not self._validate_chart_data(formatted_data, input_schema):
                    raise ValueError("Formatted data does not match schema")"""

                # Add styling information
                chart_plan["styles"] = self.charts_docs["common"]["styling"]

                # Add component configurations
                chart_plan["components"] = {
                    "tooltip": {"variant": "default"},
                    "legend": {"position": "bottom", "alignment": "center"},
                }

                return chart_plan

            return {"requires_chart": False}

        except Exception as e:
            print(f"Error in chart resolution: {str(e)}")
            return {"requires_chart": False}

    def _validate_chart_data(
        self, data: List[Dict[str, Any]], schema: Dict[str, Any]
    ) -> bool:
        """Validate chart data against its schema"""
        try:
            if not isinstance(data, list):
                return False

            required_props = schema.get("items", {}).get("required", [])
            properties = schema.get("items", {}).get("properties", {})

            for item in data:
                # Check required properties
                if not all(prop in item for prop in required_props):
                    return False

                # Validate property types
                for prop, value in item.items():
                    expected_type = properties.get(prop)
                    if not expected_type:
                        continue

                    if expected_type == "string" and not isinstance(value, str):
                        return False
                    elif expected_type == "number" and not isinstance(
                        value, (int, float)
                    ):
                        return False

            return True

        except Exception as e:
            print(f"Error validating chart data: {str(e)}")
            return False

    async def _resolve_media(
        self, deps: MLBDeps, data: Dict[str, Any], steps: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Resolve media using optimized search and image analysis"""
        try:
            # Get ready-to-use media items and homerun search terms
            media_plan = await self._get_search_parameters(self.intent, data)
            print("meedia", media_plan)
            # Analyze and enhance media items with descriptions

            return media_plan.get("direct_media")

        except Exception as e:
            print(f"Media resolution error: {str(e)}")
            traceback.print_exc()
            return []

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
            result = await self.gemini.generate_with_fallback(
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

    async def translate_response(
        self, response: Any, target_language: str
    ) -> MLBResponse:
        """Translate human-readable fields in the MLB response while preserving structure and technical data."""
        if not target_language or target_language.lower() == "english":
            return response

        prompt = f"""Translate this MLB baseball response from English to {target_language}.
            The response is provided as JSON. Return the exact same JSON structure.
            
            Rules:
            1. Translate ONLY human-readable text like descriptions, messages, and titles
            2. DO NOT translate or modify:
            - Technical fields (ids, urls, types, flags)
            - Player names and team names
            - Statistics and numbers
            - Data structure or field names
            - Boolean flags or status indicators
            3. Preserve all JSON structure and formatting exactly
            
            Input Response:
            {json.dumps(response, indent=2)}
            
            Return the translated JSON with identical structure."""

        try:
            result = await self.gemini.generate_with_fallback(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.1, response_mime_type="application/json"
                ),
            )

            return json.loads(result.text)

        except Exception as e:
            print(f"Translation error: {str(e)}")
            return response


with open("src/core/constants/endpoints.json", "r") as f:
    endpoints_json = f.read()

with open("src/core/constants/mlb_functions.json", "r") as f:
    functions_json = f.read()

with open("src/core/constants/media_sources.json", "r") as f:
    media_json = f.read()

# Useful to return valid charts data
with open("src/core/constants/charts_docs.json", "r") as f:
    charts_json = f.read()

# Create agent instance
mlb_agent = MLBAgent(
    api_key=settings.GEMINI_API_KEY,
    endpoints_json=endpoints_json,
    functions_json=functions_json,
    media_json=media_json,
    charts_json=charts_json,
)
