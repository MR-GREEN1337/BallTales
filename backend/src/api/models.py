from httpx import AsyncClient
import typing_extensions as typing
import enum
from dataclasses import dataclass
from typing import TypedDict, List, Optional, Dict, Any, Literal


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


class ComparisonType(enum.Enum):
    NONE = "none"
    PLAYER_VS_PLAYER = "player_vs_player"
    TEAM_VS_TEAM = "team_vs_team"
    HISTORICAL = "historical"


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
