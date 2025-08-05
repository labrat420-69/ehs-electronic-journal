"""
Equipment routes - Equipment logs, pipettes, water conductivity
"""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def equipment_list():
    """Equipment logs"""
    return "Equipment List - Coming Soon"

@router.get("/pipettes", response_class=HTMLResponse)
async def pipette_log():
    """Pipette calibration logs"""
    return "Pipette Log - Coming Soon"

@router.get("/water-conductivity", response_class=HTMLResponse)
async def water_conductivity():
    """Water conductivity tests"""
    return "Water Conductivity Tests - Coming Soon"