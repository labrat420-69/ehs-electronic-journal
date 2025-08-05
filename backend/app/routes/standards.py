"""
Standards routes - MM and FlameAA
"""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/mm", response_class=HTMLResponse)
async def mm_standards():
    """MM Standards management"""
    return "MM Standards - Coming Soon"

@router.get("/flameaa", response_class=HTMLResponse)
async def flameaa_standards():
    """FlameAA Standards management"""
    return "FlameAA Standards - Coming Soon"