from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field, EmailStr, field_validator
import google.generativeai as genai
from fastapi import HTTPException
from datetime import datetime
import json


class Message(BaseModel):
    """
    Represents a single message in the chat interaction.
    This structure allows for both simple text messages and interactive elements.
    """

    content: str = Field(..., description="The content of the message")
    sender: Literal["bot", "user"] = Field(..., description="Who sent the message")
    type: Literal["text", "options", "selection"] = Field(
        ..., description="Type of message"
    )
    suggestions: Optional[List[str]] = Field(
        None, description="Optional suggestions for user interaction"
    )


class UserStats(BaseModel):
    daysActive: int = Field(
        default=0, description="Number of days the user has been active"
    )
    messagesExchanged: int = Field(
        default=0, description="Total number of messages exchanged"
    )
    queriesAnswered: int = Field(default=0, description="Number of queries answered")

    # Add validators to handle None values
    @field_validator("daysActive", "messagesExchanged", "queriesAnswered")
    def set_default_if_none(cls, v):
        return v if v is not None else 0


class UserPreferences(BaseModel):
    language: str = Field(default="en", description="User's preferred language")
    notificationPreference: str = Field(
        default="Game Time Only", description="When to send notifications"
    )
    statsPreference: str = Field(
        default="Basic", description="Level of statistical detail preferred"
    )

    # Add validators to handle None values
    @field_validator("language")
    def set_default_language(cls, v):
        return v if v is not None else "en"

    @field_validator("notificationPreference")
    def set_default_notification(cls, v):
        return v if v is not None else "Game Time Only"

    @field_validator("statsPreference")
    def set_default_stats(cls, v):
        return v if v is not None else "Basic"


class BaseballPreferences(BaseModel):
    favoriteHomeRun: Optional[str] = Field(
        None, description="User's favorite home run moment"
    )
    favoritePlayer: Optional[str] = Field(None, description="User's favorite player")
    favoriteTeam: Optional[str] = Field(None, description="User's favorite team")
    preferences: UserPreferences = Field(default_factory=UserPreferences)
    stats: UserStats = Field(default_factory=UserStats)

    @classmethod
    def parse_gemini_response(
        cls, response_text: str, current_preferences: "BaseballPreferences"
    ) -> "BaseballPreferences":
        """
        Safely parse Gemini's response and create a new BaseballPreferences object.
        Falls back to current preferences for invalid fields.
        """
        try:
            # First try to parse the response as JSON
            response_data = json.loads(response_text)

            # Create new preferences with default values
            new_prefs = cls(
                favoriteHomeRun=response_data.get(
                    "favoriteHomeRun", current_preferences.favoriteHomeRun
                ),
                favoritePlayer=response_data.get(
                    "favoritePlayer", current_preferences.favoritePlayer
                ),
                favoriteTeam=response_data.get(
                    "favoriteTeam", current_preferences.favoriteTeam
                ),
                preferences=UserPreferences(
                    language=response_data.get("preferences", {}).get(
                        "language", current_preferences.preferences.language
                    ),
                    notificationPreference=response_data.get("preferences", {}).get(
                        "notificationPreference",
                        current_preferences.preferences.notificationPreference,
                    ),
                    statsPreference=response_data.get("preferences", {}).get(
                        "statsPreference",
                        current_preferences.preferences.statsPreference,
                    ),
                ),
                stats=UserStats(
                    daysActive=response_data.get("stats", {}).get(
                        "daysActive", current_preferences.stats.daysActive
                    ),
                    messagesExchanged=response_data.get("stats", {}).get(
                        "messagesExchanged", current_preferences.stats.messagesExchanged
                    ),
                    queriesAnswered=response_data.get("stats", {}).get(
                        "queriesAnswered", current_preferences.stats.queriesAnswered
                    ),
                ),
            )
            return new_prefs

        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error parsing Gemini response: {e}")
            return current_preferences


class UserProfile(BaseModel):
    """
    Basic user profile information.
    Contains personal identification and display information.
    """

    avatar: Optional[str] = Field(None, description="URL to user's avatar image")
    email: EmailStr = Field(..., description="User's email address")
    name: str = Field(..., description="User's display name")


class UpdateUserDataRequest(BaseModel):
    """
    Complete model for updating user data, incorporating both
    baseball preferences and basic profile information.
    Includes methods for analyzing messages and updating preferences using Gemini.
    """

    messages: List[Message] = Field(..., description="Recent message history")
    preferences: BaseballPreferences = Field(
        ..., description="Current baseball preferences"
    )
    user: UserProfile = Field(..., description="User profile information")

    async def analyze_with_gemini(self) -> BaseballPreferences:
        try:
            model = genai.GenerativeModel("gemini-pro")

            # Extract relevant messages for analysis
            baseball_context = "\n".join(
                [f"{msg.sender}: {msg.content}" for msg in self.messages[-5:]]
            )

            prompt = f"""
            Based on these recent messages:
            {baseball_context}
            
            And current user preferences:
            - Favorite Team: {self.preferences.favoriteTeam}
            - Favorite Player: {self.preferences.favoritePlayer}
            - Favorite Home Run: {self.preferences.favoriteHomeRun}
            - Notification Setting: {self.preferences.preferences.notificationPreference}
            - Stats Detail Level: {self.preferences.preferences.statsPreference}
            
            Analyze the conversation for baseball preferences and suggest updates.
            Look for mentions of:
            1. Favorite teams, players, or memorable home runs
            2. Preferred level of statistical detail (Basic/Advanced)
            3. When they want notifications
            
            Return ONLY a valid JSON object with this EXACT structure:
            {{
                "favoriteHomeRun": null,
                "favoritePlayer": null,
                "favoriteTeam": null,
                "preferences": {{
                    "language": "en",
                    "notificationPreference": "Game Time Only",
                    "statsPreference": "Basic"
                }},
                "stats": {{
                    "daysActive": 0,
                    "messagesExchanged": 0,
                    "queriesAnswered": 0
                }}
            }}
            
            Replace null/default values with any preferences found in the conversation.
            Do not include any explanation or text outside the JSON object.
            """

            # Get Gemini's response
            response = await model.generate_content_async(prompt)

            # Use the new parse_gemini_response method
            updated_prefs = BaseballPreferences.parse_gemini_response(
                response.text, self.preferences
            )

            # Update message count
            updated_prefs.stats.messagesExchanged = (
                self.preferences.stats.messagesExchanged + len(self.messages)
            )

            return updated_prefs

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error analyzing user preferences: {str(e)}"
            )

    def update_stats(self) -> UserStats:
        """
        Updates user statistics based on current activity.
        Returns updated UserStats object.
        """
        stats = self.preferences.stats

        # Update message count
        new_messages = len([msg for msg in self.messages if msg.sender == "user"])
        stats.messagesExchanged += new_messages

        # Update queries answered (messages with type 'selection' or containing answers)
        new_queries = len(
            [
                msg
                for msg in self.messages
                if msg.sender == "user"
                and (
                    msg.type == "selection"
                    or any(s in msg.content.lower() for s in ["yes", "no", "choose"])
                )
            ]
        )
        stats.queriesAnswered += new_queries

        return stats
