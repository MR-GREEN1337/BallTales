from datetime import datetime
import google.generativeai as genai
from google.generativeai.types import GenerateContentResponse
import json
from typing import Dict, Any, Optional, List, Union
from loguru import logger
import asyncio
from functools import partial
import uuid
import aiohttp
from PIL import Image
from io import BytesIO
from fastapi import HTTPException

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
        self.processing_steps.append({
            "step": name,
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details or {}
        })
        
    def get_duration(self) -> float:
        """Calculates total processing duration in seconds."""
        return (datetime.utcnow() - self.start_time).total_seconds()
        
    def to_dict(self) -> Dict[str, Any]:
        """Converts metrics to a dictionary format for logging."""
        return {
            "start_time": self.start_time.isoformat(),
            "duration_seconds": self.get_duration(),
            "steps": self.processing_steps
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
        
    async def generate_content_async(
        self,
        content: Union[str, List[Any]],
        temperature: float = 0.7
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
                generation_config={"temperature": temperature}
            )
        )
    
    async def download_image(self, url: str) -> Image.Image:
        """
        Downloads and processes an image from a URL.
        Handles various potential errors during image download and processing.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Failed to download image: {response.status}"
                        )
                    image_data = await response.read()
                    return Image.open(BytesIO(image_data))
        except Exception as e:
            logger.error(f"Image download failed: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Image download failed: {str(e)}"
            )
    
    async def analyze_media(
        self,
        media_url: str,
        user_message: str,
        media_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyzes media content (image or video) and returns structured insights.
        Provides detailed analysis of baseball-related content using AI.
        """
        metrics = AnalysisMetrics()
        
        try:
            # Create analysis prompt based on media type and context
            prompt = self._create_analysis_prompt(
                media_type=media_type,
                user_message=user_message,
                metadata=metadata
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
            
            # Create the final response with metrics
            final_response = {
                **analysis_result,
                "timestamp": datetime.utcnow(),
                "request_id": str(uuid.uuid4()),
                "metrics": metrics.to_dict()
            }
            
            return final_response
            
        except Exception as e:
            metrics.add_step("analysis", "failed", {"error": str(e)})
            logger.error(f"Media analysis failed: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Analysis failed: {str(e)}"
            )
    
    def _create_analysis_prompt(
        self,
        media_type: str,
        user_message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Creates a detailed analysis prompt for the Gemini model.
        Structures the prompt to get comprehensive baseball-specific analysis.
        """
        return f"""
        You are a professional sports analyst specializing in baseball analysis.
        Analyze this {media_type} and provide detailed insights.
        
        Context:
        - Media Type: {media_type}
        - User Query: {user_message}
        {f'- Additional Context: {json.dumps(metadata)}' if metadata else ''}
        
        Return a JSON object with this exact structure:
        {{
            "summary": "Concise summary of key findings",
            "details": {{
                "technical_analysis": "Technical breakdown of player mechanics/positioning",
                "visual_elements": "Key visual aspects and important details",
                "strategic_insights": "Strategic implications and analysis",
                "additional_context": "Historical or statistical context if relevant"
            }}
        }}
        
        Focus on providing concrete, specific observations and insights.
        Analyze all visible aspects of the play, player positioning, and game situation.
        Include relevant historical context or statistical comparisons when appropriate.
        """
    
    def _parse_analysis_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parses and validates the analysis response.
        Ensures the response contains all required fields and proper formatting.
        """
        try:
            cleaned_text = response_text.replace("```json", "").replace("```", "").strip()
            result = json.loads(cleaned_text)
            
            required_fields = ["summary", "details"]
            if not all(field in result for field in required_fields):
                raise ValueError("Missing required fields in analysis result")
                
            return result
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse analysis response: {e}")