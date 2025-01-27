from datetime import datetime
import google.generativeai as genai
from google.generativeai.types import GenerateContentResponse
import json
from typing import Dict, Any, Optional, List, Union
from loguru import logger
import asyncio
from functools import partial, lru_cache
import uuid
import aiohttp
from PIL import Image
from io import BytesIO
from fastapi import HTTPException
import mimetypes
import cairosvg
import os
from src.core.settings import settings

# Initialize mimetypes database
mimetypes.init()


class AnalysisMetrics:
    """
    Tracks and manages analysis metrics for monitoring purposes.
    This class helps track the performance and success of different analysis steps.
    """

    def __init__(self):
        # Record the start time when analysis begins
        self.start_time: datetime = datetime.utcnow()
        # Store individual processing steps with their outcomes
        self.processing_steps: List[Dict[str, Any]] = []

    def add_step(self, name: str, status: str, details: Optional[Dict] = None):
        """
        Records a processing step with timing information.
        Helps track the progress and success of each analysis phase.
        """
        self.processing_steps.append(
            {
                "step": name,
                "status": status,
                "timestamp": datetime.utcnow().isoformat(),
                "details": details or {},
            }
        )

    def get_duration(self) -> float:
        """Calculates total processing duration in seconds."""
        return (datetime.utcnow() - self.start_time).total_seconds()

    def to_dict(self) -> Dict[str, Any]:
        """Converts metrics to a dictionary format for logging."""
        return {
            "start_time": self.start_time.isoformat(),
            "duration_seconds": self.get_duration(),
            "steps": self.processing_steps,
        }


