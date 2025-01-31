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
        player_id, group="[hitting,pitching]", type="career"
    )


@lru_cache(maxsize=100)
def get_team_stats_cached(team_id: int, season: Optional[int] = None) -> Dict[str, Any]:
    """Cached wrapper for getting team stats using league_leader_data"""
    try:
        # Get latest available season if none specified or future date
        if season is None or season > datetime.now().year:
            season = datetime.now().year - 1  # Use previous year for reliability

        # Get batting stats using league_leader_data
        batting_data = statsapi.league_leader_data(
            "homeRuns,runs,battingAverage,onBasePlusSlugging,hits,rbi,stolenBases",
            season=season,
            leagueId=None,  # Include all leagues
            limit=50,  # Get enough players to find team members
        )

        # Get pitching stats
        pitching_data = statsapi.league_leader_data(
            "earnedRunAverage,strikeouts,saves,whip,completeGames",
            season=season,
            leagueId=None,
            limit=50,
            statGroup="pitching",
        )

        return {"batting": batting_data, "pitching": pitching_data, "season": season}

    except Exception as e:
        logger.error(f"Error in get_team_stats_cached: {str(e)}")
        raise


class MLBWorkflowHandler:
    def __init__(self, entity_id: str, entity_type: EntityType, chart_docs: str):
        self.chart_docs = json.loads(chart_docs)["charts"]
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

    async def _get_team_championships(self) -> Dict[str, Any]:
        """Get comprehensive team championship history using Gemini analysis."""
        try:
            # Get basic team info
            team_data = statsapi.get("team", {"teamId": self.entity_id})
            team_info = team_data["teams"][0]
            first_year = int(team_info.get("firstYearOfPlay", datetime.now().year))
            
            # Get team's awards history
            awards_data = statsapi.get("awards", {
                "sportId": 1,
                "teamId": self.entity_id,
            })

            # Create prompt for Gemini
            formatted_prompt = f"""Analyze this MLB team's awards and achievements data to generate a comprehensive championship history.
            
            Team Info:
            {json.dumps(team_info, indent=2)}
            
            Awards Data:
            {json.dumps(awards_data, indent=2)}
            
            Create a JSON response with the following structure:
            {{
                "championships": {{
                    "world_series": [sorted years, newest first],
                    "league_pennants": [sorted years, newest first],
                    "division_titles": [sorted years, newest first],
                    "wild_cards": [sorted years, newest first]
                }},
                "historical_achievements": [
                    {{
                        "year": int,
                        "achievement": "description",
                        "category": "championship_type"
                    }}
                ],
                "stats": {{
                    "total_world_series": int,
                    "total_pennants": int,
                    "total_division_titles": int,
                    "total_wild_cards": int,
                    "last_world_series": int or null,
                    "last_pennant": int or null,
                    "last_division_title": int or null,
                    "championship_drought": int (years since last WS or founding)
                }}
            }}
            
            Rules:
            1. Include all championships under correct categories
            2. Sort years in descending order
            3. Categories: World Series, League Pennants (AL/NL), Division Titles, Wild Cards
            4. Historical achievements should note significant milestones
            5. Calculate championship drought from last WS or team founding
            """

            # Generate analysis using Gemini
            result = await self.gemini.generate_with_fallback(
                formatted_prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.1,
                    response_mime_type="application/json",
                ),
                model_name="gemini-2.0-flash-exp"
            )

            # Parse Gemini response and combine with team info
            championship_data = json.loads(result.text)

            return championship_data

        except Exception as e:
            logger.error(f"Error fetching team championships: {str(e)}")
            raise
    def _process_roster_parallel(
        self, roster_str: str, max_workers: int = 10
    ) -> Dict[str, Any]:
        """
        Process roster data in parallel using ThreadPoolExecutor.

        Args:
            roster_str: Raw roster string from statsapi
            max_workers: Maximum number of parallel workers

        Returns:
            Dictionary containing processed roster data
        """
        try:
            # Parse player names from roster string
            player_names = [
                " ".join(player.split(" ")[-2:]).strip()
                for player in roster_str.split("\n")
                if player.strip()
            ]

            formatted_players = []

            # Process players in batches using ThreadPoolExecutor
            with ThreadPoolExecutor(max_workers=max_workers) as executor:

                def process_player(name):
                    try:
                        player_data = lookup_player_cached(name)
                        if not player_data:
                            return None

                        return {
                            "imageUrl": PLAYER_HEADSHOT_URL.format(
                                player_id=player_data[0]["id"]
                            ),
                            "name": name,
                        }
                    except Exception as e:
                        logger.error(f"Error processing player {name}: {str(e)}")
                        return None

                # Process players in parallel and filter out None results
                formatted_players = list(
                    filter(None, executor.map(process_player, player_names))
                )

            return {
                "team_id": self.entity_id,
                "total_players": len(formatted_players),
                "players": formatted_players,
            }

        except Exception as e:
            logger.error(f"Error processing roster: {str(e)}")
            raise

    def _get_team_roster_all_time(self) -> Dict[str, Any]:
        """Get historical roster information."""
        try:
            historical_players = statsapi.roster(self.entity_id, rosterType="allTime")
            return self._process_roster_parallel(historical_players)
        except Exception as e:
            logger.error(f"Error fetching historical roster: {str(e)}")
            raise

    def _get_team_roster_current(self) -> Dict[str, Any]:
        """Get current team roster."""
        try:
            current_roster = statsapi.roster(self.entity_id)
            return self._process_roster_parallel(current_roster)
        except Exception as e:
            logger.error(f"Error fetching current roster: {str(e)}")
            raise

    async def _get_team_stats(self) -> Dict[str, Any]:
        """Get comprehensive team statistics using cached league leader data."""
        try:
            # Get stats for most recent completed season
            team_data = get_team_stats_cached(self.entity_id)
            actual_season = team_data["season"]

            # Format stats data for Gemini analysis
            stats_data = {
                "team_id": self.entity_id,
                "season": actual_season,
                "stats": {
                    "batting": team_data["batting"],
                    "pitching": team_data["pitching"],
                },
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
            5. title: Clear descriptive title that includes the {actual_season} season
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
                ),
            )

            # Parse Gemini response
            chart_config = json.loads(result.text)

            # Add styling information
            chart_config["styles"] = self.chart_docs["common"]["styling"]

            # Add component configurations
            chart_config["components"] = {
                "tooltip": {"variant": "default"},
                "legend": {"position": "bottom", "alignment": "center"},
            }

            return chart_config

        except Exception as e:
            logger.error(f"Error fetching team stats: {str(e)}")
            raise

    def _get_team_recent_games(self) -> Dict[str, Any]:
        """Get team's recent and upcoming game results."""
        try:
            # Get date range for past 14 days and upcoming 14 days
            end_date = datetime.now() + timedelta(days=7*4*3)
            start_date = datetime.now() - timedelta(days=7*4*3)

            schedule = statsapi.schedule(
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d"),
                team=self.entity_id,
            )

            # Cache for team lookups to avoid multiple calls for same team
            team_logo_cache = {}
            
            def get_opponent_logo(opponent_id: int) -> str:
                """Helper function to get opponent logo URL with caching."""
                if opponent_id not in team_logo_cache:
                    team_logo_cache[opponent_id] = TEAM_LOGO_URL.format(team_id=opponent_id)
                return team_logo_cache[opponent_id]

            recent_games = []
            upcoming_games = []
            current_time = datetime.now()

            for game in schedule:
                game_date = datetime.strptime(game['game_date'], "%Y-%m-%d")
                opponent_id = game["away_id"] if game["home_id"] == self.entity_id else game["home_id"]
                
                game_data = {
                    "game_id": game["game_id"],
                    "date": game["game_date"],
                    "opponent": game["away_name"] if game["home_id"] == self.entity_id else game["home_name"],
                    "opponent_image_url": get_opponent_logo(opponent_id),
                    "home_away": "home" if game["home_id"] == self.entity_id else "away",
                    "status": game["status"],
                    "venue": game.get("venue_name", ""),
                    "time": game.get("game_time", ""),
                }

                # Add score for completed games
                if game["status"] == "Final":
                    game_data.update({
                        "result": game["summary"],
                        "score": f"{game['home_score']}-{game['away_score']}"
                    })
                # Add scheduled info for upcoming games
                else:
                    game_data.update({
                        "probable_pitcher": game.get("probable_pitchers", {}).get(
                            "home" if game["home_id"] == self.entity_id else "away", 
                            "TBD"
                        ),
                    })

                # Sort into recent or upcoming based on game date
                if game_date < current_time:
                    recent_games.append(game_data)
                else:
                    upcoming_games.append(game_data)

            return {
                "team_id": self.entity_id,
                "period": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
                "recent_games": sorted(recent_games, key=lambda x: x["date"], reverse=True),
                "upcoming_games": sorted(upcoming_games, key=lambda x: x["date"])
            }
        except Exception as e:
            logger.error(f"Error fetching recent and upcoming games: {str(e)}")
            raise
    async def _get_player_career_stats(self) -> Dict[str, Any]:
        """Get comprehensive player career statistics and generate visualization configuration."""
        try:
            stat_data = statsapi.player_stat_data(
                self.entity_id, group="[hitting,pitching,fielding]", type="career"
            )

            # Create prompt for Gemini
            formatted_prompt = f"""Analyze this MLB player's career statistics data and determine how to best visualize it.

            Data:
            {json.dumps(stat_data, indent=2)}

            Create a chart configuration that effectively visualizes these baseball statistics.
            Return a JSON structure with these fields:

            1. requires_chart: true
            2. chart_type: Choose from:
            - "bar" (for comparing numerical stats)
            - "radar" (for displaying multiple related metrics)
            - "pie" (for showing proportions)
            3. variant: "basic" or "grouped"
            4. formatted_data: Array of objects with these fields:
            - category: The stat category (e.g. "Home Runs")
            - value: The numerical value
            - label: Display label
            5. title: Clear descriptive title
            6. description: Brief explanation of what the chart shows

            Consider:
            - Choose the most appropriate chart type for the player's primary role (pitcher vs position player)
            - Group related statistics together
            - Ensure data is properly formatted for visualization
            - Include clear labels and descriptions
            - For pitchers, focus on ERA, WHIP, strikeouts, etc.
            - For position players, focus on batting average, home runs, RBI, etc.
            """

            # Generate chart configuration using Gemini
            result = await self.gemini.generate_with_fallback(
                formatted_prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.1,
                    response_mime_type="application/json",
                ),
            )

            # Parse Gemini response
            chart_config = json.loads(result.text)

            # Add styling information
            chart_config["styles"] = self.chart_docs["common"]["styling"]

            # Add component configurations
            chart_config["components"] = {
                "tooltip": {"variant": "default"},
                "legend": {"position": "bottom", "alignment": "center"},
            }

            # Combine stats and chart configuration
            final_response = {"data": chart_config}

            return final_response

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
            full_name = (
                f"{player.get('firstName', '')} {player.get('lastName', '')}".strip()
            )
            is_active = player.get("active", False)
            primary_position = player.get("primaryPosition", {}).get("abbreviation", "")

            # Format data for frontend
            search_query = f"{full_name} MLB highlights"
            search_url = f"https://www.youtube.com/results?search_query={'+'.join(search_query.split())}"

            # Get basic player stats for context
            stats = statsapi.player_stat_data(
                self.entity_id, group="[hitting,pitching]", type="career"
            )

            # Determine if player is pitcher or position player
            is_pitcher = primary_position == "P"

            # Get relevant career stats
            career_stats = {}
            if "hitting" in stats and not is_pitcher:
                hitting_stats = stats["hitting"]
                career_stats = {
                    "avg": hitting_stats.get("avg", ".000"),
                    "home_runs": hitting_stats.get("homeRuns", 0),
                    "hits": hitting_stats.get("hits", 0),
                    "rbi": hitting_stats.get("rbi", 0),
                }
            elif "pitching" in stats and is_pitcher:
                pitching_stats = stats["pitching"]
                career_stats = {
                    "era": pitching_stats.get("era", "0.00"),
                    "wins": pitching_stats.get("wins", 0),
                    "strikeouts": pitching_stats.get("strikeOuts", 0),
                    "saves": pitching_stats.get("saves", 0),
                }

            return {
                "player_id": self.entity_id,
                "player_info": {
                    "name": full_name,
                    "position": primary_position,
                    "active": is_active,
                    "career_stats": career_stats,
                },
                "highlight_info": {
                    "search_query": search_query,
                    "search_url": search_url,
                },
            }

        except Exception as e:
            logger.error(f"Error fetching player highlights: {str(e)}")
            raise

    def _get_player_recent_games(self) -> Dict[str, Any]:
        """Get player's recent and upcoming game performances."""
        try:
            # Get basic player info including team ID
            player_info = statsapi.lookup_player(self.entity_id)[0]
            team_id = player_info.get("currentTeam", {}).get("id")
            
            if not team_id:
                raise ValueError(f"No current team found for player {self.entity_id}")

            # Get team schedule
            end_date = datetime.now() + timedelta(days=7*4*3)
            start_date = datetime.now() - timedelta(days=7*4*3)

            schedule = statsapi.schedule(
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d"),
                team=team_id
            )

            # Cache for team lookups to avoid multiple calls for same team
            team_logo_cache = {}
            
            def get_opponent_logo(opponent_id: int) -> str:
                """Helper function to get opponent logo URL with caching."""
                if opponent_id not in team_logo_cache:
                    team_logo_cache[opponent_id] = TEAM_LOGO_URL.format(team_id=opponent_id)
                return team_logo_cache[opponent_id]

            recent_games = []
            upcoming_games = []
            current_time = datetime.now()

            # Get recent performance stats
            stat_data = statsapi.player_stat_data(
                self.entity_id, 
                group="[hitting,pitching]", 
                type="lastTen"
            )

            # Process recent games with stats
            for game in schedule:
                game_date = datetime.strptime(game['game_date'], "%Y-%m-%d")
                opponent_id = game["away_id"] if game["home_id"] == team_id else game["home_id"]
                
                if game_date < current_time:
                    # Find matching stats for this game
                    game_stats = None
                    if "hitting" in stat_data:
                        game_stats = next(
                            (g for g in stat_data["hitting"] if g["date"] == game["game_date"]),
                            None
                        )
                        if game_stats:
                            game_data = {
                                "date": game["game_date"],
                                "opponent": game["away_name"] if game["home_id"] == team_id else game["home_name"],
                                "opponent_image_url": get_opponent_logo(opponent_id),
                                "home_away": "home" if game["home_id"] == team_id else "away",
                                "status": game["status"],
                                "batting": {
                                    "hits": game_stats.get("hits", 0),
                                    "at_bats": game_stats.get("atBats", 0),
                                    "home_runs": game_stats.get("homeRuns", 0),
                                    "rbi": game_stats.get("rbi", 0),
                                    "walks": game_stats.get("baseOnBalls", 0),
                                    "strikeouts": game_stats.get("strikeOuts", 0),
                                    "avg": game_stats.get("avg", ".000"),
                                }
                            }
                            recent_games.append(game_data)

                    if "pitching" in stat_data:
                        game_stats = next(
                            (g for g in stat_data["pitching"] if g["date"] == game["game_date"]),
                            None
                        )
                        if game_stats:
                            game_data = {
                                "date": game["game_date"],
                                "opponent": game["away_name"] if game["home_id"] == team_id else game["home_name"],
                                "opponent_image_url": get_opponent_logo(opponent_id),
                                "home_away": "home" if game["home_id"] == team_id else "away",
                                "status": game["status"],
                                "pitching": {
                                    "innings": game_stats.get("inningsPitched", "0.0"),
                                    "hits": game_stats.get("hits", 0),
                                    "runs": game_stats.get("runs", 0),
                                    "earned_runs": game_stats.get("earnedRuns", 0),
                                    "walks": game_stats.get("baseOnBalls", 0),
                                    "strikeouts": game_stats.get("strikeOuts", 0),
                                    "era": game_stats.get("era", "0.00"),
                                }
                            }
                            recent_games.append(game_data)
                else:
                    # Add upcoming games
                    upcoming_games.append({
                        "game_id": game["game_id"],
                        "date": game["game_date"],
                        "opponent": game["away_name"] if game["home_id"] == team_id else game["home_name"],
                        "opponent_image_url": get_opponent_logo(opponent_id),
                        "home_away": "home" if game["home_id"] == team_id else "away",
                        "status": game["status"],
                        "venue": game.get("venue_name", ""),
                        "time": game.get("game_time", ""),
                        "probable_pitcher": game.get("probable_pitchers", {}).get(
                            "home" if game["home_id"] == team_id else "away",
                            "TBD"
                        ) if player_info.get("primaryPosition", {}).get("abbreviation") == "P" else None
                    })

            return {
                "player_id": self.entity_id,
                "total_games": len(recent_games) + len(upcoming_games),
                "recent_games": sorted(recent_games, key=lambda x: x["date"], reverse=True),
                "upcoming_games": sorted(upcoming_games, key=lambda x: x["date"])
            }
        except Exception as e:
            logger.error(f"Error fetching player recent and upcoming games: {str(e)}")
            raise

    def _get_player_homeruns(self) -> Dict[str, Any]:
        """Get comprehensive home run statistics for a player."""
        try:
            # Get player info
            player = statsapi.lookup_player(self.entity_id)[0]
            player_name = player["fullName"]

            # Use difflib to find matching home runs
            def calculate_similarity(row):
                hr_name = str(row["title"]).split(" homers")[
                    0
                ]  # Using 'title' instead of 'description'
                return SequenceMatcher(
                    None, hr_name.lower(), player_name.lower()
                ).ratio()

            # Add similarity scores and filter matches
            self.homeruns["similarity"] = self.homeruns.apply(
                calculate_similarity, axis=1
            )
            matching_hrs = self.homeruns[self.homeruns["similarity"] > 0.8]

            # Convert matching rows to list of dictionaries
            homeruns_list = []
            for _, hr in matching_hrs.iterrows():
                homeruns_list.append(
                    {
                        "year": int(hr["season"]),  # Changed from 'year' to 'season'
                        "description": hr[
                            "title"
                        ],  # Changed from 'description' to 'title'
                        "metadata": {
                            "exit_velocity": float(
                                hr["ExitVelocity"]
                            ),  # Changed to match CSV column name
                            "launch_angle": float(
                                hr["LaunchAngle"]
                            ),  # Changed to match CSV column name
                            "distance": float(
                                hr["HitDistance"]
                            ),  # Changed to match CSV column name
                        },
                        "video": {
                            "type": "video",
                            "url": hr["video"],  # Changed from 'video_url' to 'video'
                            "title": hr["title"],
                        },
                    }
                )

            # Calculate metrics using pandas with updated column names
            metrics = {
                "avg_distance": float(matching_hrs["HitDistance"].mean())
                if not matching_hrs.empty
                else 0,
                "avg_exit_velocity": float(matching_hrs["ExitVelocity"].mean())
                if not matching_hrs.empty
                else 0,
                "avg_launch_angle": float(matching_hrs["LaunchAngle"].mean())
                if not matching_hrs.empty
                else 0,
                "longest_homerun": float(matching_hrs["HitDistance"].max())
                if not matching_hrs.empty
                else 0,
                "highest_exit_velocity": float(matching_hrs["ExitVelocity"].max())
                if not matching_hrs.empty
                else 0,
            }

            result = {
                "player_id": self.entity_id,
                "player_name": player_name,
                "total_homeruns": len(matching_hrs),
                "homeruns": sorted(
                    homeruns_list, key=lambda x: x["metadata"]["distance"], reverse=True
                ),
                "metrics": metrics,
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
                self.entity_id, group="[hitting,pitching]", type="career"
            )
            yearly_data = statsapi.player_stat_data(
                self.entity_id, group="[hitting,pitching]", type="yearByYear"
            )

            # Safely get player info with defaults
            first_name = career_data.get("first_name", "")
            last_name = career_data.get("last_name", "")
            position = career_data.get("position", "Unknown")
            mlb_debut = career_data.get("mlb_debut", "")

            # Safely get stats with proper null checks
            stats = career_data.get("stats", [])
            career_stats = {}
            if stats and len(stats) > 0:
                career_stats = stats[0].get("stats", {})

            # Safely get yearly stats
            yearly_stats = {}
            for stat in yearly_data.get("stats", []):
                if stat.get("type") == "yearByYear":
                    season = stat.get("season")
                    if season:
                        yearly_stats[season] = stat.get("stats", {})

            # Construct player stats dictionary with safe values
            player_stats = {
                "player_info": {
                    "name": f"{first_name} {last_name}".strip(),
                    "position": position,
                    "mlb_debut": mlb_debut,
                },
                "career_stats": career_stats,
                "yearly_stats": yearly_stats,
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

            # Generate response using Gemini with error handling
            try:
                result = await self.gemini.generate_with_fallback(
                    formatted_prompt,
                    generation_config=genai.GenerationConfig(
                        temperature=0.1,
                        response_mime_type="application/json",
                    ),
                )

                # Parse and validate the response
                parsed_result = json.loads(result.text)

                # Ensure minimum required structure
                required_fields = [
                    "player_info",
                    "career_achievements",
                    "notable_seasons",
                    "records",
                ]
                if not all(field in parsed_result for field in required_fields):
                    return {
                        "player_info": player_stats["player_info"],
                        "career_achievements": [],
                        "notable_seasons": [],
                        "records": [],
                    }

                return parsed_result

            except Exception as gemini_error:
                logger.error(f"Gemini processing error: {str(gemini_error)}")
                # Return a valid but empty structure on Gemini error
                return {
                    "player_info": player_stats["player_info"],
                    "career_achievements": [],
                    "notable_seasons": [],
                    "records": [],
                }

        except Exception as e:
            logger.error(f"Error fetching player achievements: {str(e)}")
            # Return a valid but empty structure on any error
            return {
                "player_info": {"name": "", "position": "Unknown", "mlb_debut": ""},
                "career_achievements": [],
                "notable_seasons": [],
                "records": [],
            }

    async def process_workflow(self, endpoint: str) -> Dict[str, Any]:
        """Process the workflow based on the endpoint."""
        try:
            normalized_endpoint = endpoint.replace("*", "_")
            if normalized_endpoint not in self.workflows:
                raise ValueError(f"Unsupported endpoint: {endpoint}")

            if (
                normalized_endpoint.startswith("_api_team_")
                and self.entity_type != EntityType.TEAM
            ):
                raise ValueError("Team endpoint cannot be used with player entity")

            if (
                normalized_endpoint.startswith("_api_player_")
                and self.entity_type != EntityType.PLAYER
            ):
                raise ValueError("Player endpoint cannot be used with team entity")

            workflow = self.workflows[normalized_endpoint]
            return (
                await workflow()
                if asyncio.iscoroutinefunction(workflow)
                else workflow()
            )

        except Exception as e:
            logger.error(f"Workflow processing failed: {str(e)}")
            raise
