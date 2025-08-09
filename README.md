# EHS Electronic Journal - Development Setup Guide

## Overview
The EHS Electronic Journal is a comprehensive laboratory management system designed for EHS Labs Environmental Hazards Services. This system provides electronic tracking of chemical inventory, reagents, standards, equipment, and maintenance operations.

## Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Git

### Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/labrat420-69/ehs-electronic-journal.git
   cd ehs-electronic-journal
   ```

2. **Set up Python environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials and settings
   ```

4. **Database Setup:**
   
   **Option A: SQLite (Simplest - No external database required)**
   ```bash
   # Set in .env file:
   DATABASE_TYPE=sqlite
   # No additional setup required
   ```
   
   **Option B: PostgreSQL**
   ```bash
   # Set in .env file:
   DATABASE_TYPE=postgresql
   POSTGRES_SERVER=localhost
   POSTGRES_USER=ehs_user
   POSTGRES_PASSWORD=ehs_password
   
   # Create database
   createdb ehs_electronic_journal
   
   # Run schema
   psql -d ehs_electronic_journal -f database/postgresql/schema.sql
   ```
   
   **Option C: MS SQL Server**
   ```bash
   # Set in .env file:
   DATABASE_TYPE=mssql
   MSSQL_SERVER=localhost
   MSSQL_USER=ehs_user
   MSSQL_PASSWORD=EhsPassword123!
   
   # Create database (using SQL Server Management Studio or sqlcmd)
   sqlcmd -S localhost -E -Q "CREATE DATABASE ehs_electronic_journal"
   sqlcmd -S localhost -d ehs_electronic_journal -i database/sqlserver/schema.sql
   ```

5. **Run the application:**
   ```bash
   # Run from the root directory using module syntax
   python -m backend.main
   
   # Or using uvicorn directly
   python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Access the application:**
   - Open browser to: http://localhost:8000
   - **Authentication Required**: The application now requires login to access the dashboard and protected features
   - Default admin login: **Username:** `admin` / **Password:** `admin123`
   - **Security Note**: Change the default password immediately after first login

## Fly.io Deployment

### Prerequisites
- [Fly CLI installed](https://fly.io/docs/getting-started/installing-flyctl/)
- Fly.io account created (`fly auth signup`)
- Docker installed locally (for testing)

### Deployment Steps

1. **Login to Fly.io:**
   ```bash
   fly auth login
   ```

2. **Deploy the application:**
   ```bash
   # Clone and navigate to the repository
   git clone https://github.com/labrat420-69/ehs-electronic-journal.git
   cd ehs-electronic-journal
   
   # Deploy to Fly.io (uses existing fly.toml configuration)
   fly deploy
   ```

3. **Set up environment variables (optional):**
   ```bash
   # For production, you may want to set environment variables
   fly secrets set DATABASE_TYPE=sqlite
   fly secrets set DATABASE_PATH=/app/ehs_journal.db
   
   # For PostgreSQL database (recommended for production):
   # fly secrets set DATABASE_TYPE=postgresql
   # fly secrets set POSTGRES_SERVER=your-postgres-host
   # fly secrets set POSTGRES_USER=your-username
   # fly secrets set POSTGRES_PASSWORD=your-password
   # fly secrets set POSTGRES_DATABASE=ehs_electronic_journal
   ```

4. **Open your deployed application:**
   ```bash
   fly open
   ```

### Fly.io Configuration

The `fly.toml` file is already configured with:
- **App name**: `ehs-electronic-journal`
- **Region**: `iad` (US East - Northern Virginia)
- **Port**: 8000 (FastAPI default)
- **HTTPS**: Force HTTPS enabled
- **Auto-scaling**: Configured to stop/start machines automatically
- **Resources**: 1GB RAM, 1 shared CPU

### Database Considerations

**For Production (Recommended):**
- Use Fly Postgres for production deployments:
  ```bash
  fly postgres create --name ehs-journal-db --region iad
  fly postgres attach --app ehs-electronic-journal ehs-journal-db
  ```

**For Development/Testing:**
- SQLite database is used by default and created automatically at startup
- Database file is stored in `/app/ehs_journal.db` inside the container
- **Note**: SQLite data will be lost when the container restarts unless you use Fly volumes

**Using Fly Volumes for SQLite Persistence:**
```bash
# Create a volume for SQLite database persistence
fly volumes create ehs_data --region iad --size 1

