"""
Reagents routes - MM, Pb, TCLP
"""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/mm", response_class=HTMLResponse)
async def mm_reagents():
    """MM Reagents management"""
    return "MM Reagents - Coming Soon"

@router.get("/pb", response_class=HTMLResponse)
async def pb_reagents():
    """Pb Reagents management"""
    return "Pb Reagents - Coming Soon"

@router.get("/tclp", response_class=HTMLResponse)
async def tclp_reagents():
    """TCLP Reagents management"""
    return "TCLP Reagents - Coming Soon"