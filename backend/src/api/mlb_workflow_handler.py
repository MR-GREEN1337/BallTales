from typing import Optional, Dict, Any, List
import statsapi
from enum import Enum
from datetime import datetime, timedelta
from loguru import logger
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
import json
from src.api.gemini_solid import GeminiSolid
import asyncio
import google.generativeai as genai
import pandas as pd
from difflib import SequenceMatcher

PLAYER_HEADSHOT_URL = "https://img.mlbstatic.com/mlb-photos/image/upload/d_people:generic:headshot:67:current.png/w_213,q_auto:best/v1/people/{player_id}/headshot/67/current.png"
TEAM_LOGO_URL = "https://www.mlbstatic.com/team-logos/{team_id}.svg"

class EntityType(str, Enum):
    PLAYER = "player"
    TEAM = "team"

@lru_cache(maxsize=1000)  # Cache player data
def lookup_player_cached(name: str):
    return statsapi.lookup_player(name)

@lru_cache(maxsize=1000)  # Cache player stats
def get_player_stats_cached(player_id: int):
    return statsapi.player_stat_data(
        player_id,
        group="[hitting,pitching]",
        type="career"
    )
class MLBWorkflowHandler:
    def __init__(self, entity_id: str, entity_type: EntityType, chart_docs: str):
        self.chart_docs = json.loads(chart_docs)
        self.homeruns = pd.read_csv("src/core/constants/mlb_homeruns.csv")
        self.entity_id = int(entity_id)
        self.entity_type = entity_type
        self.gemini = GeminiSolid()
        self.workflows = {
            # Team workflows
            "_api_team_championships": self._get_team_championships,
            "_api_team_roster_all-time": self._get_team_roster_all_time,
            "_api_team_stats": self._get_team_stats,
            "_api_team_roster_current": self._get_team_roster_current,
            "_api_team_games_recent": self._get_team_recent_games,
            # Player workflows
            "_api_player_stats": self._get_player_career_stats,
            "_api_player_highlights": self._get_player_highlights,
            "_api_player_games_recent": self._get_player_recent_games,
            "_api_player_homeruns": self._get_player_homeruns,
            "_api_player_awards": self._get_player_awards,
        }

    def _get_team_championships(self) -> Dict[str, Any]:
        """Get team's championship history."""
        try:
            # Get team info directly using the teams endpoint
            team_data = statsapi.get("team", {"teamId": self.entity_id})
            print(team_data)
            team_info = team_data['teams'][0]
            print(team_info)
            
            return team_info
        except Exception as e:
            logger.error(f"Error fetching team championships: {str(e)}")
            raise

    def _get_team_roster_all_time(self) -> Dict[str, Any]:
        """Get historical roster information."""
        try:
            historical_players = statsapi.roster(
                self.entity_id, 
                rosterType="allTime"
            )
            
            list_history = historical_players.split('\n')
            player_names = [' '.join(player.split(' ')[-2:]).strip() 
                        for player in list_history if player.strip()]
            
            formatted_players = []
            
            # Process players in batches using ThreadPoolExecutor
            with ThreadPoolExecutor(max_workers=10) as executor:
                def process_player(name):
                    try:
                        player_data = lookup_player_cached(name)
                        if not player_data:
                            return None

                        return {
                            "imageUrl": PLAYER_HEADSHOT_URL.format(player_id=player_data[0]['id']),
                            "name": name,
                        }
                    except Exception as e:
                        logger.error(f"Error processing player {name}: {str(e)}")
                        return None

                # Process players in parallel
                results = list(executor.map(process_player, player_names))
                formatted_players = [r for r in results if r is not None]

            return {
                "team_id": self.entity_id,
                "total_players": len(formatted_players),
                "players": formatted_players
            }
            
        except Exception as e:
            logger.error(f"Error fetching historical roster: {str(e)}")
            raise

    async def _get_team_stats(self) -> Dict[str, Any]:
        """Get comprehensive team statistics."""
        try:
            current_season = datetime.now().year
            team_stats = statsapi.team_stats(self.entity_id, season=current_season)
            
            # Format stats data for Gemini analysis
            stats_data = {
                "team_id": self.entity_id,
                "season": current_season,
                "stats": {
                    "batting": {
                        "avg": float(team_stats["batting"]["avg"]),
                        "runs": team_stats["batting"]["runs"],
                        "home_runs": team_stats["batting"]["homeRuns"],
                        "ops": float(team_stats["batting"]["ops"]),
                    },
                    "pitching": {
                        "era": float(team_stats["pitching"]["era"]),
                        "whip": float(team_stats["pitching"]["whip"]),
                        "strikeouts": team_stats["pitching"]["strikeOuts"],
                        "saves": team_stats["pitching"]["saves"],
                    },
                    "fielding": {
                        "fielding_percentage": float(team_stats["fielding"]["fielding_percentage"]),
                        "errors": team_stats["fielding"]["errors"],
                    }
                }
            }

            # Create prompt for Gemini
            formatted_prompt = f"""Analyze this MLB team statistics data and determine how to best visualize it.

            Data:
            {json.dumps(stats_data, indent=2)}

            Create a chart configuration that effectively visualizes these baseball statistics.
            Return a JSON structure with these fields:

            1. requires_chart: true
            2. chart_type: "bar" (for column charts) or "radar" (for multi-stat comparison)
            3. variant: "basic" or "grouped"
            4. formatted_data: Array of objects with these fields:
            - category: The stat category (e.g. "Batting - Home Runs")
            - value: The numerical value
            - label: Display label
            5. title: Clear descriptive title
            6. description: Brief explanation of what the chart shows

            Consider:
            - Choose between bar chart (for absolute values) or radar chart (for relative performance)
            - Group related statistics together
            - Ensure data is properly formatted for visualization
            - Include clear labels and descriptions
            """

            # Generate chart configuration using Gemini
            result = await self.gemini.generate_with_fallback(
                formatted_prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.1,
                    response_mime_type="application/json",
                )
            )
            
            # Parse Gemini response
            chart_config = json.loads(result.text)
            
            # Add styling information
            chart_config["styles"] = self.charts_docs["common"]["styling"]
            
            # Add component configurations
            chart_config["components"] = {
                "tooltip": {"variant": "default"},
                "legend": {"position": "bottom", "alignment": "center"},
            }

            return chart_config
                
        except Exception as e:
            logger.error(f"Error fetching team stats: {str(e)}")
            raise

    def _get_team_roster_current(self) -> Dict[str, Any]:
        """Get current team roster."""
        try:
            roster = statsapi.roster(self.entity_id)
            logger.info(roster)
            player_names = [' '.join(player.split(' ')[-2:]).strip() 
                        for player in roster.split('\n') if player.strip()]
            logger.info(player_names)
            players_data = []
            def process_player(name):
                try:
                    player_data = lookup_player_cached(name)
                    if not player_data:
                        return None

                    return {
                        "imageUrl": PLAYER_HEADSHOT_URL.format(player_id=player_data[0]['id']),
                        "name": name,
                    }
                except Exception as e:
                    logger.error(f"Error processing player {name}: {str(e)}")
                    return None
            for player_name in player_names:
                players_data.append(process_player(player_name))


            return {
                "team_id": self.entity_id,
                "total_players": len(players_data),
                "players": players_data
            }
            
        except Exception as e:
            logger.error(f"Error fetching historical roster: {str(e)}")
            raise

    def _get_team_recent_games(self) -> Dict[str, Any]:
        """Get team's recent game results."""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=14)
            
            schedule = statsapi.schedule(
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d"),
                team=self.entity_id
            )

            formatted_games = []
            for game in schedule:
                formatted_games.append({
                    "game_id": game["game_id"],
                    "date": game["game_date"],
                    "opponent": game["away_name"] 
                              if game["home_id"] == self.entity_id 
                              else game["home_name"],
                    "home_away": "home" 
                               if game["home_id"] == self.entity_id 
                               else "away",
                    "result": game["summary"],
                    "score": f"{game['home_score']}-{game['away_score']}",
                })

            return {
                "team_id": self.entity_id,
                "period": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
                "games": formatted_games
            }
        except Exception as e:
            logger.error(f"Error fetching recent games: {str(e)}")
            raise

    def _get_player_career_stats(self) -> Dict[str, Any]:
        """Get comprehensive player career statistics."""
        try:
            stat_data = statsapi.player_stat_data(
                self.entity_id,
                group="[hitting,pitching,fielding]",
                type="career"
            )
            
            career_stats = {
                "player_id": self.entity_id,
                "career_stats": {
                    "batting": {},
                    "pitching": {},
                    "fielding": {}
                }
            }

            # Process hitting stats
            if "hitting" in stat_data:
                career_stats["career_stats"]["batting"] = {
                    "games": stat_data["hitting"].get("gamesPlayed", 0),
                    "avg": stat_data["hitting"].get("avg", ".000"),
                    "home_runs": stat_data["hitting"].get("homeRuns", 0),
                    "rbi": stat_data["hitting"].get("rbi", 0),
                    "ops": stat_data["hitting"].get("ops", ".000"),
                    "hits": stat_data["hitting"].get("hits", 0),
                    "runs": stat_data["hitting"].get("runs", 0),
                    "stolen_bases": stat_data["hitting"].get("stolenBases", 0),
                    "doubles": stat_data["hitting"].get("doubles", 0),
                    "triples": stat_data["hitting"].get("triples", 0),
                    "strikeouts": stat_data["hitting"].get("strikeOuts", 0),
                    "walks": stat_data["hitting"].get("baseOnBalls", 0)
                }

            # Process pitching stats
            if "pitching" in stat_data:
                career_stats["career_stats"]["pitching"] = {
                    "games": stat_data["pitching"].get("gamesPlayed", 0),
                    "era": stat_data["pitching"].get("era", "0.00"),
                    "wins": stat_data["pitching"].get("wins", 0),
                    "losses": stat_data["pitching"].get("losses", 0),
                    "saves": stat_data["pitching"].get("saves", 0),
                    "innings_pitched": stat_data["pitching"].get("inningsPitched", "0.0"),
                    "strikeouts": stat_data["pitching"].get("strikeOuts", 0),
                    "whip": stat_data["pitching"].get("whip", "0.00")
                }

            # Process fielding stats
            if "fielding" in stat_data:
                career_stats["career_stats"]["fielding"] = {
                    "games": stat_data["fielding"].get("gamesPlayed", 0),
                    "fielding_percentage": stat_data["fielding"].get("fielding", ".000"),
                    "assists": stat_data["fielding"].get("assists", 0),
                    "putouts": stat_data["fielding"].get("putOuts", 0),
                    "errors": stat_data["fielding"].get("errors", 0)
                }

            return career_stats
        except Exception as e:
            logger.error(f"Error fetching player career stats: {str(e)}")
            raise

    def _get_player_highlights(self) -> Dict[str, Any]:
        """Get player's name and prepare highlight search query."""
        try:
            # Get player info
            player_info = statsapi.lookup_player(self.entity_id)
            
            if not player_info or len(player_info) == 0:
                raise ValueError(f"Player with ID {self.entity_id} not found")
            
            # Extract player name and active status
            player = player_info[0]
            full_name = f"{player.get('firstName', '')} {player.get('lastName', '')}".strip()
            is_active = player.get('active', False)
            primary_position = player.get('primaryPosition', {}).get('abbreviation', '')
            
            # Format data for frontend
            search_query = f"{full_name} MLB highlights"
            search_url = f"https://www.youtube.com/results?search_query={'+'.join(search_query.split())}"
            
            # Get basic player stats for context
            stats = statsapi.player_stat_data(
                self.entity_id,
                group="[hitting,pitching]",
                type="career"
            )
            
            # Determine if player is pitcher or position player
            is_pitcher = primary_position == 'P'
            
            # Get relevant career stats
            career_stats = {}
            if "hitting" in stats and not is_pitcher:
                hitting_stats = stats["hitting"]
                career_stats = {
                    "avg": hitting_stats.get("avg", ".000"),
                    "home_runs": hitting_stats.get("homeRuns", 0),
                    "hits": hitting_stats.get("hits", 0),
                    "rbi": hitting_stats.get("rbi", 0)
                }
            elif "pitching" in stats and is_pitcher:
                pitching_stats = stats["pitching"]
                career_stats = {
                    "era": pitching_stats.get("era", "0.00"),
                    "wins": pitching_stats.get("wins", 0),
                    "strikeouts": pitching_stats.get("strikeOuts", 0),
                    "saves": pitching_stats.get("saves", 0)
                }

            return {
                "player_id": self.entity_id,
                "player_info": {
                    "name": full_name,
                    "position": primary_position,
                    "active": is_active,
                    "career_stats": career_stats
                },
                "highlight_info": {
                    "search_query": search_query,
                    "search_url": search_url
                }
            }
            
        except Exception as e:
            logger.error(f"Error fetching player highlights: {str(e)}")
            raise
        
    def _get_player_recent_games(self) -> Dict[str, Any]:
        """Get player's recent game performances."""
        try:
            stat_data = statsapi.player_stat_data(
                self.entity_id,
                group="[hitting,pitching]",
                type="lastTen"
            )
            
            formatted_games = []
            
            # Process hitting games
            if "hitting" in stat_data:
                for game in stat_data["hitting"]:
                    game_data = {
                        "date": game["date"],
                        "opponent": game["opponent"],
                        "batting": {
                            "hits": game.get("hits", 0),
                            "at_bats": game.get("atBats", 0),
                            "home_runs": game.get("homeRuns", 0),
                            "rbi": game.get("rbi", 0),
                            "walks": game.get("baseOnBalls", 0),
                            "strikeouts": game.get("strikeOuts", 0),
                            "avg": game.get("avg", ".000")
                        }
                    }
                    formatted_games.append(game_data)

            # Process pitching games
            if "pitching" in stat_data:
                for game in stat_data["pitching"]:
                    game_data = {
                        "date": game["date"],
                        "opponent": game["opponent"],
                        "pitching": {
                            "innings": game.get("inningsPitched", "0.0"),
                            "hits": game.get("hits", 0),
                            "runs": game.get("runs", 0),
                            "earned_runs": game.get("earnedRuns", 0),
                            "walks": game.get("baseOnBalls", 0),
                            "strikeouts": game.get("strikeOuts", 0),
                            "era": game.get("era", "0.00")
                        }
                    }
                    formatted_games.append(game_data)

            return {
                "player_id": self.entity_id,
                "total_games": len(formatted_games),
                "recent_games": sorted(formatted_games, key=lambda x: x["date"], reverse=True)
            }
        except Exception as e:
            logger.error(f"Error fetching player recent games: {str(e)}")
            raise

    def _get_player_homeruns(self) -> Dict[str, Any]:
        """Get comprehensive home run statistics for a player."""
        try:
            # Get player info
            player = statsapi.lookup_player(self.entity_id)[0]
            player_name = player['fullName']
            
            # Use difflib to find matching home runs
            def calculate_similarity(row):
                hr_name = str(row['title']).split(' homers')[0]  # Using 'title' instead of 'description'
                return SequenceMatcher(None, hr_name.lower(), player_name.lower()).ratio()
            
            # Add similarity scores and filter matches
            self.homeruns['similarity'] = self.homeruns.apply(calculate_similarity, axis=1)
            matching_hrs = self.homeruns[self.homeruns['similarity'] > 0.8]
            
            # Convert matching rows to list of dictionaries
            homeruns_list = []
            for _, hr in matching_hrs.iterrows():
                homeruns_list.append({
                    "year": int(hr['season']),  # Changed from 'year' to 'season'
                    "description": hr['title'],  # Changed from 'description' to 'title'
                    "metadata": {
                        "exit_velocity": float(hr['ExitVelocity']),  # Changed to match CSV column name
                        "launch_angle": float(hr['LaunchAngle']),    # Changed to match CSV column name
                        "distance": float(hr['HitDistance'])         # Changed to match CSV column name
                    },
                    "video": {
                        "type": "video",
                        "url": hr['video'],  # Changed from 'video_url' to 'video'
                        "title": hr['title']
                    }
                })
            
            # Calculate metrics using pandas with updated column names
            metrics = {
                "avg_distance": float(matching_hrs['HitDistance'].mean()) if not matching_hrs.empty else 0,
                "avg_exit_velocity": float(matching_hrs['ExitVelocity'].mean()) if not matching_hrs.empty else 0,
                "avg_launch_angle": float(matching_hrs['LaunchAngle'].mean()) if not matching_hrs.empty else 0,
                "longest_homerun": float(matching_hrs['HitDistance'].max()) if not matching_hrs.empty else 0,
                "highest_exit_velocity": float(matching_hrs['ExitVelocity'].max()) if not matching_hrs.empty else 0
            }
            
            result = {
                "player_id": self.entity_id,
                "player_name": player_name,
                "total_homeruns": len(matching_hrs),
                "homeruns": sorted(homeruns_list, key=lambda x: x["metadata"]["distance"], reverse=True),
                "metrics": metrics
            }
            logger.info(result)
            return result
            
        except Exception as e:
            logger.error(f"Error fetching player home runs: {str(e)}")
            raise

    async def _get_player_awards(self) -> Dict[str, Any]:
        """Get player's statistical achievements and milestones."""
        try:
            # Get career and yearly stats
            career_data = statsapi.player_stat_data(
                self.entity_id,
                group="[hitting,pitching]",
                type="career"
            )
            yearly_data = statsapi.player_stat_data(
                self.entity_id,
                group="[hitting,pitching]",
                type="yearByYear"
            )
            
            # Extract relevant stats
            player_stats = {
                "player_info": {
                    "name": f"{career_data['first_name']} {career_data['last_name']}",
                    "position": career_data['position'],
                    "mlb_debut": career_data['mlb_debut']
                },
                "career_stats": career_data['stats'][0]['stats'],  # Career hitting stats
                "yearly_stats": {
                    stat['season']: stat['stats']
                    for stat in yearly_data['stats']
                    if stat['type'] == 'yearByYear'
                }
            }
            
            # Create prompt for Gemini
            formatted_prompt = f"""Analyze these MLB player statistics and generate a structured achievement summary as JSON.
    Focus on career milestones, exceptional seasons, and notable records.
    Return the data in this exact JSON structure:

    {{
    "player_info": {{
        "name": "full_name",
        "position": "position",
        "mlb_debut": "date"
    }},
    "career_achievements": [
        {{
        "type": "milestone",
        "description": "achievement description",
        "value": "numerical_value",
        "year": "year_achieved (if applicable)"
        }}
    ],
    "notable_seasons": [
        {{
        "year": "season_year",
        "achievements": [
            {{
            "type": "record/achievement type",
            "description": "specific achievement",
            "value": "numerical_value"
            }}
        ]
        }}
    ],
    "records": [
        {{
        "type": "record_type",
        "description": "record description",
        "value": "record_value",
        "year": "year_set"
        }}
    ]
    }}

    Consider these thresholds for achievements:
    - Career milestones: 300+ HR, 700+ RBI, .400+ OBP, 1.000+ OPS
    - Season highlights: 40+ HR, .300+ AVG, 1.000+ OPS, 100+ RBI
    - Records: AL/MLB records, franchise records, season bests

    Parse this player data and return only verified achievements:
    {json.dumps(player_stats, indent=2)}"""

            # Generate response using Gemini
            result = await self.gemini.generate_with_fallback(
                formatted_prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.1,
                    response_mime_type="application/json",
                )
            )
            
            # Parse and return JSON response
            return json.loads(result.text)
            
        except Exception as e:
            logger.error(f"Error fetching player achievements: {str(e)}")
            raise
        
    async def process_workflow(self, endpoint: str) -> Dict[str, Any]:
        """Process the workflow based on the endpoint."""
        try:
            normalized_endpoint = endpoint.replace("*", "_")
            if normalized_endpoint not in self.workflows:
                raise ValueError(f"Unsupported endpoint: {endpoint}")

            if (normalized_endpoint.startswith("_api_team_") and 
                self.entity_type != EntityType.TEAM):
                raise ValueError("Team endpoint cannot be used with player entity")
            
            if (normalized_endpoint.startswith("_api_player_") and 
                self.entity_type != EntityType.PLAYER):
                raise ValueError("Player endpoint cannot be used with team entity")

            workflow = self.workflows[normalized_endpoint]
            return await workflow() if asyncio.iscoroutinefunction(workflow) else workflow()

        except Exception as e:
            logger.error(f"Workflow processing failed: {str(e)}")
            raise