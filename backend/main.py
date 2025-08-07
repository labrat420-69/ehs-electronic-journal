from fastapi import FastAPI, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
import os
from datetime import datetime
import pytz

from app.auth.jwt_handler import get_current_user
from app.routes import auth, dashboard, chemical_inventory, reagents, standards, equipment, maintenance
from app.utils.timezone_utils import get_est_time
from app.database import create_tables

# Import all models to ensure they're registered with SQLAlchemy
from app.models import user, chemical_inventory as chem_models, equipment as eq_models, maintenance as maint_models, reagents as reagent_models, standards as std_models, department

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup - create database tables
    create_tables()
    yield
    # Shutdown (cleanup if needed)

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(dashboard.router)
app.include_router(chemical_inventory.router, prefix="/chemical-inventory", tags=["Chemical Inventory"])
app.include_router(reagents.router, prefix="/reagents", tags=["Reagents"])
app.include_router(standards.router, prefix="/standards", tags=["Standards"])
app.include_router(equipment.router, prefix="/equipment", tags=["Equipment"])
app.include_router(maintenance.router, prefix="/maintenance", tags=["Maintenance"])

@app.get("/health")
def health():
    return {"status": "ok"}

app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
templates = Jinja2Templates(directory="frontend/templates")

@app.get("/")
def read_root(request: Request):
    est_time = get_est_time()
    return templates.TemplateResponse("index.html", {"request": request, "time": est_time})