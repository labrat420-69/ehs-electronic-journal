"""
Dashboard routes
"""

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.jwt_handler import get_optional_user
from app.models.chemical_inventory import ChemicalInventoryLog
from app.models.reagents import MMReagents
from app.models.equipment import Equipment

# Import templates from main.py setup
from pathlib import Path
from fastapi.templating import Jinja2Templates

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
templates = Jinja2Templates(directory=str(PROJECT_ROOT / "frontend" / "templates"))

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    db: Session = Depends(get_db)
):
    """Main dashboard page with real data statistics"""
    current_user = await get_optional_user(request, db)
    
    # Calculate real statistics from database with error handling
    try:
        total_chemicals = db.query(ChemicalInventoryLog).count()
    except Exception:
        total_chemicals = 0
        
    try:
        total_reagents = db.query(MMReagents).count()
    except Exception:
        total_reagents = 0
    
    expiring_soon = 0  # TODO: Add expiry date logic when implemented
    maintenance_due = 0  # TODO: Add maintenance due logic when implemented
    
    context = {
        "request": request,
        "title": "Dashboard - EHS Electronic Journal",
        "current_user": current_user,
        "current_time_est": "01/01/2025 12:00 PM",  # This will be updated by JavaScript
        "stats": {
            "total_chemicals": total_chemicals,
            "expiring_soon": expiring_soon,
            "total_reagents": total_reagents,
            "maintenance_due": maintenance_due
        }
    }
    
    return templates.TemplateResponse("index.html", context)