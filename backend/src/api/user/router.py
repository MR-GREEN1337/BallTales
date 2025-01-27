from fastapi import APIRouter, Request
from fastapi_simple_rate_limiter import rate_limiter
from src.api.user.models import UpdateUserDataRequest

# Configure router with proper prefixes and tags
router = APIRouter(
    prefix="/user",
    tags=["user"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "/update-preferences",
    description="Update user profile and baseball preferences",
)
@rate_limiter(limit=30, seconds=60)
async def update_user(request: Request, data: UpdateUserDataRequest):
    print(data)
    # Analyze messages and update preferences
    updated_preferences = await data.analyze_with_gemini()

    # Update usage statistics
    updated_stats = data.update_stats()
    updated_preferences.stats = updated_stats

    return {"preferences": updated_preferences, "user": data.user}
