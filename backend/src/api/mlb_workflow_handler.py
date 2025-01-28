from typing import Optional, Dict, Any, List
import statsapi
from enum import Enum
from datetime import datetime, timedelta
from loguru import logger


class EntityType(str, Enum):
    PLAYER = "player"
    TEAM = "team"


class MLBWorkflowHandler:
    def __init__(self, entity_id: str, entity_type: EntityType):
        self.entity_id = int(entity_id)
        self.entity_type = entity_type
        self.workflows = {
            # Team workflows
            "_api_team_championships": self._get_team_championships,
            "_api_team_roster_all_time": self._get_team_roster_all_time,
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

    def process_workflow(self, endpoint: str) -> Dict[str, Any]:
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
            return workflow()

        except Exception as e:
            logger.error(f"Workflow processing failed: {str(e)}")
            raise

    def _get_team_championships(self) -> Dict[str, Any]:
        """Get team's championship history."""
        try:
            team_info = statsapi.lookup_team(self.entity_id)[0]
            championships = statsapi.team_leaders(self.entity_id, "championships")

            return {
                "team_id": self.entity_id,
                "team_name": team_info["name"],
                "world_series": {
                    "titles": championships.get("worldSeries", []),
                    "total": len(championships.get("worldSeries", [])),
                    "last_won": max(championships.get("worldSeries", [0]))
                    if championships.get("worldSeries")
                    else None,
                },
                "pennants": {
                    "titles": championships.get("pennants", []),
                    "total": len(championships.get("pennants", [])),
                    "last_won": max(championships.get("pennants", [0]))
                    if championships.get("pennants")
                    else None,
                },
            }
        except Exception as e:
            logger.error(f"Error fetching team championships: {str(e)}")
            raise

    def _get_team_roster_all_time(self) -> Dict[str, Any]:
        """Get historical roster information."""
        try:
            historical_players = statsapi.team_roster(
                self.entity_id, rosterType="allTime"
            )
            formatted_players = []

            for player in historical_players:
                formatted_players.append(
                    {
                        "id": player["id"],
                        "name": player["fullName"],
                        "position": player["primaryPosition"]["abbreviation"],
                        "years": player["years"],
                        "hall_of_fame": player.get("hallOfFame", False),
                    }
                )

            return {
                "team_id": self.entity_id,
                "total_players": len(formatted_players),
                "players": formatted_players,
            }
        except Exception as e:
            logger.error(f"Error fetching historical roster: {str(e)}")
            raise

    def _get_team_stats(self) -> Dict[str, Any]:
        """Get comprehensive team statistics."""
        try:
            current_season = datetime.now().year
            team_stats = statsapi.team_stats(self.entity_id, season=current_season)

            return {
                "team_id": self.entity_id,
                "season": current_season,
                "stats": {
                    "batting": {
                        "avg": team_stats["batting"]["avg"],
                        "runs": team_stats["batting"]["runs"],
                        "home_runs": team_stats["batting"]["homeRuns"],
                        "ops": team_stats["batting"]["ops"],
                    },
                    "pitching": {
                        "era": team_stats["pitching"]["era"],
                        "whip": team_stats["pitching"]["whip"],
                        "strikeouts": team_stats["pitching"]["strikeOuts"],
                        "saves": team_stats["pitching"]["saves"],
                    },
                    "fielding": {
                        "fielding_percentage": team_stats["fielding"][
                            "fielding_percentage"
                        ],
                        "errors": team_stats["fielding"]["errors"],
                    },
                },
            }
        except Exception as e:
            logger.error(f"Error fetching team stats: {str(e)}")
            raise

    def _get_team_roster_current(self) -> Dict[str, Any]:
        """Get current team roster."""
        try:
            roster = statsapi.roster(self.entity_id)
            formatted_roster = []

            for player in roster:
                formatted_roster.append(
                    {
                        "id": player["id"],
                        "name": player["fullName"],
                        "position": player["primaryPosition"]["abbreviation"],
                        "number": player.get("jerseyNumber", ""),
                        "status": player["status"]["description"],
                        "bats": player.get("batSide", {}).get("code", ""),
                        "throws": player.get("pitchHand", {}).get("code", ""),
                    }
                )

            return {
                "team_id": self.entity_id,
                "roster_date": datetime.now().strftime("%Y-%m-%d"),
                "roster_size": len(formatted_roster),
                "players": formatted_roster,
            }
        except Exception as e:
            logger.error(f"Error fetching current roster: {str(e)}")
            raise

    def _get_team_recent_games(self) -> Dict[str, Any]:
        """Get team's recent game results."""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=14)

            schedule = statsapi.schedule(
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d"),
                team=self.entity_id,
            )

            formatted_games = []
            for game in schedule:
                formatted_games.append(
                    {
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
                    }
                )

            return {
                "team_id": self.entity_id,
                "period": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
                "games": formatted_games,
            }
        except Exception as e:
            logger.error(f"Error fetching recent games: {str(e)}")
            raise

    def _get_player_career_stats(self) -> Dict[str, Any]:
        """Get comprehensive player career statistics."""
        try:
            player_info = statsapi.player_stats(self.entity_id, "career")

            return {
                "player_id": self.entity_id,
                "career_stats": {
                    "games_played": player_info["games_played"],
                    "batting": {
                        "avg": player_info.get("avg", ".000"),
                        "home_runs": player_info.get("home_runs", 0),
                        "rbi": player_info.get("rbi", 0),
                        "ops": player_info.get("ops", ".000"),
                        "hits": player_info.get("hits", 0),
                        "stolen_bases": player_info.get("stolen_bases", 0),
                    },
                },
            }
        except Exception as e:
            logger.error(f"Error fetching player career stats: {str(e)}")
            raise

    def _get_player_highlights(self) -> Dict[str, Any]:
        """Get player's career highlights and notable achievements."""
        try:
            player_info = statsapi.player_info(self.entity_id)

            return {
                "player_id": self.entity_id,
                "highlights": {
                    "milestones": player_info.get("milestones", []),
                    "notable_achievements": player_info.get("notable_achievements", []),
                    "career_highlights": player_info.get("career_highlights", []),
                },
            }
        except Exception as e:
            logger.error(f"Error fetching player highlights: {str(e)}")
            raise

    def _get_player_recent_games(self) -> Dict[str, Any]:
        """Get player's recent game performances."""
        try:
            game_log = statsapi.player_stats(self.entity_id, "gameLog")
            recent_games = game_log["stats"][-10:]  # Last 10 games

            formatted_games = []
            for game in recent_games:
                formatted_games.append(
                    {
                        "date": game["game_date"],
                        "opponent": game["opponent"],
                        "result": game["result"],
                        "batting": {
                            "hits": game.get("hits", 0),
                            "at_bats": game.get("at_bats", 0),
                            "home_runs": game.get("home_runs", 0),
                            "rbi": game.get("rbi", 0),
                        },
                    }
                )

            return {"player_id": self.entity_id, "recent_games": formatted_games}
        except Exception as e:
            logger.error(f"Error fetching player recent games: {str(e)}")
            raise

    def _get_player_homeruns(self) -> Dict[str, Any]:
        """Get player's home run statistics and details."""
        try:
            stats = statsapi.player_stats(self.entity_id, "career")
            season_stats = statsapi.player_stats(self.entity_id, "season")

            return {
                "player_id": self.entity_id,
                "career_home_runs": stats.get("home_runs", 0),
                "season_home_runs": season_stats.get("home_runs", 0),
                "longest_home_run": stats.get("longest_home_run", 0),
                "home_run_details": {
                    "pulled": stats.get("pulled_hr", 0),
                    "center": stats.get("center_hr", 0),
                    "opposite_field": stats.get("oppo_hr", 0),
                },
            }
        except Exception as e:
            logger.error(f"Error fetching player home runs: {str(e)}")
            raise

    def _get_player_awards(self) -> Dict[str, Any]:
        """Get player's awards and accolades."""
        try:
            player_info = statsapi.player_info(self.entity_id)
            awards = player_info.get("awards", [])

            formatted_awards = []
            for award in awards:
                formatted_awards.append(
                    {
                        "name": award["name"],
                        "year": award["year"],
                        "team": award.get("team", ""),
                        "league": award.get("league", ""),
                    }
                )

            return {
                "player_id": self.entity_id,
                "total_awards": len(formatted_awards),
                "awards": formatted_awards,
            }
        except Exception as e:
            logger.error(f"Error fetching player awards: {str(e)}")
            raise
