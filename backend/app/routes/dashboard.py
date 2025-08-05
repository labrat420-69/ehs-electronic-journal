"""
Dashboard routes
"""

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.jwt_handler import get_optional_user

router = APIRouter()
templates = Jinja2Templates(directory="frontend/templates")

@router.get("/", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    db: Session = Depends(get_db)
):
    """Main dashboard page"""
    current_user = await get_optional_user(request, db)
    
    context = {
        "request": request,
        "title": "Dashboard - EHS Electronic Journal",
        "current_user": current_user,
        "current_time_est": "01/01/2025 12:00 PM"  # This will be updated by JavaScript
    }
    
    return templates.TemplateResponse("index.html", context)