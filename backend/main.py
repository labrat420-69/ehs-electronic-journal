from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from fastapi.responses import RedirectResponse
import os
from datetime import datetime
import pytz

from backend.auth.jwt_handler import get_current_user
from backend.routes import auth, dashboard, chemical_inventory, reagents, standards, equipment, maintenance, analytics, reminders, waste
from backend.utils.timezone_utils import get_est_time

# --- Add this import for table creation ---
from backend.database import create_tables, init_default_user

app = FastAPI()

# --- Add this startup event to ensure tables are created ---
@app.on_event("startup")
def on_startup():
    create_tables()
    init_default_user()

# --- Add exception handler for authentication redirects ---
@app.exception_handler(HTTPException)
async def auth_exception_handler(request: Request, exc: HTTPException):
    """Handle authentication exceptions by redirecting to login"""
    if exc.status_code == 401 and request.url.path != "/login":
        # If it's a web request (not API), redirect to login
        if request.headers.get("accept", "").startswith("text/html"):
            return RedirectResponse(url="/login?next=" + str(request.url), status_code=302)
    
    # For API requests or non-auth errors, return the original exception
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

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
app.include_router(reminders.router)
app.include_router(waste.router)

@app.get("/health")
def health():
    return {"status": "ok"}

app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
templates = Jinja2Templates(directory="frontend/templates")

# The dashboard router handles "/"
# @app.get("/")
# def read_root(request: Request):
#     est_time = get_est_time()
#     return templates.TemplateResponse("index.html", {"request": request, "time": est_time})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
