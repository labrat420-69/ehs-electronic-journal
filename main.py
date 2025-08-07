from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
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
    full_name = Column(String, nullable=False)
    hashed_password = Column(String)
    role = Column(String, default="Technician")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# Pydantic models
class UserCreate(BaseModel):
    username: str
    email: str
    full_name: str = "Admin User"
    password: str
    role: str = "Technician"

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# FastAPI app
app = FastAPI(title="EHS Electronic Journal", version="1.0.0")

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
                    '🕒 EST Time: ' + est.toLocaleString('en-US', options).replace(/(\d+)\/(\d+)\/(\d+),/, '$1/$2/$3');
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
        <p>📊 <a href="/analytics" style="color: #1a73e8; text-decoration: none;">Analytics Dashboard</a></p>
        <p>📋 Access the API documentation: <a href="/docs">/docs</a></p>
        <p>🧪 Chemical Inventory: <a href="/chemicals">/chemicals</a></p>
        <p>⚗️ Reagents Management: <a href="/reagents">/reagents</a></p>
        <p>🔧 Equipment Calibration: <a href="/equipment">/equipment</a></p>
    </body>
    </html>
    """

@app.get("/analytics", response_class=HTMLResponse)
async def analytics_dashboard():
    # Mock data sources for now
    data_sources = {
        "chemical_inventory": {
            "name": "Chemical Inventory",
            "fields": {
                "created_at": "Date Created",
                "current_quantity": "Current Quantity",
                "expiration_date": "Expiration Date",
                "chemical_name": "Chemical Name",
                "manufacturer": "Manufacturer"
            }
        },
        "equipment": {
            "name": "Equipment",
            "fields": {
                "calibration_date": "Calibration Date",
                "next_calibration_due": "Next Calibration Due",
                "equipment_name": "Equipment Name"
            }
        }
    }
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>📊 Analytics Dashboard - EHS Electronic Journal</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <script src="https://cdn.plot.ly/plotly-2.26.0.min.js"></script>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #f8f9fa, #e9ecef); min-height: 100vh; }}
            .container {{ max-width: 1400px; margin: 0 auto; padding: 20px; }}
            .header {{ background: white; border-radius: 12px; padding: 30px; margin-bottom: 30px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); text-align: center; }}
            .logo {{ font-size: 32px; font-weight: bold; color: #1a73e8; margin-bottom: 10px; }}
            .subtitle {{ color: #666; font-size: 18px; }}
            .controls {{ background: white; border-radius: 12px; padding: 25px; margin-bottom: 25px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
            .controls-row {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px; }}
            .control-group {{ display: flex; flex-direction: column; }}
            .control-group label {{ font-weight: 600; color: #202124; margin-bottom: 8px; font-size: 14px; }}
            .control-group select {{ padding: 12px; border: 2px solid #dadce0; border-radius: 8px; font-size: 14px; background: white; }}
            .action-buttons {{ display: flex; gap: 12px; flex-wrap: wrap; justify-content: center; margin-top: 20px; }}
            .btn {{ padding: 12px 24px; border: none; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; transition: all 0.2s; display: inline-flex; align-items: center; gap: 8px; }}
            .btn-primary {{ background: linear-gradient(135deg, #1a73e8, #4285f4); color: white; }}
            .btn-primary:hover {{ background: linear-gradient(135deg, #1557b0, #3367d6); transform: translateY(-1px); }}
            .btn-secondary {{ background: #f8f9fa; color: #5f6368; border: 2px solid #dadce0; }}
            .btn-success {{ background: linear-gradient(135deg, #34a853, #66bb6a); color: white; }}
            .graphs-container {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(500px, 1fr)); gap: 25px; }}
            .graph-card {{ background: white; border-radius: 12px; padding: 0; box-shadow: 0 4px 12px rgba(0,0,0,0.1); overflow: hidden; min-height: 500px; }}
            .graph-header {{ padding: 20px 25px; background: linear-gradient(135deg, #f8f9fa, #ffffff); border-bottom: 1px solid #e8eaed; display: flex; justify-content: space-between; align-items: center; }}
            .graph-title {{ font-size: 18px; font-weight: 600; color: #202124; margin: 0; }}
            .graph-content {{ padding: 0; min-height: 400px; background: #1a1a1a; position: relative; }}
            .graph-placeholder {{ display: flex; flex-direction: column; align-items: center; justify-content: center; height: 400px; color: #9aa0a6; text-align: center; }}
            .graph-placeholder i {{ font-size: 48px; margin-bottom: 15px; color: #dadce0; }}
            .quick-actions {{ background: white; border-radius: 12px; padding: 25px; margin-top: 25px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
            .quick-actions h3 {{ margin-bottom: 20px; color: #202124; }}
            .quick-actions-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }}
            .quick-action {{ background: #f8f9fa; border: 2px solid #e8eaed; border-radius: 8px; padding: 15px; text-align: center; text-decoration: none; color: #5f6368; transition: all 0.2s; }}
            .quick-action:hover {{ border-color: #1a73e8; color: #1a73e8; transform: translateY(-2px); }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">📊 Analytics Dashboard</div>
                <div class="subtitle">Customizable Chemical Inventory & Lab Analytics</div>
                <p style="margin-top: 15px;"><a href="/dashboard" style="color: #1a73e8;">← Back to Main Dashboard</a></p>
            </div>
            
            <div class="controls">
                <div class="controls-row">
                    <div class="control-group">
                        <label for="data-source">Data Source</label>
                        <select id="data-source">
                            <option value="">Select Data Source...</option>
                            <option value="chemical_inventory">Chemical Inventory</option>
                            <option value="equipment">Equipment</option>
                        </select>
                    </div>
                    
                    <div class="control-group">
                        <label for="x-axis">X-Axis Field</label>
                        <select id="x-axis" disabled>
                            <option value="">Select X-Axis...</option>
                        </select>
                    </div>
                    
                    <div class="control-group">
                        <label for="y-axis">Y-Axis Field</label>
                        <select id="y-axis" disabled>
                            <option value="">Select Y-Axis...</option>
                        </select>
                    </div>
                    
                    <div class="control-group">
                        <label for="graph-type">Graph Type</label>
                        <select id="graph-type">
                            <option value="line">Line Chart</option>
                            <option value="bar">Bar Chart</option>
                            <option value="area">Area Chart</option>
                            <option value="scatter">Scatter Plot</option>
                        </select>
                    </div>
                </div>
                
                <div class="action-buttons">
                    <button class="btn btn-primary" onclick="generateGraph()" disabled id="generate-btn">
                        <i class="fas fa-chart-line"></i> Generate Graph
                    </button>
                    <button class="btn btn-secondary" onclick="saveAsPreset()" disabled id="save-preset-btn">
                        <i class="fas fa-save"></i> Save as Preset
                    </button>
                    <button class="btn btn-success" onclick="exportToExcel()" disabled id="export-btn">
                        <i class="fas fa-file-excel"></i> Export to Excel
                    </button>
                </div>
            </div>

            <div class="graphs-container" id="graphs-container">
                <div class="graph-card" id="graph-1">
                    <div class="graph-header">
                        <h3 class="graph-title">Graph 1</h3>
                    </div>
                    <div class="graph-content">
                        <div class="graph-placeholder">
                            <i class="fas fa-chart-line"></i>
                            <p>Select data source and fields to generate a graph</p>
                            <small>Crypto-style visualization with red/green trendlines</small>
                        </div>
                    </div>
                </div>
                
                <div class="graph-card" id="graph-2">
                    <div class="graph-header">
                        <h3 class="graph-title">Graph 2</h3>
                    </div>
                    <div class="graph-content">
                        <div class="graph-placeholder">
                            <i class="fas fa-chart-bar"></i>
                            <p>Additional graph slot available</p>
                        </div>
                    </div>
                </div>
                
                <div class="graph-card" id="graph-3">
                    <div class="graph-header">
                        <h3 class="graph-title">Graph 3</h3>
                    </div>
                    <div class="graph-content">
                        <div class="graph-placeholder">
                            <i class="fas fa-chart-area"></i>
                            <p>Third graph slot available</p>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="quick-actions">
                <h3><i class="fas fa-bolt"></i> Quick Actions & Features</h3>
                <div class="quick-actions-grid">
                    <div class="quick-action">
                        <i class="fas fa-download"></i><br>
                        <strong>CSV Templates</strong><br>
                        <small>Download import templates</small>
                    </div>
                    <div class="quick-action">
                        <i class="fas fa-bell"></i><br>
                        <strong>Reminders</strong><br>
                        <small>Set dashboard reminders</small>
                    </div>
                    <div class="quick-action">
                        <i class="fas fa-sticky-note"></i><br>
                        <strong>Notes</strong><br>
                        <small>Department-wide notes</small>
                    </div>
                    <div class="quick-action">
                        <i class="fas fa-trash"></i><br>
                        <strong>Waste Tracking</strong><br>
                        <small>COC & disposal module</small>
                    </div>
                </div>
            </div>
        </div>

        <script>
        const dataSources = {data_sources};
        let activeGraphs = {{}};

        document.getElementById('data-source').addEventListener('change', function() {{
            const selectedSource = this.value;
            const xAxisSelect = document.getElementById('x-axis');
            const yAxisSelect = document.getElementById('y-axis');
            
            xAxisSelect.innerHTML = '<option value="">Select X-Axis...</option>';
            yAxisSelect.innerHTML = '<option value="">Select Y-Axis...</option>';
            
            if (selectedSource && dataSources[selectedSource]) {{
                const fields = dataSources[selectedSource].fields;
                
                for (const [key, label] of Object.entries(fields)) {{
                    xAxisSelect.innerHTML += `<option value="${{key}}">${{label}}</option>`;
                    yAxisSelect.innerHTML += `<option value="${{key}}">${{label}}</option>`;
                }}
                
                xAxisSelect.disabled = false;
                yAxisSelect.disabled = false;
            }} else {{
                xAxisSelect.disabled = true;
                yAxisSelect.disabled = true;
            }}
            
            checkGenerateButton();
        }});

        function checkGenerateButton() {{
            const dataSource = document.getElementById('data-source').value;
            const xAxis = document.getElementById('x-axis').value;
            const yAxis = document.getElementById('y-axis').value;
            
            const generateBtn = document.getElementById('generate-btn');
            const saveBtn = document.getElementById('save-preset-btn');
            const exportBtn = document.getElementById('export-btn');
            
            const isValid = dataSource && xAxis && yAxis;
            
            generateBtn.disabled = !isValid;
            saveBtn.disabled = !isValid;
            exportBtn.disabled = !isValid;
        }}

        document.getElementById('x-axis').addEventListener('change', checkGenerateButton);
        document.getElementById('y-axis').addEventListener('change', checkGenerateButton);

        function generateGraph() {{
            // Find next available graph slot
            let targetSlot = null;
            for (let i = 1; i <= 3; i++) {{
                if (!activeGraphs[i]) {{
                    targetSlot = i;
                    break;
                }}
            }}
            
            if (!targetSlot) {{
                alert('Maximum of 3 graphs allowed. Please remove a graph first.');
                return;
            }}
            
            const dataSource = document.getElementById('data-source').value;
            const xAxis = document.getElementById('x-axis').value;
            const yAxis = document.getElementById('y-axis').value;
            const graphType = document.getElementById('graph-type').value;
            
            const graphContent = document.querySelector(`#graph-${{targetSlot}} .graph-content`);
            const graphTitle = document.querySelector(`#graph-${{targetSlot}} .graph-title`);
            
            graphTitle.textContent = `${{dataSources[dataSource].name}}: ${{yAxis}} vs ${{xAxis}}`;
            
            // Generate sample data for demo
            const sampleData = generateSampleData(dataSource, xAxis, yAxis);
            
            // Create Plotly graph
            const trace = {{
                x: sampleData.x,
                y: sampleData.y,
                type: graphType === 'scatter' ? 'scatter' : graphType,
                mode: graphType === 'line' ? 'lines+markers' : undefined,
                line: {{ color: '#1a73e8', width: 2 }},
                marker: {{ color: '#4285f4' }},
                fill: graphType === 'area' ? 'tonexty' : undefined,
                fillcolor: 'rgba(26,115,232,0.3)'
            }};
            
            const layout = {{
                title: `${{yAxis}} vs ${{xAxis}}`,
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: '#1a1a1a',
                font: {{ color: 'white', family: 'Arial, sans-serif' }},
                xaxis: {{ 
                    gridcolor: 'rgba(255,255,255,0.1)',
                    title: xAxis
                }},
                yaxis: {{ 
                    gridcolor: 'rgba(255,255,255,0.1)',
                    title: yAxis
                }},
                margin: {{ t: 50, r: 50, b: 50, l: 50 }}
            }};
            
            Plotly.newPlot(graphContent, [trace], layout, {{responsive: true}});
            
            activeGraphs[targetSlot] = {{ dataSource, xAxis, yAxis, graphType }};
        }}

        function generateSampleData(dataSource, xField, yField) {{
            const data = {{ x: [], y: [] }};
            
            // Generate 20 sample data points
            for (let i = 0; i < 20; i++) {{
                if (xField.includes('date')) {{
                    data.x.push(new Date(2024, 0, i + 1).toISOString().split('T')[0]);
                }} else if (xField.includes('name')) {{
                    data.x.push(`Item ${{i + 1}}`);
                }} else {{
                    data.x.push(i + 1);
                }}
                
                if (yField.includes('quantity')) {{
                    data.y.push(Math.random() * 100 + 50);
                }} else if (yField.includes('date')) {{
                    data.y.push(new Date(2024, Math.floor(Math.random() * 12), Math.floor(Math.random() * 28) + 1).toISOString().split('T')[0]);
                }} else {{
                    data.y.push(Math.random() * 1000 + 100);
                }}
            }}
            
            return data;
        }}

        function saveAsPreset() {{
            const name = prompt('Enter preset name:');
            if (name) {{
                alert(`Preset "${{name}}" saved! (Demo - full functionality coming soon)`);
            }}
        }}

        function exportToExcel() {{
            alert('Excel export functionality - coming soon!');
        }}
        </script>
    </body>
    </html>
    """
    
    return html_content

# Initialize default admin user
@app.on_event("startup")
async def startup_event():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    admin_user = db.query(User).filter(User.username == "admin").first()
    if not admin_user:
        hashed_password = get_password_hash("admin123!")
        admin = User(
            username="admin",
            email="admin@ehslabs.com",
            full_name="Admin User",
            hashed_password=hashed_password,
            role="Admin"
        )
        db.add(admin)
        db.commit()
        print("✅ Default admin user created: admin/admin123!")
    db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)