# Update fly.toml to mount the volume (add to [mounts] section):
# [mounts]
# destination = "/app/data"
# source = "ehs_data"

# Then set DATABASE_PATH to use the volume:
fly secrets set DATABASE_PATH=/app/data/ehs_journal.db
```

### Deployment Checklist

Before deploying to production, ensure:

- [x] All backend Python code is present and functional
- [x] **Authentication system properly configured and tested**
- [x] **Dashboard and API endpoints protected from unauthorized access**
- [x] **Login/logout functionality working with proper error handling**
- [x] **Default admin user auto-created on first startup**
- [x] All frontend templates are included (especially `frontend/templates/dashboard/overview.html`)
- [x] All static assets are copied to the Docker image (`frontend/static/`)
- [x] Dockerfile installs all requirements and copies necessary files
- [x] .dockerignore properly excludes development files but includes required assets
- [x] Database is created at startup but not included in the image
- [x] App starts successfully and serves templates without TemplateNotFound errors
- [x] Health endpoint responds correctly (`/health`)
- [ ] Environment variables configured for production
- [ ] Database backup strategy implemented (if using Fly Postgres)
- [ ] SSL certificates configured (handled automatically by Fly.io)
- [ ] Monitoring and logging set up

### Monitoring and Logs

```bash
# View application logs
fly logs

# Monitor resource usage
fly status

# Scale the application if needed
fly scale count 2  # Run 2 instances

# Connect to the running container for debugging
fly ssh console
```

### Troubleshooting

**Common Issues:**

1. **Build fails with SSL certificates:**
   - The Dockerfile includes `--trusted-host` flags for environments with certificate issues

2. **TemplateNotFound errors:**
   - Ensure templates are copied to the correct path in Dockerfile
   - Check that template paths in routes match the directory structure

3. **Static files not loading:**
   - Verify `frontend/static` is copied in Dockerfile
   - Check static file mounting in `backend/main.py`

4. **Database connection errors:**
   - For SQLite: Ensure `DATABASE_PATH` points to a writable location
   - For Postgres: Verify connection strings and credentials

5. **App won't start:**
   ```bash
   # Check logs for errors
   fly logs
   
   # Connect to container for debugging
   fly ssh console
   cd /app
   python -m uvicorn backend.main:app --host 0.0.0.0 --port 8080
   ```

### Cost Optimization

- Use `fly scale count 0` during development to stop machines when not needed
- Configure `min_machines_running = 0` in fly.toml for development apps
- Monitor resource usage and adjust memory/CPU allocation as needed

## Fly.io Deployment

The EHS Electronic Journal can be deployed to Fly.io for cloud hosting. The deployment configuration uses port 8080 and requires deploying from the correct branch.

### Prerequisites
- [Fly CLI installed](https://fly.io/docs/hands-on/install-flyctl/)
- Fly.io account and authenticated (`fly auth login`)

### Initial Deployment

1. **Ensure you're on the correct branch:**
   ```bash
   # The application should be deployed from the main1 branch
   git checkout main1
   git pull origin main1
   ```

2. **Deploy to Fly.io:**
   ```bash
   fly deploy
   ```

### Important Configuration Details

- **Port Configuration**: The application is configured to use port 8080 (not 8000)
  - `Dockerfile` exposes port 8080 
  - `fly.toml` uses `internal_port = 8080`
  - FastAPI runs on `uvicorn backend.main:app --host 0.0.0.0 --port 8080`

- **Static Files**: The Dockerfile correctly copies both:
  - `frontend/templates/` - Jinja2 templates
  - `frontend/static/` - CSS, JS, and static assets

- **Application Entry Point**: Uses `uvicorn backend.main:app` (correct module path)

### Deployment Checklist

Before deploying, ensure:
- [x] All recent template and static file changes are merged to main1
- [x] Dockerfile copies `frontend/templates` and `frontend/static` 
- [x] Port configuration uses 8080 in both Dockerfile and fly.toml
- [x] Application entry point is `backend.main:app`
- [ ] Environment secrets configured (`fly secrets set KEY=value`)
- [ ] Database configured (SQLite with volumes or Fly Postgres)

### Environment Configuration

```bash
# Set required secrets
fly secrets set SECRET_KEY="your-secret-key-here"
fly secrets set DATABASE_TYPE="sqlite"  # or postgresql

