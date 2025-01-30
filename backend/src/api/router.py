from fastapi import APIRouter, HTTPException, BackgroundTasks, Query, Depends
import httpx
from numpy import char
from src.core import LANGUAGES_FOR_LABELLING
from src.api.models import (
    ChatRequest,
    VideoAnalysisRequest,
    ImageAnalysisRequest,
    AnalysisResponse,
    ImageAnalysisResponse,
    SuggestionResponse,
)
from src.api.agent import MLBDeps
from src.api.analysis import MediaAnalyzer, get_analyzer, media_analyzer
from src.api.utils import log_analysis_request, _build_chat_context
from src.api.mlb_workflow_handler import MLBWorkflowHandler
from fastapi_simple_rate_limiter import rate_limiter
from fastapi.requests import Request
from loguru import logger
from datetime import datetime
import re
import json

# Configure router with proper prefixes and tags
router = APIRouter(
    prefix="/chat",
    tags=["chat"],
    responses={404: {"description": "Not found"}},
)


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
    from src.main import get_mlb_agent
    mlb_agent = get_mlb_agent()
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
    description="Analyze baseball images with detailed insights and contextual suggestions",
)
@rate_limiter(limit=30, seconds=60)
async def analyze_image(
    request: Request,
    analysis_request: ImageAnalysisRequest,
    background_tasks: BackgroundTasks,
) -> ImageAnalysisResponse:
    """
    Analyzes baseball images with AI-powered insights and provides contextual suggestions.

    This endpoint processes baseball images to provide:
    - Detailed analysis of players, teams, or game situations
    - Contextual suggestions based on the image type (team logos, player headshots, or game action)
    - Relevant data endpoints for additional information

    Args:
        request: The incoming FastAPI request
        analysis_request: The analysis request containing image URL and metadata
        background_tasks: FastAPI background tasks handler

    Returns:
        ImageAnalysisResponse: Analysis results including suggestions for further actions

    Raises:
        HTTPException: On analysis failure or invalid input
    """
    try:
        # Extract media type details
        is_svg = media_analyzer.is_svg(analysis_request.imageUrl)
        content_type = "svg" if is_svg else "jpeg"

        # Log analysis start with content type
        logger.info(f"Starting image analysis for content type: {content_type}")

        # Perform image analysis with enhanced metadata
        enhanced_metadata = {
            **(analysis_request.metadata or {}),
            "content_type": content_type,
            "analysis_timestamp": datetime.utcnow().isoformat(),
        }

        result = await media_analyzer.analyze_media(
            media_url=str(analysis_request.imageUrl),
            user_message=analysis_request.message,
            media_type="image",
            metadata=enhanced_metadata,
        )

        # Log the analysis request in the background
        background_tasks.add_task(
            log_analysis_request,
            media_type="image",
            success=True,
            metadata=enhanced_metadata,
        )

        return ImageAnalysisResponse(**result)

    except Exception as e:
        # Enhanced error logging
        logger.error(f"Image analysis failed: {str(e)}", exc_info=True)

        # Log failed analysis attempt with more context
        background_tasks.add_task(
            log_analysis_request,
            media_type="image",
            content_type=content_type if "content_type" in locals() else "unknown",
            success=False,
            error=str(e),
            error_type=type(e).__name__,
        )

        # Re-raise the exception for proper error handling
        raise


chart_docs = open("src/core/constants/charts_docs.json", "r").read()


@router.post(
    "/{suggestion_type}",
    response_model=SuggestionResponse,
    description="Handle various suggestion-based queries for baseball content",
)
@rate_limiter(limit=30, seconds=60)
async def handle_suggestion(
    request: Request,
    suggestion_type: str,
    mediaUrl: str = Query(..., description="URL of the media being analyzed"),
    analyzer: MediaAnalyzer = Depends(get_analyzer),
):
    """
    Processes suggestion-based queries by integrating with existing analysis workflows.

    This endpoint determines the appropriate analysis type based on the suggestion
    and leverages existing analysis capabilities to generate relevant responses.
    """
    global chart_docs
    try:
        # Determine media type from URL
        is_svg = analyzer.is_svg(mediaUrl)
        entity_type = "team" if is_svg else "player"

        team_pattern = r"team-logos/(\d+)\.svg$"
        player_pattern = r"people/(\d+)/headshot"

        # Try team logo pattern first
        team_match = re.search(team_pattern, mediaUrl)
        if team_match:
            mlb_id = team_match.group(1)

        # Try player headshot pattern
        player_match = re.search(player_pattern, mediaUrl)
        if player_match:
            mlb_id = player_match.group(1)
        logger.info(
            f"id: {mlb_id}, entity_type: {entity_type}, endpoint: {suggestion_type}"
        )

        handler = MLBWorkflowHandler(mlb_id, entity_type, chart_docs=chart_docs)
        logger.info(f"Handler: {handler}")
        result = await handler.process_workflow(suggestion_type)
        logger.info(f"Result: {result}")
        return SuggestionResponse(status="success", data=result)

    except ValueError as ve:
        logger.error(f"Invalid request: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Suggestion handling failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