class MediaAnalyzer:
    """
    Handles media analysis operations for baseball content.
    This class focuses on analyzing images and videos using the Gemini AI model.
    """

    def __init__(self, api_key: str):
        """
        Initializes the analyzer with necessary API configurations.
        Sets up the Gemini model for content analysis.
        """
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.analysis_model = genai.GenerativeModel(model_name="gemini-2.0-flash-exp")

        # Define supported image formats
        self.supported_formats = {
            "image/jpeg",
            "image/png",
            "image/gif",
            "image/svg+xml",
            "image/webp",
            "image/tiff",
        }

    def is_svg(self, url: str) -> bool:
        """
        Determines if a URL points to an SVG file by checking the file extension.

        Args:
            url: The URL to check

        Returns:
            bool: True if the URL ends with .svg, False otherwise
        """
        return url.lower().endswith(".svg")

    def _detect_mime_type(self, file_data: bytes, filename: str = "") -> str:
        """
        Detects the MIME type of a file using a hierarchical approach:
        1. First checks file extension if provided
        2. Then examines file signatures
        3. Finally attempts content-based detection

        Args:
            file_data: The binary content of the file
            filename: Optional filename to help with type detection

        Returns:
            str: The detected MIME type
        """
        # Check filename extension first if provided
        if filename:
            mime_type, _ = mimetypes.guess_type(filename)
            if mime_type and mime_type in self.supported_formats:
                return mime_type

        # Check common file signatures
        signatures = {
            b"\x89PNG\r\n\x1a\n": "image/png",
            b"\xff\xd8\xff": "image/jpeg",
            b"GIF87a": "image/gif",
            b"GIF89a": "image/gif",
            b"RIFF": "image/webp",  # WEBP starts with 'RIFF'
        }

        for signature, mime_type in signatures.items():
            if file_data.startswith(signature):
                return mime_type

        # Check for SVG content
        try:
            content_start = file_data[:1000].decode("utf-8").lower()
            if "<?xml" in content_start and "<svg" in content_start:
                return "image/svg+xml"
        except UnicodeDecodeError:
            pass

        return "application/octet-stream"

    async def download_image(self, url: str) -> Image.Image:
        """
        Downloads and processes an image from a URL, with enhanced support for various formats.

        Args:
            url: The URL of the image to download

        Returns:
            PIL.Image: The processed image ready for analysis

        Raises:
            HTTPException: If image download or processing fails
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Failed to download image: HTTP {response.status}",
                        )

                    image_data = await response.read()

                    # Get filename from URL and detect MIME type
                    filename = os.path.basename(url)
                    mime_type = self._detect_mime_type(image_data, filename)

                    if mime_type not in self.supported_formats:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Unsupported image format: {mime_type}",
                        )

                    # Handle SVG conversion
                    if mime_type == "image/svg+xml" or self.is_svg(url):
                        try:
                            png_data = cairosvg.svg2png(bytestring=image_data)
                            return Image.open(BytesIO(png_data))
                        except Exception as svg_error:
                            logger.error(f"SVG conversion failed: {svg_error}")
                            raise HTTPException(
                                status_code=400, detail="Failed to convert SVG image"
                            )

                    # Process other image formats
                    try:
                        image = Image.open(BytesIO(image_data))
                        # Convert to RGB if necessary (handles RGBA, CMYK, etc.)
                        if image.mode not in ("RGB", "L"):
                            image = image.convert("RGB")
                        return image
                    except Exception as img_error:
                        logger.error(f"Image processing failed: {img_error}")
                        raise HTTPException(
                            status_code=400, detail="Failed to process image"
                        )

        except aiohttp.ClientError as e:
            logger.error(f"Network error during image download: {e}")
            raise HTTPException(
                status_code=500, detail="Failed to download image: Network error"
            )
        except Exception as e:
            logger.error(f"Unexpected error in image processing: {e}")
            raise HTTPException(
                status_code=500, detail=f"Image processing failed: {str(e)}"
            )

    def _get_suggestions(self, media_type: str, url: str) -> List[Dict[str, str]]:
        """
        Returns contextual suggestions based on media type.
        """
        if media_type == "image" and self.is_svg(url):
            return [
                {
                    "text": "Show team's championship history",
                    "endpoint": "/api/team/championships",
                    "icon": "Trophy",
                },
                {
                    "text": "View all-time roster",
                    "endpoint": "/api/team/roster/all-time",
                    "icon": "Users",
                },
                {
                    "text": "Show team statistics",
                    "endpoint": "/api/team/stats",
                    "icon": "BarChart",
                },
                {
                    "text": "View current roster",
                    "endpoint": "/api/team/roster/current",
                    "icon": "UserCheck",
                },
                {
                    "text": "Show recent games",
                    "endpoint": "/api/team/games/recent",
                    "icon": "Calendar",
                },
            ]
        elif media_type == "image":  # JPEG/player headshot
            return [
                {
                    "text": "Show career statistics",
                    "endpoint": "/api/player/stats",
                    "icon": "LineChart",
                },
                {
                    "text": "View career highlights",
                    "endpoint": "/api/player/highlights",
                    "icon": "Video",
                },
                {
                    "text": "Show recent games",
                    "endpoint": "/api/player/games/recent",
                    "icon": "Calendar",
                },
                {
                    "text": "View home runs",
                    "endpoint": "/api/player/homeruns",
                    "icon": "Target",
                },
                {
                    "text": "Show awards and achievements",
                    "endpoint": "/api/player/awards",
                    "icon": "Award",
                },
            ]
        return []

    async def analyze_media(
        self,
        media_url: str,
        user_message: str,
        media_type: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        metrics = AnalysisMetrics()

        try:
            # Get suggestions based on media type
            suggestions = self._get_suggestions(media_type, media_url)

            # Create analysis prompt based on media type and context
            prompt = self._create_analysis_prompt(
                media_type=media_type, user_message=user_message, metadata=metadata
            )
            metrics.add_step("prompt_creation", "success")

            # Process different media types appropriately
            if media_type == "image":
                image = await self.download_image(media_url)
                metrics.add_step("image_download", "success")
                response = await self.generate_content_async([image, prompt])
            else:
                response = await self.generate_content_async([media_url, prompt])

            metrics.add_step("content_generation", "success")

            # Parse and validate the analysis response
            analysis_result = self._parse_analysis_response(response.text)
            metrics.add_step("response_parsing", "success")

            # Create the final response with metrics and suggestions
            final_response = {
                **analysis_result,
                "timestamp": datetime.utcnow(),
                "request_id": str(uuid.uuid4()),
                "metrics": metrics.to_dict(),
                "suggestions": suggestions,  # Add suggestions to response
            }

            return final_response

        except Exception as e:
            metrics.add_step("analysis", "failed", {"error": str(e)})
            logger.error(f"Media analysis failed: {e}")
            raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

    async def generate_content_async(
        self, content: Union[str, List[Any]], temperature: float = 0.7
    ) -> GenerateContentResponse:
        """
        Asynchronously generates content analysis using the Gemini model.
        Wraps the synchronous API call in an asyncio executor for better performance.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            partial(
                self.analysis_model.generate_content,
                content,
                generation_config={"temperature": temperature},
            ),
        )

    def _create_analysis_prompt(
        self,
        media_type: str,
        user_message: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Creates a comprehensive analysis prompt focusing on historical, biographical,
        and gameplay aspects based on media type.
        """
        base_response_structure = """
            Return a JSON object with this exact structure:
            {
                "summary": "Concise summary of key findings",
                "details": {
                    "technical_analysis": "Core facts and historical/statistical data",
                    "visual_elements": "Current state and recent developments",
                    "strategic_insights": "Analysis of trends and patterns",
                    "additional_context": "Broader context and future implications"
                }
            }
            """

        if media_type == "image" and self.is_svg(user_message):
            # Team historical analysis
            return f"""
                You are a baseball historian with deep knowledge of MLB team histories, traditions, and cultural impact.
                Provide a comprehensive analysis of this team's history and legacy in baseball.
                
                Context:
                - Team Identifier: {user_message}
                {f"- Additional Context: {json.dumps(metadata)}" if metadata else ""}
                
                {base_response_structure}
                
                Structure your analysis to cover:
                - Franchise history: founding, relocations, name changes, and key eras
                - Championship history and postseason appearances
                - Hall of Fame players and legendary figures associated with the team
                - Notable rivalries and significant moments in team history
                - Team culture, traditions, and impact on baseball
                - Recent organizational developments and future outlook
                
                Base your analysis on verified historical records and emphasize:
                - Major organizational milestones and achievements
                - Evolution of team identity through different eras
                - Impact on baseball culture and local community
                - Key ownership changes and organizational philosophy
                - Player development history and team-building approach
                """

        elif media_type == "image":
            # Player career and background analysis
            return f"""
                You are a baseball biographer and player development expert with access to comprehensive player histories.
                Provide an in-depth analysis of this player's career, background, and impact on baseball.
                
                Context:
                - Player Image Reference: {user_message}
                {f"- Additional Context: {json.dumps(metadata)}" if metadata else ""}
                
                {base_response_structure}
                
                Structure your analysis to cover:
                - Early life and path to professional baseball
                - Amateur career and draft/signing history
                - Professional development and career progression
                - Playing style, strengths, and notable achievements
                - Impact on teams and roles throughout career
                - Off-field influence and personality traits
                
                Focus your analysis on:
                - Key career moments and development milestones
                - Influences and mentors in their baseball journey
                - Playing philosophy and approach to the game
                - Leadership qualities and clubhouse presence
                - Statistical achievements and career highlights
                - Legacy and impact on the sport
                """

        else:
            # Game highlight/homerun video analysis
            return f"""
                You are a baseball performance analyst specializing in game analysis and player achievements.
                Analyze this gameplay moment and provide comprehensive insights about its significance.
                
                Context:
                - Play Type: Game Highlight Video
                - User Query: {user_message}
                {f"- Additional Context: {json.dumps(metadata)}" if metadata else ""}
                
                {base_response_structure}
                
                Structure your analysis to cover:
                - Game situation and context
                - Player's approach and execution
                - Statistical significance of the moment
                - Historical comparisons to similar achievements
                - Impact on game/season/career statistics
                - Place in baseball history (if applicable)
                
                Emphasize:
                - Situation-specific strategy and execution
                - Player's historical performance in similar situations
                - Statistical significance and record implications
                - Context within the player's career achievements
                - Comparison to similar historic moments
                """

    def _parse_analysis_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parses and validates the analysis response.
        Ensures the response contains all required fields and proper formatting.
        """
        try:
            cleaned_text = (
                response_text.replace("```json", "").replace("```", "").strip()
            )
            result = json.loads(cleaned_text)

            required_fields = ["summary", "details"]
            if not all(field in result for field in required_fields):
                raise ValueError("Missing required fields in analysis result")

            return result

        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse analysis response: {e}")


@lru_cache()
def get_analyzer() -> MediaAnalyzer:
    return MediaAnalyzer(api_key=settings.GEMINI_API_KEY)


# Initialize the media analyzer with API key
media_analyzer = MediaAnalyzer(api_key=settings.GEMINI_API_KEY)
