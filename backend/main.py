"""
EHS Electronic Journal - Main Application Entry Point
Laboratory Management System for EHS Labs Environmental Hazards Services
"""

from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
import os
from datetime import datetime
import pytz

from app.auth.jwt_handler import get_current_user
from app.routes import auth, dashboard, chemical_inventory, reagents, standards, equipment, maintenance
from app.utils.timezone_utils import get_est_time

# Initialize FastAPI app
app = FastAPI(
    title="EHS Electronic Journal",
    description="Laboratory Management System for EHS Labs Environmental Hazards Services",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files and templates
import os
from pathlib import Path

# Get the project root directory (parent of backend)
PROJECT_ROOT = Path(__file__).parent.parent

app.mount("/static", StaticFiles(directory=str(PROJECT_ROOT / "frontend" / "static")), name="static")
templates = Jinja2Templates(directory=str(PROJECT_ROOT / "frontend" / "templates"))

# Security
security = HTTPBearer()

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
app.include_router(chemical_inventory.router, prefix="/chemical-inventory", tags=["Chemical Inventory"])
app.include_router(reagents.router, prefix="/reagents", tags=["Reagents"])
app.include_router(standards.router, prefix="/standards", tags=["Standards"])
app.include_router(equipment.router, prefix="/equipment", tags=["Equipment"])
app.include_router(maintenance.router, prefix="/maintenance", tags=["Maintenance"])

# Template context processor - adds common variables to all templates
@app.middleware("http")
async def add_template_context(request: Request, call_next):
    """Add common template variables to all requests"""
    response = await call_next(request)
    return response

# Global template variables
def get_template_context(request: Request):
    """Get common template context variables"""
    return {
        "request": request,
        "current_time_est": get_est_time().strftime("%m/%d/%Y %I:%M %p"),
        "app_name": "EHS Electronic Journal",
        "company_name": "EHS Labs Environmental Hazards Services",
        "current_user": getattr(request.state, "user", None)
    }

@app.get("/")
async def root(request: Request):
    """Root endpoint - redirect to dashboard"""
    context = get_template_context(request)
    return templates.TemplateResponse("index.html", context)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": get_est_time().isoformat(),
        "timezone": "EST"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)