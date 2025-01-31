from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import google.generativeai as genai
from fastapi import HTTPException
import json
from src.api.gemini_solid import GeminiSolid


class UpdateUserDataRequest(BaseModel):
    messages: List[Dict[str, Any]]
    preferences: Dict[str, Any]
    user: Dict[str, Any]


async def analyze_user_preferences(request: UpdateUserDataRequest) -> Dict[str, Any]:
    """
    Analyze user chat history and current preferences using Gemini.
    Returns enhanced preferences based on conversation context.
    """
    try:
        model = GeminiSolid()

        # Convert the entire request to a formatted string for analysis
        data_context = {
            "messages": request.messages,
            "current_preferences": request.preferences,
            "user": request.user,
        }

        prompt = f"""
        Analyze this user's baseball chat history and preferences:
        {json.dumps(data_context, indent=2)}

        Based on the conversation and current preferences, generate updated user preferences.
        Follow this schema EXACTLY:

        {{
            "favoriteHomeRun": string | null,      // Memorable home run moment with description
            "favoriteHomeRunUrl": string | null,    // URL to moment highlight/image
            "favoriteHomeRunDescription": string | null,  // Detailed description of the moment
            
            "favoritePlayer": string | null,        // Player's name
            "favoritePlayerUrl": string | null,     // Player's image URL
            "favoritePlayerDescription": string | null,  // Description of why they like this player
            
            "favoriteTeam": string | null,          // Team name
            "favoriteTeamUrl": string | null,       // Team logo URL
            "favoriteTeamDescription": string | null,    // Why they support this team
            
            "preferences": {{
                "language": string,                 // User's preferred language (e.g., "en", "es")
                "statsPreference": string,          // "Basic" or "Advanced"
                "notificationPreference": string    // When to send notifications
            }},
            
            "stats": {{
                "daysActive": number,              // Days using the platform
                "messagesExchanged": number,       // Total messages sent
                "queriesAnswered": number          // Number of questions answered
            }}
        }}

        Rules for analysis:
        1. Preserve existing preferences unless chat clearly indicates changes
        2. Look for mentions of teams, players, or memorable moments
        3. Understand the context of why they like something
        4. Include URLs if mentioned in chat
        5. Keep descriptions concise but meaningful
        6. Maintain existing stats, only update if new data present

        Return ONLY the JSON object, no additional text.
        """

        # Get Gemini's analysis
        response = await model.generate_with_fallback(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
            ),
            model_name="gemini-1.5-flash",
        )

        # Parse and validate the response
        try:
            updated_preferences = json.loads(response.text)
            return updated_preferences
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON response from Gemini")

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error analyzing user preferences: {str(e)}"
        )
