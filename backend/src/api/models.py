from httpx import AsyncClient
from pydantic import BaseModel, HttpUrl
import typing_extensions as typing
import enum
from dataclasses import dataclass
from typing import NotRequired, TypedDict, List, Optional, Dict, Any, Literal
from datetime import datetime
from src.core import LANGUAGES_FOR_LABELLING


@dataclass
class MLBDeps:
    client: AsyncClient
    season: int = 2025
    endpoints: Dict[str, Any] = None


class REPLResult(TypedDict):
    status: str
    logs: List[str]
    error: Optional[str]
    output: Optional[str]


class MLBResponse(TypedDict):
    message: str
    conversation: str
    data_type: str
    data: Dict[str, Any]
    context: Dict[str, Any]
    suggestions: List[str]
    media: Optional[Dict[str, Any]]
    chart: Optional[Dict[str, Any]]


class IntentType(str, enum.Enum):
    TEAM_INFO = "team_info"
    PLAYER_INFO = "player_info"
    GAME_INFO = "game_info"
    STATS = "stats"
    STANDINGS = "standings"
    SCHEDULE = "schedule"
    HIGHLIGHTS = "highlights"
    CONVERSATION = "conversation"


class Specificity(str, enum.Enum):
    GENERAL = "general"
    SPECIFIC = "specific"
    COMPARATIVE = "comparative"
    ANALYTICAL = "analytical"


class Timeframe(str, enum.Enum):
    HISTORICAL = "historical"
    CURRENT = "current"
    UPCOMING = "upcoming"
    SEASON = "season"
    CAREER = "career"


class Complexity(str, enum.Enum):
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"


class ComparisonType(str, enum.Enum):
    NONE = "none"
    PLAYER_VS_PLAYER = "player_vs_player"
    TEAM_VS_TEAM = "team_vs_team"
    HISTORICAL = "historical"


class StatFocus(str, enum.Enum):
    NONE = "none"
    OFFENSIVE = "offensive"
    DEFENSIVE = "defensive"
    BOTH = "both"


class Sentiment(str, enum.Enum):
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
    comparison_type: ComparisonType
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
    description: str


# Data Plan Enums
class PlanType(str, enum.Enum):
    ENDPOINT = "endpoint"
    FUNCTION = "function"


class StepType(str, enum.Enum):
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


class MediaType(str, enum.Enum):
    IMAGE = "image"
    VIDEO = "video"


class MediaParams(TypedDict):
    param1: str  # Defining specific param structure
    search_query: NotRequired[str]
    date_range: NotRequired[str]


class MediaEndpoint(TypedDict):
    type: MediaType
    endpoint: str
    params: MediaParams


class SearchIdentifiers(TypedDict):
    ids: List[str]
    names: List[str]


class SearchParameters(TypedDict):
    homerun_keywords: List[str]
    player_search: SearchIdentifiers
    team_search: SearchIdentifiers
    media_endpoints: List[MediaEndpoint]


class Message(BaseModel):
    """Represents a single message in the chat"""

    content: str
    sender: Literal["bot", "user"]
    type: Literal["text", "options", "selection"]
    suggestions: Optional[List[str]] = None


class UserPreferences(BaseModel):
    """Represents user's baseball preferences"""

    favorite_teams: Optional[List[str]] = []
    favorite_players: Optional[List[str]] = []
    interests: Optional[List[str]] = []


class User(BaseModel):
    """Represents the user data structure"""

    id: Optional[str] = None
    name: str
    email: str


class UserData(User):
    """Represents complete user information"""

    preferences: Optional[UserPreferences] = None
    language: str


class ChatRequest(BaseModel):
    """Complete chat request schema matching frontend data structure"""

    message: str
    history: List[Message]
    user_data: UserData


class AnalysisRequest(BaseModel):
    """Base class for analysis requests with common fields."""

    message: str
    metadata: Optional[Dict[str, Any]] = None


class VideoAnalysisRequest(AnalysisRequest):
    """Request model for video analysis."""

    videoUrl: HttpUrl


class ImageAnalysisRequest(BaseModel):
    """Request model for image analysis with enhanced fields."""

    imageUrl: HttpUrl
    message: str
    metadata: Optional[Dict[str, Any]] = None
    generate_variation: bool = True  # Flag to control whether to generate a new image


class SuggestionItem(BaseModel):
    """Defines the structure for a suggestion action."""

    text: str
    endpoint: str
    icon: str


class ImageAnalysisRequest(BaseModel):
    """Request model for image analysis."""

    imageUrl: str
    message: str
    metadata: Optional[Dict[str, Any]] = None


class ImageAnalysisDetails(BaseModel):
    """Detailed analysis components."""

    technical_analysis: str
    visual_elements: str
    strategic_insights: str
    additional_context: str


class ImageAnalysisResponse(BaseModel):
    """Enhanced response model including suggestions."""

    summary: str
    details: ImageAnalysisDetails
    timestamp: datetime
    request_id: str
    suggestions: List[SuggestionItem]
    metrics: Optional[Dict[str, Any]] = None


class AnalysisResponse(BaseModel):
    """Response model for analysis results."""

    summary: str
    details: Dict[str, Any]
    timestamp: datetime
    request_id: str


class SuggestionResponse(BaseModel):
    """Response model for suggestion endpoints."""

    data: Dict[str, Any]
    timestamp: datetime
    request_id: str
