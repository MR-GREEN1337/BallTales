from fastapi import APIRouter, HTTPException
import httpx

from src.core import LANGUAGES_FOR_LABELLING
from src.api.models import ChatRequest, VideoAnalysisRequest
from src.api.agent import mlb_agent, MLBDeps

from fastapi_simple_rate_limiter import rate_limiter  # type: ignore
from fastapi.requests import Request

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
@rate_limiter(limit=30, seconds=60)  # Limited to 30 requests per minute
async def chat(request: Request, chat_request: ChatRequest):
    """Process chat messages with context from message history and user preferences"""
    # print(request)
    async with httpx.AsyncClient() as client:
        deps = MLBDeps(client=client)

        try:
            # Include history and user data in context
            context = {
                "message_history": [
                    {"content": msg.content, "sender": msg.sender}
                    for msg in chat_request.history
                ],
                "user_preferences": chat_request.user_data.preferences.model_dump()
                if chat_request.user_data.preferences
                else {},
                "user_info": {
                    "name": chat_request.user_data.name,
                    "language": LANGUAGES_FOR_LABELLING[
                        chat_request.user_data.language
                    ],
                    "id": chat_request.user_data.id,
                },
            }
            # print("Incoming Data...: ", context)
            result = await mlb_agent.process_message(
                deps=deps, message=chat_request.message, context=context
            )

            return result

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error processing chat: {str(e)}"
            )


@router.post(
    "/analyze-video",
    description="Analyze Homerun video",
    # response_model=MLBResponse,
)
@rate_limiter(limit=30, seconds=60)  # Limited to 30 requests per minute
async def chat(request: Request, chat_request: VideoAnalysisRequest):
    return {
        "analysis": {
            "pitch_type": "Four-Seam Fastball",
            "pitch_velocity": "94.8 mph",
            "spin_rate": "2450 rpm",
            "contact_metrics": {
                "exit_velocity": "108.5 mph",
                "launch_angle": "28°",
                "distance": "432 ft",
                "apex": "98 ft",
            },
            "expected_stats": {
                "xBA": "0.850",
                "xwOBA": "0.925",
                "hit_probability": "0.890",
            },
            "game_context": {
                "inning": "7",
                "outs": "2",
                "base_state": "Runner on First",
                "leverage": "High Leverage",
                "run_expectancy": "1.25",
            },
            "pitch_location": {
                "horizontal": "4.2 inches",
                "vertical": "25.8 inches",
                "zone": "4",
            },
            "additional_insights": "Elite exit velocity in the top 1% of all batted balls this season. Optimal launch angle for maximum distance. Shows ability to handle high-velocity fastballs effectively.",
        },
        "timestamp": "2024-01-24T15:30:45.123Z",
        "request_id": "mlb_analysis_57391",
    }