# For PostgreSQL (if using Fly Postgres):
fly postgres create --name ehs-db
fly postgres attach ehs-db  # Sets DATABASE_URL automatically
fly secrets set DATABASE_TYPE="postgresql"
```

### SQLite Configuration with Persistent Storage

```bash
# Create a volume for SQLite database persistence
fly volumes create ehs_data --region iad --size 1

# Update fly.toml to mount the volume:
# [mounts]
# destination = "/app/data" 
# source = "ehs_data"

# Set the database path to use the volume:
fly secrets set DATABASE_PATH="/app/data/ehs_journal.db"
```

### Redeployment After Updates

```bash
# Ensure you're on main1 branch with latest changes
git checkout main1
git pull origin main1

# Deploy the updated application
fly deploy

# Monitor deployment logs
fly logs
```

### Troubleshooting Fly.io Deployment

1. **Outdated template served:**
   - Verify you're deploying from main1 branch: `git branch --show-current`
   - Check Docker cache: `fly deploy --no-cache`

2. **Port connection errors:**
   - Verify `internal_port = 8080` in fly.toml
   - Check Dockerfile exposes port 8080
   - Ensure uvicorn starts on port 8080

3. **Static files not loading:**
   - Confirm Dockerfile copies `frontend/static` and `frontend/templates`
   - Check build logs: `fly logs`

4. **Application won't start:**
   ```bash
   # Check deployment status
   fly status
   
   # View application logs
   fly logs
   
   # Connect to container for debugging
   fly ssh console
   ```

## Docker Deployment

### Quick Start (All Platforms)
```bash
docker compose up -d
```

### Database Options
The system now supports three database backends:

1. **SQLite** (default for development)
   ```bash
   # No additional setup required - works out of the box
   python -m backend.main
   ```

2. **PostgreSQL** (recommended for production)
   ```bash
   # Using Docker Compose
   docker compose up -d
   
   # Or Windows-optimized
   docker compose -f docker-compose.windows.yml up -d
   ```

3. **MS SQL Server** (Windows enterprise environments)
   ```bash
   # Using SQL Server Docker Compose
   docker compose -f docker-compose.mssql.yml up -d
   ```

### Windows Deployment
For Windows users, we provide multiple deployment options optimized for Windows environments:

#### Option 1: PowerShell Script (Recommended)
```powershell
# Start in production mode with PostgreSQL (recommended)
.\start-ehs.ps1

# Start with MS SQL Server
.\start-ehs.ps1 -Database mssql

# Start in development mode
.\start-ehs.ps1 -Mode development

# Force rebuild
.\start-ehs.ps1 -Build

# Check status
.\start-ehs.ps1 -Status

# Stop services
.\start-ehs.ps1 -Stop
```

#### Option 2: Direct Docker Compose
```powershell
# PostgreSQL (Windows-optimized)
docker compose -f docker-compose.windows.yml up -d

# MS SQL Server
docker compose -f docker-compose.mssql.yml up -d

# Simple development setup
docker compose -f docker-compose-simple.yml up -d
```

#### Option 3: Native Windows Installation
```powershell
# 1. Install dependencies
python -m pip install -r requirements.txt

# 2. Configure environment
copy .env.example .env
# Edit .env file with your preferred database settings

