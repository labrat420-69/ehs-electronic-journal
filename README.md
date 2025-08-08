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

4. **Set up PostgreSQL database:**
   ```bash
   # Create database
   createdb ehs_electronic_journal
   
   # Run schema
   psql -d ehs_electronic_journal -f database/postgresql/schema.sql
   ```

5. **Run the application:**
   ```bash
   cd backend
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Access the application:**
   - Open browser to: http://localhost:8000
   - Default admin login: admin / admin123!

## Docker Deployment

### Quick Start (All Platforms)
```bash
docker compose up -d
```

### Windows Deployment
For Windows users, we provide a PowerShell script for easy deployment:

```powershell
# Start in production mode (recommended)
.\start-ehs.ps1

# Start in development mode
.\start-ehs.ps1 -Mode development

# Force rebuild
.\start-ehs.ps1 -Build

# Check status
.\start-ehs.ps1 -Status

# Stop services
.\start-ehs.ps1 -Stop
```

See [WINDOWS_DEPLOYMENT.md](WINDOWS_DEPLOYMENT.md) for detailed Windows-specific instructions.

### Development with Docker
```bash
docker compose -f docker-compose-simple.yml up -d
```

### Production Deployment
```bash
# Standard production
docker compose up -d

# Windows-optimized production
docker compose -f docker-compose.windows.yml up -d
```

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
