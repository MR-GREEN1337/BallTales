from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import httpx

from src.api.views.onboarding.agent import mlb_agent, MLBDeps, MLBResponse

router = APIRouter(
    prefix="/onboarding",
    tags=["onboarding"],
    responses={404: {"description": "Not found"}}
)

class ChatRequest(BaseModel):
    message: str
    context: Optional[dict] = None

@router.post("/chat")
async def chat(request: ChatRequest):
    """
    Test endpoint for MLB chat agent.
    
    Sample request:
    {
        "message": "Tell me about the Yankees",
        "context": {"favorite_team": "Yankees"}
    }
    """
    async with httpx.AsyncClient() as client:
        deps = MLBDeps(client=client)
        
        try:
            result = await mlb_agent.run(request.message, deps=deps)
            print(result)
            
            # Convert agent result to frontend response
            '''response = MLBResponse(
                message=result.data,
                data_type=result.context.get('data_type', 'text'),
                data=result.context.get('data', {}),
                suggestions=result.context.get('suggestions', [
                    "Show recent games",
                    "View team roster",
                    "Show highlights"
                ]),
                media=result.context.get('media'),
                actions=result.context.get('actions', [])
            )'''
            
            return result
            
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Error processing chat: {str(e)}"
            )

# Keep your existing test endpoint
@router.post("/")
async def test():
    return "hi"