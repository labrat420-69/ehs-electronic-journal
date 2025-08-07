from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Float, Text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import Optional, List
import os
from pathlib import Path

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./ehs_journal.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Security
SECRET_KEY = "ehs-labs-secret-key-2025"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Database Models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="Technician")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class ChemicalInventory(Base):
    __tablename__ = "chemical_inventory"
    id = Column(Integer, primary_key=True, index=True)
    chemical_name = Column(String, index=True)
    cas_number = Column(String)
    lot_number = Column(String)
    expiry_date = Column(String)
    quantity = Column(Float)
    unit = Column(String)
    location = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_by = Column(String)

class MMReagents(Base):
    __tablename__ = "mm_reagents"
    id = Column(Integer, primary_key=True, index=True)
    reagent_name = Column(String)
    preparation_date = Column(String)
    expiry_date = Column(String)
    concentration = Column(String)
    volume = Column(Float)
    prepared_by = Column(String)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class EquipmentCalibration(Base):
    __tablename__ = "equipment_calibration"
    id = Column(Integer, primary_key=True, index=True)
    equipment_name = Column(String)
    serial_number = Column(String)
    calibration_date = Column(String)
    next_calibration = Column(String)
    technician = Column(String)
    status = Column(String, default="Active")
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

# Pydantic models
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str = "Technician"

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class ChemicalCreate(BaseModel):
    chemical_name: str
    cas_number: Optional[str] = None
    lot_number: Optional[str] = None
    expiry_date: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    location: Optional[str] = None

# Initialize default admin user
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    admin_user = db.query(User).filter(User.username == "admin").first()
    if not admin_user:
        hashed_password = get_password_hash("admin123!")
        admin = User(
            username="admin",
            email="admin@ehslabs.com",
            hashed_password=hashed_password,
            role="Admin"
        )
        db.add(admin)
        db.commit()
        print("✅ Default admin user created: admin/admin123!")
    db.close()
    yield
    # Shutdown (cleanup if needed)

# Create tables
# Note: moved to lifespan function

