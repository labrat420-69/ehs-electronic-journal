from fastapi import FastAPI, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
import os
from datetime import datetime
import pytz

from app.auth.jwt_handler import get_current_user
from app.routes import auth, dashboard, chemical_inventory, reagents, standards, equipment, maintenance, analytics
from app.utils.timezone_utils import get_est_time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(chemical_inventory.router)
app.include_router(reagents.router)
app.include_router(standards.router)
app.include_router(equipment.router)
app.include_router(maintenance.router)
app.include_router(analytics.router)

@app.get("/health")
def health():
    return {"status": "ok"}

app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
templates = Jinja2Templates(directory="frontend/templates")

# Remove this conflicting route - dashboard router handles "/"
# @app.get("/")
# def read_root(request: Request):
#     est_time = get_est_time()
#     return templates.TemplateResponse("index.html", {"request": request, "time": est_time})