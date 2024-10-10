from fastapi import APIRouter, HTTPException
from ..database import get_user, create_user, update_user_language

router = APIRouter()

@router.get("/{discord_id}")
async def read_user(discord_id: str):
    user = await get_user(discord_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/")
async def create_new_user(discord_id: str, language: str = "en"):
    user = await create_user(discord_id, language)
    return user

@router.put("/{discord_id}/language")
async def update_language(discord_id: str, language: str):
    user = await update_user_language(discord_id, language)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
