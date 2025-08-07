# EHS Electronic Journal - Modern Desktop Laboratory Management System

## Overview
The EHS Electronic Journal is a comprehensive, modern laboratory management system designed for EHS Labs Environmental Hazards Services. This system provides electronic tracking of chemical inventory, reagents, standards, equipment, and maintenance operations with a sleek, desktop-focused interface and advanced data visualization capabilities.

![Enhanced Dashboard](https://github.com/user-attachments/assets/ca0aeffb-681a-434a-9d8e-23a2002661b3)

## 🚀 New Features & Modern Interface

### ✨ Sleek Desktop-Focused Theme
- **Modern Design Language**: Professional interface with enhanced typography, improved color schemes, and smooth animations
- **Responsive Sidebar**: Dark theme with glass morphism effects, collapsible navigation, and shimmer animations
- **Desktop Optimization**: Better horizontal space utilization, reduced vertical scrolling, and grid-based layouts
- **Enhanced Visual Hierarchy**: Improved cards, buttons, and form styling with consistent spacing and shadows

### 📊 Advanced Analytics Dashboard
- **Interactive Charts**: Integrated Plotly.js for dynamic data visualization
- **Chart Builder**: Intuitive interface for creating custom charts with multiple data sources
- **Smart Data Handling**: Automatic 'no data' state detection with helpful guidance
- **Multiple Chart Types**: Line charts, pie charts, bar charts, scatter plots, and histograms

![Analytics Dashboard](https://github.com/user-attachments/assets/cc78c35b-aa71-4ccf-9cc3-af810cc2ac9e)

### 👤 Profile Picture System
- **User Profiles**: Complete profile management with picture upload functionality
- **Drag & Drop Upload**: Modern file upload interface with preview and validation
- **Smart Avatars**: Automatic avatar generation with user initials as fallback
- **File Management**: PNG/JPG support with 2MB size limit and automatic file handling

### 🎨 Enhanced User Experience
- **Smooth Animations**: CSS transitions and hover effects throughout the interface
- **Visual Feedback**: Loading states, success messages, and interactive elements
- **Consistent Theming**: CSS variables for maintainable and consistent styling
- **Accessibility**: Improved color contrast and keyboard navigation

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
   
   # Additional packages for enhanced features
   pip install plotly pandas openpyxl  # For analytics and data export
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
- **Database**: PostgreSQL with history tracking (SQLite for development)
- **File Handling**: Profile picture upload with validation and storage management
- **API Design**: RESTful endpoints with OpenAPI documentation
- **Timezone**: EST (UTC-5) with automatic conversion

### Frontend (Modern HTML/CSS/JS)
- **Templates**: Jinja2 with responsive design and modern aesthetics
- **Styling**: Enhanced CSS with CSS variables, animations, and glass morphism effects
- **Typography**: Inter font family with improved readability
- **JavaScript**: Vanilla JS with Plotly.js for data visualization
- **Real-time**: EST clock, live updates, and interactive charts
- **Theme**: Sleek desktop-focused design with professional blue color scheme

### Enhanced Features
- **Data Visualization**: Plotly.js integration for interactive charts and analytics
- **Profile Management**: Complete user profile system with picture upload
- **Modern UI Components**: Enhanced cards, buttons, forms, and navigation
- **Performance**: Optimized asset loading and efficient CSS architecture
- **Accessibility**: Improved color contrast and user experience

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

### 📊 Analytics & Data Visualization
- **Interactive Charts**: Create custom charts from laboratory data using Plotly.js
- **Chart Builder**: Intuitive interface for selecting data sources and configuring visualizations
- **Multiple Chart Types**: Line, pie, bar, scatter, area, and histogram charts
- **Data Analysis**: Activity timelines and inventory distribution analytics
- **Smart Data Handling**: Automatic detection of insufficient data with user guidance

### 👤 User Profile Management
- **Profile Pictures**: Upload and manage user profile pictures with drag & drop interface
- **File Validation**: PNG/JPG support with 2MB size limit and automatic validation
- **Smart Avatars**: Automatic generation of avatar initials as fallback
- **Profile Information**: Complete user profile management with account details

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

## API Documentation

When running the development server, API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### New API Endpoints

#### Analytics API
- `GET /api/analytics/data-availability` - Check if sufficient data exists for charts
- `GET /api/analytics/activity-timeline` - Get activity timeline data for line charts
- `GET /api/analytics/inventory-distribution` - Get inventory distribution for pie charts

#### Profile Management API
- `POST /auth/profile-picture` - Upload user profile picture
- `DELETE /auth/profile-picture` - Delete user profile picture
- `GET /api/profile-picture/{filename}` - Serve profile picture files
- `GET /auth/profile` - User profile management page

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

- **v2.0.0** - Major UI/UX Enhancement & Feature Expansion
  - 🎨 Complete theme refactoring with sleek, desktop-focused design
  - 📊 Advanced analytics dashboard with Plotly.js integration
  - 👤 Profile picture system with drag & drop upload
  - ✨ Enhanced sidebar with glass morphism and smooth animations
  - 🚀 Modern CSS architecture with variables and improved performance
  - 📱 Better responsive design and desktop optimization
  - 🎯 Improved user experience with visual feedback and transitions

- **v1.0.0** - Initial release with core functionality
  - User authentication and role management
  - Chemical inventory tracking
  - Reagents and standards management
  - Equipment and maintenance logging
  - Real-time EST timezone handling
  - Professional UI with responsive design
