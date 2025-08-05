"""
Chemical inventory routes
"""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def chemical_inventory_list():
    """List all chemicals in inventory"""
    return "Chemical Inventory List - Coming Soon"

@router.get("/add", response_class=HTMLResponse)
async def add_chemical():
    """Add new chemical to inventory"""
    return "Add Chemical - Coming Soon"

@router.get("/history", response_class=HTMLResponse)
async def chemical_history():
    """View chemical inventory history"""
    return "Chemical History - Coming Soon"