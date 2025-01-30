from fastapi import APIRouter, Request
from fastapi_simple_rate_limiter import rate_limiter
from src.api.user.models import UpdateUserDataRequest
from src.api.user.models import analyze_user_preferences
from loguru import logger

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
async def update_preferences(request: Request, user_req: UpdateUserDataRequest):
    """
    Update user preferences based on the provided request.
    """
    updated_prefs = await analyze_user_preferences(user_req)
    logger.info(f"Updated preferences: {updated_prefs}")
    # Save to database
    return {"preferences": updated_prefs, "user": user_req.user}