# 3. Run the application
python -m backend.main
```

**Windows-Specific Features:**
- Proper volume mount handling for Windows Docker
- Support for Windows file paths and line endings
- MS SQL Server integration with Windows authentication
- PowerShell deployment scripts
- Optimized Docker configurations for Windows containers

See [WINDOWS_DEPLOYMENT.md](WINDOWS_DEPLOYMENT.md) for detailed Windows-specific instructions and troubleshooting.

## Project Structure

The codebase is organized into a clean, modular structure:

```
ehs-electronic-journal/
├── backend/                 # FastAPI application (main entry point)
│   ├── main.py             # Application entry point
│   ├── auth/               # Authentication & JWT handling
│   ├── models/             # SQLAlchemy database models
│   ├── routes/             # API route handlers
│   └── utils/              # Utility functions & validation
├── frontend/               # Static files & templates
│   ├── static/             # CSS, JS, and assets
│   └── templates/          # Jinja2 HTML templates
├── database/               # Database schemas & migrations
├── docker/                 # Docker configuration files
└── requirements.txt        # Python dependencies
```

**Entry Points:**
- Main application: `python -m backend.main`
- Docker development: `backend.main:app`
- All imports use `backend.` prefix for clarity

**Key Changes:**
- Eliminated duplicate `backend/app/` directory
- Unified import structure with `backend.` prefix
- Single FastAPI entry point at `backend/main.py`
- Proper static/template path references

## System Architecture

### Backend (FastAPI)
- **Framework**: FastAPI with SQLAlchemy ORM
- **Authentication**: JWT tokens with role-based access
- **Database**: PostgreSQL with history tracking
- **Timezone**: EST (UTC-5) with automatic conversion

### Frontend (HTML/CSS/JS)
- **Templates**: Jinja2 with responsive design
- **Styling**: Professional blue theme (#1a73e8)
- **JavaScript**: Vanilla JS with utility libraries
- **Real-time**: EST clock and live updates

### Database Models
- **Users & Departments**: Role-based authentication
- **Chemical Inventory**: Stock tracking with history
- **Reagents**: MM, Pb, and TCLP reagent management
- **Standards**: MM and FlameAA standards preparation
- **Equipment**: Calibration and maintenance tracking
- **Maintenance**: ICP-OES and equipment logs

## User Roles

- **Admin**: Full system access and user management
- **Manager**: Department oversight and approvals
- **Lab Tech**: Equipment operation and maintenance
- **User**: Standard laboratory operations
- **Read Only**: View-only access to records

## Key Features

### Chemical Inventory Management
- Real-time quantity tracking
- Expiration date monitoring
- Safety information and storage conditions
- Complete history audit trail

### Reagent Preparation
- MM (Metals) reagents with pH and conductivity
- Pb (Lead) reagents with concentration verification
- TCLP extraction fluids with pH targeting

### Standards Management
- MM standards for ICP analysis
- FlameAA standards with calibration curves
- Volume tracking and usage history

### Equipment Tracking
- Calibration scheduling and records
- Pipette accuracy and precision testing
- Water conductivity monitoring
- Service and maintenance scheduling

### Maintenance Logging
- ICP-OES detailed maintenance records
- Performance verification
- Parts and consumables tracking
- Cost analysis and scheduling

### Analytics Dashboard
- Professional enterprise-style interface with 2-chart layout
- Customizable data visualization with multiple graph types
- Real-time data analysis from all laboratory systems
- Export capabilities and preset management
- Integrated reminders and department notes

![Analytics Dashboard](https://github.com/user-attachments/assets/4dd2d1d8-3419-4592-97fb-37f746358ca2)

### Main Dashboard Overview
- Comprehensive laboratory management dashboard with modern enterprise theme
- Real-time status cards for all major system components
- Global sidebar navigation with collapsible sections
- Professional high-contrast blue color scheme (#1d4ed8)
- Responsive design optimized for desktop and mobile use

![Main Dashboard](https://github.com/user-attachments/assets/a1daef67-1a09-4c36-aef4-f4feb2afce2c)

### Standards Management
- MM (Multi-Metal) and FlameAA standards tracking
- Concentration verification and certification management
- Batch tracking with expiration date monitoring
- Advanced search and filtering capabilities
- Professional CRUD forms with comprehensive validation

### Equipment Management
- Complete laboratory equipment tracking and calibration
- Specialized pipette accuracy and precision testing
- Water conductivity monitoring with quality guidelines
- Maintenance scheduling and reminder system
- Performance verification and compliance documentation

### Maintenance Management
- ICP-OES specific maintenance record keeping
- Preventive and corrective maintenance tracking
- Parts usage and cost analysis
- Performance verification workflows
- Comprehensive maintenance dashboard with status overview

### Waste Management
- Laboratory waste container tracking
- Disposal compliance documentation
- Real-time capacity monitoring with visual indicators
- Waste type classification and handling procedures
- Complete audit trail for regulatory compliance

## API Documentation

When running the development server, API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

*Note: For Fly.io deployments, the application runs on port 8080, but Fly.io handles the port mapping automatically.*

## Database Migration

### PostgreSQL to SQL Server
The system includes SQL Server migration markers in the code and a complete SQL Server schema at `database/sqlserver/schema.sql`.

Key differences handled:
- SERIAL → IDENTITY(1,1)
- TIMESTAMP WITH TIME ZONE → DATETIME2
- func.now() → GETUTCDATE()
- VARCHAR → NVARCHAR
- TEXT → NTEXT
- BOOLEAN → BIT

### Database Configuration Environment Variables
```bash
# Database Type Selection
DATABASE_TYPE=sqlite|postgresql|mssql

