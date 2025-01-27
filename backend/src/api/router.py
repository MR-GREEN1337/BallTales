from fastapi import APIRouter, HTTPException, BackgroundTasks, Query, Depends
import httpx
from src.core import LANGUAGES_FOR_LABELLING
from src.api.models import (
    ChatRequest,
    VideoAnalysisRequest,
    ImageAnalysisRequest,
    AnalysisResponse,
    ImageAnalysisResponse,
    SuggestionResponse,
)
from src.api.agent import mlb_agent, MLBDeps
from src.api.analysis import MediaAnalyzer, get_analyzer, media_analyzer
from src.api.utils import log_analysis_request, _build_chat_context
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


@router.get(
    "/chat/{suggestion_type}",
    response_model=SuggestionResponse,
    description="Handle various suggestion-based queries for baseball content",
)
@rate_limiter(limit=30, seconds=60)
async def handle_suggestion(
    suggestion_type: str,
    mediaUrl: str = Query(..., description="URL of the media being analyzed"),
    analyzer: MediaAnalyzer = Depends(get_analyzer),
):
    """
    Processes suggestion-based queries by integrating with existing analysis workflows.

    This endpoint determines the appropriate analysis type based on the suggestion
    and leverages existing analysis capabilities to generate relevant responses.
    """
    try:
        # Determine media type from URL
        is_svg = analyzer.is_svg(mediaUrl)
        entity_type = "team" if is_svg else "player"

        # Define analysis templates for different suggestion types
        analysis_templates = {
            # Team-specific templates
            "team/championships": {
                "prompt": "Analyze this team's championship history and major achievements",
                "analysis_type": "historical",
                "required_type": "team",
            },
            "team/roster/all-time": {
                "prompt": "Provide analysis of the team's most significant players throughout history",
                "analysis_type": "roster",
                "required_type": "team",
            },
            "team/stats": {
                "prompt": "Analyze this team's statistical performance and trends",
                "analysis_type": "statistics",
                "required_type": "team",
            },
            "team/roster/current": {
                "prompt": "Analyze the current team roster and its composition",
                "analysis_type": "roster",
                "required_type": "team",
            },
            "team/games/recent": {
                "prompt": "Analyze the team's recent game performance and trends",
                "analysis_type": "performance",
                "required_type": "team",
            },
            # Player-specific templates
            "player/stats": {
                "prompt": "Provide comprehensive career statistics analysis",
                "analysis_type": "statistics",
                "required_type": "player",
            },
            "player/highlights": {
                "prompt": "Analyze career highlights and significant achievements",
                "analysis_type": "highlights",
                "required_type": "player",
            },
            "player/games/recent": {
                "prompt": "Analyze recent game performances and trends",
                "analysis_type": "performance",
                "required_type": "player",
            },
            "player/homeruns": {
                "prompt": "Analyze home run statistics and patterns",
                "analysis_type": "statistics",
                "required_type": "player",
            },
            "player/awards": {
                "prompt": "Analyze career awards and accolades",
                "analysis_type": "achievements",
                "required_type": "player",
            },
        }

        # Validate suggestion type
        if suggestion_type not in analysis_templates:
            raise HTTPException(
                status_code=400, detail=f"Invalid suggestion type: {suggestion_type}"
            )

        template = analysis_templates[suggestion_type]

        # Validate entity type matches request
        if template["required_type"] != entity_type:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid request: {suggestion_type} is not valid for {entity_type} analysis",
            )

        # Enhance the analysis prompt with metadata
        metadata = {
            "analysis_type": template["analysis_type"],
            "entity_type": entity_type,
            "suggestion_type": suggestion_type,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Perform specialized analysis using existing analyzer
        result = await analyzer.analyze_media(
            media_url=mediaUrl,
            user_message=template["prompt"],
            media_type="image",
            metadata=metadata,
        )

        # Transform the analysis result into appropriate response format
        response_data = {
            "data": {
                "analysis": result["summary"],
                "details": result["details"],
                "type": template["analysis_type"],
                "entityType": entity_type,
            },
            "timestamp": datetime.utcnow(),
            "request_id": str(uuid.uuid4()),
        }

        return SuggestionResponse(**response_data)

    except Exception as e:
        logger.error(f"Suggestion handling failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to process suggestion: {str(e)}"
        )
