from fastapi import APIRouter, HTTPException
from ..database import get_farm, create_farm, get_crop, plant_crop, get_planted_crops

router = APIRouter()

@router.get("/farms/{user_id}")
async def read_farm(user_id: int):
    farm = await get_farm(user_id)
    if farm is None:
        raise HTTPException(status_code=404, detail="Farm not found")
    return farm

@router.post("/farms")
async def create_new_farm(user_id: int, name: str):
    farm = await create_farm(user_id, name)
    return farm

@router.post("/farms/{farm_id}/plant")
async def plant_new_crop(farm_id: int, crop_name: str):
    crop = await get_crop(crop_name)
    if crop is None:
        raise HTTPException(status_code=404, detail="Crop not found")
    planted = await plant_crop(farm_id, crop['crop_id'], datetime.now())
    return planted

@router.get("/farms/{farm_id}/crops")
async def read_planted_crops(farm_id: int):
    crops = await get_planted_crops(farm_id)
    return crops