# PostgreSQL Settings
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_DATABASE=ehs_electronic_journal
POSTGRES_USER=ehs_user
POSTGRES_PASSWORD=ehs_password

# MS SQL Server Settings
MSSQL_SERVER=localhost
MSSQL_PORT=1433
MSSQL_DATABASE=ehs_electronic_journal
MSSQL_USER=ehs_user
MSSQL_PASSWORD=EhsPassword123!
MSSQL_DRIVER=ODBC Driver 18 for SQL Server
```

## Troubleshooting

### Windows-Specific Issues

**1. Requirements Installation Errors**
```powershell
# If you encounter UTF-16 encoding errors:
# The requirements.txt has been fixed for cross-platform compatibility
pip install -r requirements.txt
```

**2. Docker Volume Mount Issues on Windows**
```powershell
# Use the Windows-optimized Docker Compose file:
docker compose -f docker-compose.windows.yml up -d

# Or specify bind mount explicitly:
# Volumes are configured with proper Windows path handling
```

**3. MS SQL Server Connection Issues**
```powershell
# Ensure SQL Server is running and accepts connections
# Check MSSQL_DRIVER in .env matches your installed ODBC driver
# Common drivers: "ODBC Driver 18 for SQL Server", "ODBC Driver 17 for SQL Server"

# Test connection:
python -c "import pyodbc; print('PyODBC available')"
```

**4. Line Ending Issues (CRLF vs LF)**
```bash
# All project files use LF endings for cross-platform compatibility
# Git should handle this automatically with proper .gitattributes configuration
```

### General Issues

**1. Import Errors**
```bash
# Run from project root using module syntax:
python -m backend.main

# Ensure all dependencies are installed:
pip install -r requirements.txt
```

**2. Database Connection Errors**
```bash
# Check .env configuration
# Verify database server is running
# Test connection manually
```

**3. Port Already in Use**
```bash
# Find process using port 8000:
# Windows: netstat -ano | findstr :8000
# Linux: lsof -i :8000

# Change port in .env:
PORT=8001
```

## Security Considerations

### Development
- Default admin password should be changed immediately
- Secret key must be changed in production
- Database credentials should be unique

### Production
- Use HTTPS with SSL certificates
- Enable database encryption
- Implement backup strategies
- Regular security updates

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Create Pull Request

## Support

For technical support or questions:
- Create GitHub issue for bugs
- Review documentation in `/docs` folder
- Contact system administrator

## License

This project is proprietary software for EHS Labs Environmental Hazards Services.

## Version History

- **v1.5.0** - Major UI/UX modernization and feature expansion
  - Extended modern enterprise theme to all sections (Standards, Equipment, Maintenance, Waste)
  - Implemented comprehensive global sidebar navigation
  - Added professional high-contrast color scheme with responsive design
  - Created advanced CRUD forms with real-time validation and user feedback
  - Enhanced performance with optimized asset loading
  - Integrated sophisticated filtering, search, and export capabilities
  - Added specialized modules for pipette testing and water conductivity monitoring
  - Implemented waste management system with compliance tracking
  - Enhanced maintenance management with ICP-OES specific workflows

- **v1.0.0** - Initial release with core functionality
  - User authentication and role-based access control
  - Chemical inventory tracking with history
  - Reagents and standards management
  - Basic equipment and maintenance logging
  - Real-time EST timezone handling
  - Professional UI foundation
