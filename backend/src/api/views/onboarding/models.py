from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

# Base Response Models for Different Data Types
class TeamData(BaseModel):
    """Team-specific data structure"""
    id: int
    name: str
    abbreviation: str
    teamName: str
    locationName: str
    division: Dict[str, Any]
    league: Dict[str, Any]
    venue: Optional[Dict[str, Any]]
    stats: Optional[Dict[str, Any]]
    record: Optional[Dict[str, Any]]
    roster: Optional[List[Dict[str, Any]]]
    recent_games: Optional[List[Dict[str, Any]]]
    upcoming_games: Optional[List[Dict[str, Any]]]

class PlayerData(BaseModel):
    """Player-specific data structure"""
    id: int
    fullName: str
    primaryNumber: Optional[str]
    currentAge: Optional[int]
    birthDate: Optional[str]
    birthCity: Optional[str]
    birthCountry: Optional[str]
    height: Optional[str]
    weight: Optional[int]
    currentTeam: Dict[str, Any]
    primaryPosition: Dict[str, Any]
    stats: Optional[Dict[str, Any]]
    headshot_url: Optional[str]
    recent_games: Optional[List[Dict[str, Any]]]
    highlights: Optional[List[Dict[str, Any]]]

class GameData(BaseModel):
    """Game-specific data structure"""
    gamePk: int
    gameDate: str
    status: Dict[str, Any]
    teams: Dict[str, Any]
    venue: Dict[str, Any]
    dayNight: Optional[str]
    weather: Optional[Dict[str, Any]]
    probablePitchers: Optional[Dict[str, Any]]
    linescore: Optional[Dict[str, Any]]
    highlights: Optional[List[Dict[str, Any]]]

class StatData(BaseModel):
    """Statistics data structure"""
    group: str  # e.g., 'hitting', 'pitching', 'fielding'
    stats: List[Dict[str, Any]]
    splits: Optional[List[Dict[str, Any]]]

class MediaContent(BaseModel):
    """Structure for media content like highlights, images"""
    type: str = Field(..., description="Type of media - video, image, etc.")
    title: Optional[str]
    description: Optional[str]
    url: str
    thumbnailUrl: Optional[str]
    duration: Optional[str]
    date: Optional[datetime]
    tags: Optional[List[str]]

class Action(BaseModel):
    """Available actions for the frontend"""
    type: str = Field(..., description="Action type - view_roster, show_stats, etc.")
    label: str
    data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional data needed for the action"
    )

class MLBResponse(BaseModel):
    """Main response structure for MLB chat interactions"""
    message: str = Field(..., description="Natural language response to user query")
    data_type: str = Field(
        ..., 
        description="Type of data being returned - team, player, game, stats, etc."
    )
    
    # Main data payload - can be any of the specific types or generic dict
    data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Primary data payload matching the data_type"
    )
    
    # Additional context and metadata
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional context about the response"
    )
    
    # Frontend display elements
    suggestions: List[str] = Field(
        default_factory=list,
        description="Suggested follow-up queries"
    )
    media: Optional[List[MediaContent]] = Field(
        default=None,
        description="Related media content"
    )
    actions: List[Action] = Field(
        default_factory=list,
        description="Available actions for this response"
    )
    
    # Error handling
    error: Optional[str] = None
    warning: Optional[str] = None

    def format_team_response(self, team_data: TeamData) -> None:
        """Helper method to format team data response"""
        self.data_type = "team"
        self.data = team_data.dict()
        self.suggestions = [
            f"Show {team_data.name} roster",
            f"Recent {team_data.name} highlights",
            f"{team_data.name} upcoming games",
            f"{team_data.name} season stats"
        ]
        self.actions = [
            Action(
                type="view_roster",
                label="View Full Roster",
                data={"team_id": team_data.id}
            ),
            Action(
                type="view_schedule",
                label="View Schedule",
                data={"team_id": team_data.id}
            )
        ]

    def format_player_response(self, player_data: PlayerData) -> None:
        """Helper method to format player data response"""
        self.data_type = "player"
        self.data = player_data.dict()
        self.suggestions = [
            f"Show {player_data.fullName}'s career stats",
            f"{player_data.fullName}'s recent highlights",
            f"Compare with similar players"
        ]
        if player_data.headshot_url:
            self.media = [
                MediaContent(
                    type="image",
                    title=f"{player_data.fullName} Headshot",
                    url=player_data.headshot_url
                )
            ]

    def format_game_response(self, game_data: GameData) -> None:
        """Helper method to format game data response"""
        self.data_type = "game"
        self.data = game_data.dict()
        self.suggestions = [
            "Show game highlights",
            "View box score",
            "Show play-by-play"
        ]
        if game_data.highlights:
            self.media = [
                MediaContent(**highlight)
                for highlight in game_data.highlights
            ]

    def add_error(self, error_msg: str) -> None:
        """Add error message to response"""
        self.error = error_msg
        self.data = {}  # Clear any partial data
        self.suggestions = ["Try another team", "Search for a player", "View today's games"]

    def add_warning(self, warning_msg: str) -> None:
        """Add warning message while still providing data"""
        self.warning = warning_msg

    class Config:
        """Pydantic config"""
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }