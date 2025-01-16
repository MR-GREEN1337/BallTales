from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

class GameState(BaseModel):
    game_pk: str
    inning: int
    is_top_inning: bool
    balls: int
    strikes: int
    outs: int
    
class PlayerStats(BaseModel):
    player_id: str
    name: str
    position: str
    batting_avg: float
    era: Optional[float] = None
    
class GameAnalysis(BaseModel):
    situation: str
    analysis: str
    probability: Dict[str, float]
    suggested_strategies: List[str]