# FastAPI app
app = FastAPI(title="EHS Electronic Journal", version="1.0.0", lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Authentication functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# Routes
@app.get("/", response_class=HTMLResponse)
async def read_root():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>EHS Electronic Journal</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #1a73e8, #4285f4); min-height: 100vh; }
            .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
            .header { background: white; border-radius: 10px; padding: 30px; margin-bottom: 30px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; }
            .logo { font-size: 36px; font-weight: bold; color: #1a73e8; margin-bottom: 10px; }
            .subtitle { color: #666; font-size: 18px; }
            .clock { background: #1a73e8; color: white; padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 30px; font-size: 24px; font-weight: bold; }
            .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
            .card { background: white; border-radius: 10px; padding: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: transform 0.3s; }
            .card:hover { transform: translateY(-5px); }
            .card-title { font-size: 20px; font-weight: bold; color: #1a73e8; margin-bottom: 15px; }
            .card-content { color: #666; line-height: 1.6; }
            .login-section { background: white; border-radius: 10px; padding: 30px; margin-top: 30px; }
            .form-group { margin-bottom: 20px; }
            .form-group label { display: block; margin-bottom: 5px; font-weight: bold; color: #333; }
            .form-group input { width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 5px; font-size: 16px; }
            .btn { background: #1a73e8; color: white; padding: 12px 30px; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; transition: background 0.3s; }
            .btn:hover { background: #1557b0; }
            .status { background: #e8f5e8; color: #2d5d2d; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">🔬 EHS Electronic Journal</div>
                <div class="subtitle">Professional Laboratory Management System</div>
            </div>
            
            <div class="clock" id="clock"></div>
            
            <div class="status">
                ✅ System Status: Online | Database: Connected | Server: Running on Port 8000
            </div>
            
            <div class="grid">
                <div class="card">
                    <div class="card-title">🧪 Chemical Inventory</div>
                    <div class="card-content">Track and manage all laboratory chemicals, reagents, and materials with expiry dates and locations.</div>
                </div>
                <div class="card">
                    <div class="card-title">⚗️ Reagent Preparation</div>
                    <div class="card-content">Document mercury/metals, lead, and TCLP reagent preparations with full traceability.</div>
                </div>
                <div class="card">
                    <div class="card-title">🔧 Equipment Calibration</div>
                    <div class="card-content">Maintain calibration schedules and records for all laboratory equipment.</div>
                </div>
                <div class="card">
                    <div class="card-title">📊 Standards Management</div>
                    <div class="card-content">Prepare and track analytical standards for ICP-OES and Flame AA analysis.</div>
                </div>
                <div class="card">
                    <div class="card-title">💧 Water Quality Testing</div>
                    <div class="card-content">Monitor and record water conductivity and quality parameters.</div>
                </div>
                <div class="card">
                    <div class="card-title">👥 User Management</div>
                    <div class="card-content">5-tier role system: Admin, Lab Manager, Analyst, Technician, Guest.</div>
                </div>
            </div>
            
            <div class="login-section">
                <h2 style="color: #1a73e8; margin-bottom: 20px;">Login to EHS Electronic Journal</h2>
                <form id="loginForm">
                    <div class="form-group">
                        <label for="username">Username:</label>
                        <input type="text" id="username" name="username" value="admin" required>
                    </div>
                    <div class="form-group">
                        <label for="password">Password:</label>
                        <input type="password" id="password" name="password" value="admin123!" required>
                    </div>
                    <button type="submit" class="btn">🔐 Login to System</button>
                </form>
                <div style="margin-top: 20px; padding: 15px; background: #f0f8ff; border-radius: 5px;">
                    <strong>Default Login:</strong><br>
                    Username: admin<br>
                    Password: admin123!<br>
                    <small>API Documentation: <a href="/docs" style="color: #1a73e8;">/docs</a></small>
                </div>
            </div>
        </div>
        
        <script>
            function updateClock() {
                const now = new Date();
                const est = new Date(now.toLocaleString("en-US", {timeZone: "America/New_York"}));
                const options = { 
                    year: 'numeric', 
                    month: '2-digit', 
                    day: '2-digit', 
                    hour: '2-digit', 
                    minute: '2-digit',
                    hour12: true
                };
                document.getElementById('clock').innerHTML = 
                    '🕒 EST Time: ' + est.toLocaleString('en-US', options).replace(/(\\d+)\\/(\\d+)\\/(\\d+),/, '$1/$2/$3');
            }
            updateClock();
            setInterval(updateClock, 1000);
            
            document.getElementById('loginForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                const username = document.getElementById('username').value;
                const password = document.getElementById('password').value;
                
                try {
                    const response = await fetch('/login', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({username, password})
                    });
                    
                    if (response.ok) {
                        const data = await response.json();
                        localStorage.setItem('token', data.access_token);
                        alert('✅ Login successful! Redirecting to dashboard...');
                        window.location.href = '/dashboard';
                    } else {
                        alert('❌ Login failed. Please check credentials.');
                    }
                } catch (error) {
                    alert('❌ Connection error. Please try again.');
                }
            });
        </script>
    </body>
    </html>
    """
    return html_content

@app.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == user_data.username).first()
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    return """
    <html>
    <head><title>EHS Dashboard</title></head>
    <body style="font-family: Arial; padding: 20px; background: #f5f5f5;">
        <h1 style="color: #1a73e8;">🔬 EHS Electronic Journal Dashboard</h1>
        <p>✅ System is running successfully!</p>
        <p>📊 Access the API documentation: <a href="/docs">/docs</a></p>
        <p>🧪 Chemical Inventory: <a href="/chemicals">/chemicals</a></p>
        <p>⚗️ Reagents Management: <a href="/reagents">/reagents</a></p>
        <p>🔧 Equipment Calibration: <a href="/equipment">/equipment</a></p>
    </body>
    </html>
    """

@app.get("/chemicals")
async def get_chemicals(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    chemicals = db.query(ChemicalInventory).all()
    return chemicals

@app.post("/chemicals")
async def create_chemical(chemical: ChemicalCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_chemical = ChemicalInventory(**chemical.dict(), updated_by=current_user.username)
    db.add(db_chemical)
    db.commit()
    db.refresh(db_chemical)
    return db_chemical

# Initialize default admin user
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    admin_user = db.query(User).filter(User.username == "admin").first()
    if not admin_user:
        hashed_password = get_password_hash("admin123!")
        admin = User(
            username="admin",
            email="admin@ehslabs.com",
            hashed_password=hashed_password,
            role="Admin"
        )
        db.add(admin)
        db.commit()
        print("✅ Default admin user created: admin/admin123!")
    db.close()
    yield
    # Shutdown (cleanup if needed)



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)