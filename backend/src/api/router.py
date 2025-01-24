from fastapi import APIRouter, HTTPException
import httpx

from src.core import LANGUAGES_FOR_LABELLING
from src.api.models import ChatRequest, MLBResponse
from src.api.agent import mlb_agent, MLBDeps

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "/",
    description="Return Agent's response to chat request",
    # response_model=MLBResponse,
)
async def chat(request: ChatRequest):
    """Process chat messages with context from message history and user preferences"""
    # print(request)
    async with httpx.AsyncClient() as client:
        deps = MLBDeps(client=client)

        try:
            # Include history and user data in context
            context = {
                "message_history": [
                    {"content": msg.content, "sender": msg.sender}
                    for msg in request.history
                ],
                "user_preferences": request.user_data.preferences.model_dump()
                if request.user_data.preferences
                else {},
                "user_info": {
                    "name": request.user_data.name,
                    "language": LANGUAGES_FOR_LABELLING[request.user_data.language],
                    "id": request.user_data.id,
                },
            }
            # print("Incoming Data...: ", context)
            result = await mlb_agent.process_message(
                deps=deps, message=request.message, context=context
            )

            return result

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error processing chat: {str(e)}"
            )
