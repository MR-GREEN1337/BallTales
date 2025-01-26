from fastapi import APIRouter, HTTPException, BackgroundTasks
import httpx
from src.core import LANGUAGES_FOR_LABELLING
from src.api.models import (
    ChatRequest,
    VideoAnalysisRequest,
    ImageAnalysisRequest,
    AnalysisResponse,
    ImageAnalysisResponse,
)
from src.api.agent import mlb_agent, MLBDeps
from src.core.settings import settings
from src.api.analysis import MediaAnalyzer
import json
from typing import Dict, Any, Optional
from fastapi_simple_rate_limiter import rate_limiter
from fastapi.requests import Request
from loguru import logger
from datetime import datetime

# Configure router with proper prefixes and tags
router = APIRouter(
    prefix="/chat",
    tags=["chat"],
    responses={404: {"description": "Not found"}},
)

# Initialize the media analyzer with API key
media_analyzer = MediaAnalyzer(api_key=settings.GEMINI_API_KEY)


@router.post(
    "/",
    description="Return Agent's response to chat request",
)
@rate_limiter(limit=30, seconds=60)
async def chat(request: Request, chat_request: ChatRequest):
    """
    Process chat messages with context from message history and user preferences.

    This endpoint handles general chat interactions, maintaining context and user preferences.
    """
    async with httpx.AsyncClient() as client:
        try:
            # Set up dependencies and context
            deps = MLBDeps(client=client)
            context = _build_chat_context(chat_request)

            # Process the message with the MLB agent
            result = await mlb_agent.process_message(
                deps=deps, message=chat_request.message, context=context
            )

            return result

        except Exception as e:
            logger.error(f"Chat processing failed: {e}")
            raise HTTPException(
                status_code=500, detail=f"Error processing chat: {str(e)}"
            )


@router.post(
    "/analyze-video",
    response_model=AnalysisResponse,
    description="Analyze baseball video content with detailed insights",
)
@rate_limiter(limit=30, seconds=60)
async def analyze_video(
    request: Request,
    analysis_request: VideoAnalysisRequest,
    background_tasks: BackgroundTasks,
):
    """
    Analyzes baseball video content using advanced AI techniques.

    This endpoint processes video content to provide detailed baseball-specific analysis,
    including player movements, game situations, and strategic insights.
    """
    try:
        # Perform video analysis
        result = await media_analyzer.analyze_media(
            media_url=str(analysis_request.videoUrl),
            user_message=analysis_request.message,
            media_type="video",
            metadata=analysis_request.metadata,
        )

        # Log the analysis request in the background
        background_tasks.add_task(
            log_analysis_request,
            media_type="video",
            success=True,
            metadata=analysis_request.metadata,
        )

        return AnalysisResponse(**result)

    except Exception as e:
        # Log failed analysis attempt
        background_tasks.add_task(
            log_analysis_request, media_type="video", success=False, error=str(e)
        )
        raise


@router.post(
    "/analyze-image",
    response_model=ImageAnalysisResponse,
    description="Analyze baseball images with detailed insights",
)
@rate_limiter(limit=30, seconds=60)
async def analyze_image(
    request: Request,
    analysis_request: ImageAnalysisRequest,
    background_tasks: BackgroundTasks,
):
    """
    Analyzes baseball images with AI-powered insights.

    This endpoint processes baseball images to provide detailed analysis of
    player positions, techniques, and game situations.
    """
    try:
        # Perform image analysis
        print(analysis_request)
        result = await media_analyzer.analyze_media(
            media_url=str(analysis_request.imageUrl),
            user_message=analysis_request.message,
            media_type="image",
            metadata=analysis_request.metadata,
        )

        # Log the analysis request in the background
        background_tasks.add_task(
            log_analysis_request,
            media_type="image",
            success=True,
            metadata=analysis_request.metadata,
        )

        return ImageAnalysisResponse(**result)

    except Exception as e:
        # Log failed analysis attempt
        background_tasks.add_task(
            log_analysis_request, media_type="image", success=False, error=str(e)
        )
        raise


async def log_analysis_request(
    media_type: str,
    success: bool,
    metadata: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None,
):
    """
    Logs analysis requests for monitoring and analytics purposes.

    Records details about each analysis request, including success/failure status
    and any relevant metadata for monitoring and improvement.
    """
    try:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "media_type": media_type,
            "success": success,
            "metadata": metadata or {},
            "error": error,
        }

        logger.info(f"Analysis request logged: {json.dumps(log_entry)}")

    except Exception as e:
        logger.error(f"Failed to log analysis request: {e}")


def _build_chat_context(chat_request: ChatRequest) -> Dict[str, Any]:
    """
    Builds the context dictionary for chat processing.

    Creates a structured context object containing message history,
    user preferences, and other relevant information for chat processing.
    """
    return {
        "message_history": [
            {"content": msg.content, "sender": msg.sender}
            for msg in chat_request.history
        ],
        "user_preferences": (
            chat_request.user_data.preferences.model_dump()
            if chat_request.user_data.preferences
            else {}
        ),
        "user_info": {
            "name": chat_request.user_data.name,
            "language": LANGUAGES_FOR_LABELLING[chat_request.user_data.language],
            "id": chat_request.user_data.id,
        },
    }
