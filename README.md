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

### Development with Docker
```bash
docker-compose up -d
```

### Production Deployment
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
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
- Professional enterprise-style interface with customizable chart layouts
- Enhanced chart labels ("Chart 1", "Chart 2", etc.) for clarity
- Customizable data visualization with multiple graph types
- Persistent user dashboard preferences and configurations
- Auto-refresh functionality with user-defined intervals
- Save/restore dashboard layouts across login sessions
- Real-time data analysis from all laboratory systems
- Export capabilities and preset management
- Integrated reminders and department notes

![Analytics Dashboard](https://github.com/user-attachments/assets/0c914c41-2703-47d9-a844-06dedb0cbfcc)

### User Profile Management
- Complete user profile system with picture upload
- Profile picture validation, resizing, and storage
- Secure file upload with type and size validation (JPEG, PNG, GIF, WebP, max 5MB)
- Automatic image resizing to 200x200px thumbnails
- Default avatar support with fallback icons
- Profile integration in sidebar navigation
- Comprehensive profile editing with contact information

![User Profile Features](https://github.com/user-attachments/assets/7a6649a5-b58f-4751-8455-b0995153764c)

### Dashboard Preferences & Persistence
- Complete dashboard preference management system
- Persistent chart type and data source preferences
- Multiple saved dashboard configurations per user
- Auto-refresh with configurable intervals (5, 10, 30 minutes)
- Layout customization with automatic restoration on login
- "No data" state handling with helpful guidance
- Configuration sharing and management

![Dashboard Preferences](https://github.com/user-attachments/assets/4b5821eb-bc55-4cef-a909-df950c331578)

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

## Performance Optimization

### Desktop/Local-Server Performance
The application is optimized for desktop and local-server deployment:

- **Asset Loading**: Static assets (CSS, JS, images) served efficiently with proper caching headers
- **Database Optimization**: SQLAlchemy ORM with connection pooling and query optimization
- **Image Processing**: Automatic profile picture resizing and compression to reduce file sizes
- **JavaScript Optimization**: Modular JavaScript loading with specific functionality per page
- **CSS Optimization**: CSS variables for consistent theming and efficient rendering
- **Auto-refresh**: Configurable intervals to balance real-time data with server load

### Recommended Production Settings
- Enable gzip compression for static assets
- Use database connection pooling (default: 5-20 connections)
- Set appropriate cache headers for static files
- Consider CDN for static assets if deploying across multiple locations
- Monitor auto-refresh intervals to prevent excessive database queries

## Version History

- **v1.1.0** - Enhanced Dashboard & Profile Features
  - Updated analytics chart labels for improved clarity ("Chart 1", "Chart 2")
  - Complete user profile picture upload system with validation
  - Persistent dashboard preferences and configurations
  - Auto-refresh functionality with user-defined intervals
  - Multiple saved dashboard layouts per user
  - Enhanced performance optimization for desktop deployment
  - Comprehensive README updates with new screenshots

- **v1.0.0** - Initial release with core functionality
  - User authentication and role management
  - Chemical inventory tracking
  - Reagents and standards management
  - Equipment and maintenance logging
  - Real-time EST timezone handling
  - Professional UI with responsive design
