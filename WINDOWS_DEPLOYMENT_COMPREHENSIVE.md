# Windows Deployment Guide for EHS Electronic Journal

This guide provides comprehensive instructions for deploying the EHS Electronic Journal on Windows systems with full Docker and MS SQL Server support.

## System Requirements

### Minimum Requirements
- Windows 10 version 2004 (build 19041) or Windows Server 2019
- Docker Desktop for Windows 4.0+
- 4GB RAM minimum, 8GB recommended
- 10GB free disk space

### Database Options
- **SQLite** (included - no additional setup required)
- **PostgreSQL** (recommended for production)
- **MS SQL Server** (enterprise Windows environments)

## Installation Methods

### Method 1: Docker with PowerShell Script (Recommended)

1. **Install Docker Desktop**
   - Download from: https://www.docker.com/products/docker-desktop
   - Enable WSL 2 backend during installation
   - Restart Windows after installation

2. **Clone the Repository**
   ```powershell
   git clone https://github.com/labrat420-69/ehs-electronic-journal.git
   cd ehs-electronic-journal
   ```

3. **Deploy Using PowerShell Script**
   ```powershell
   # Basic deployment with PostgreSQL
   .\start-ehs.ps1
   
   # Deploy with MS SQL Server
   .\start-ehs.ps1 -Database mssql
   
   # Development mode
   .\start-ehs.ps1 -Mode development
   ```

### Method 2: Manual Docker Compose

1. **Copy Environment Configuration**
   ```powershell
   copy .env.example .env
   # Edit .env file with your preferred settings
   ```

2. **Choose Your Database Backend**

   **PostgreSQL (Default)**
   ```powershell
   # Use Windows-optimized configuration
   docker compose -f docker-compose.windows.yml up -d
   ```

   **MS SQL Server**
   ```powershell
   # Use SQL Server configuration
   docker compose -f docker-compose.mssql.yml up -d
   ```

   **Development Mode**
   ```powershell
   # Simple development setup
   docker compose -f docker-compose-simple.yml up -d
   ```

### Method 3: Native Windows Installation

1. **Install Python 3.11+**
   - Download from: https://www.python.org/downloads/
   - During installation, check "Add Python to PATH"

2. **Install Dependencies**
   ```powershell
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Database Setup**

   **SQLite (Simplest)**
   ```powershell
   # Set in .env file:
   DATABASE_TYPE=sqlite
   # No additional setup required
   ```

   **PostgreSQL**
   ```powershell
   # Install PostgreSQL from https://www.postgresql.org/download/windows/
   # Create database
   createdb ehs_electronic_journal
   # Set in .env:
   DATABASE_TYPE=postgresql
   POSTGRES_SERVER=localhost
   ```

   **MS SQL Server**
   ```powershell
   # Install SQL Server Express or use existing instance
   # Set in .env:
   DATABASE_TYPE=mssql
   MSSQL_SERVER=localhost
   MSSQL_USER=ehs_user
   MSSQL_PASSWORD=YourPassword123!
   ```

4. **Run the Application**
   ```powershell
   python -m backend.main
   ```

## MS SQL Server Configuration

### For SQL Server Express
1. Download SQL Server Express from Microsoft
2. During installation, enable "Mixed Mode Authentication"
3. Set a strong SA password
4. Enable TCP/IP protocol in SQL Server Configuration Manager

### For Existing SQL Server Instances
1. Create database:
   ```sql
   CREATE DATABASE ehs_electronic_journal;
   ```

2. Create user:
   ```sql
   CREATE LOGIN ehs_user WITH PASSWORD = 'YourPassword123!';
   USE ehs_electronic_journal;
   CREATE USER ehs_user FOR LOGIN ehs_user;
   ALTER ROLE db_owner ADD MEMBER ehs_user;
   ```

### Environment Variables for MS SQL Server
```powershell
DATABASE_TYPE=mssql
MSSQL_SERVER=localhost
MSSQL_PORT=1433
MSSQL_DATABASE=ehs_electronic_journal
MSSQL_USER=ehs_user
MSSQL_PASSWORD=YourPassword123!
MSSQL_DRIVER=ODBC Driver 18 for SQL Server
```

## Windows-Specific Configuration

### Docker Volume Mounts
The Windows Docker Compose files use explicit bind mount types for better Windows compatibility:

```yaml
volumes:
  - type: bind
    source: ./backend
    target: /app/backend
    read_only: true
```

### File Path Handling
All configurations handle Windows file paths correctly:
- Volume mounts use forward slashes in Docker contexts
- Environment variables support Windows-style paths
- Line endings are properly handled (LF in containers, CRLF on Windows)

### PowerShell Script Features
The `start-ehs.ps1` script provides:
- Automatic database selection
- Health checking
- Log viewing
- Service management
- Development/production mode switching

## Troubleshooting

### Common Issues

**1. Docker Desktop Not Starting**
```powershell
# Ensure WSL 2 is enabled
wsl --install
# Restart Docker Desktop
```

**2. Port Already in Use**
```powershell
# Find process using port 8000
netstat -ano | findstr :8000
# Kill process or change port in .env
PORT=8001
```

**3. MS SQL Server Connection Issues**
```powershell
# Test SQL Server connectivity
sqlcmd -S localhost -U ehs_user -P YourPassword123! -Q "SELECT 1"

# Check ODBC drivers installed
# Run: odbcad32.exe
# Look for "ODBC Driver 18 for SQL Server"
```

**4. Volume Mount Issues**
```powershell
# Ensure Docker Desktop has access to your drive
# Docker Desktop -> Settings -> Resources -> File Sharing
# Add your project drive (usually C:)
```

**5. Requirements Installation Errors**
```powershell
# If encountering build errors, install Visual Studio Build Tools
# Or use pre-compiled wheels:
pip install --only-binary=all -r requirements.txt
```

### Performance Optimization

**For Production on Windows:**
1. Use SSD storage for Docker volumes
2. Allocate adequate memory to Docker Desktop (8GB+)
3. Use MS SQL Server instead of PostgreSQL for better Windows performance
4. Enable Hyper-V for better container performance

**For Development:**
1. Use SQLite for fastest development iteration
2. Mount only necessary volumes
3. Use development mode Docker compose files

## Security Considerations

### Windows-Specific Security
- Run Docker Desktop as administrator if needed for volume mounts
- Configure Windows Firewall to allow container ports
- Use Windows Credential Manager for database passwords
- Enable BitLocker for data at rest encryption

### Database Security
- Change default passwords in .env file
- Use Windows Authentication for SQL Server when possible
- Enable SSL/TLS for database connections
- Regular security updates for SQL Server

## Backup and Recovery

### SQLite Backup
```powershell
# Simple file copy
copy ehs_journal.db ehs_journal_backup.db
```

### SQL Server Backup
```sql
BACKUP DATABASE ehs_electronic_journal 
TO DISK = 'C:\Backups\ehs_electronic_journal.bak'
```

### Docker Volume Backup
```powershell
docker run --rm -v ehs-electronic-journal_postgres_data:/data -v ${pwd}:/backup busybox tar czf /backup/backup.tar.gz -C /data .
```

## Support and Resources

- **Official Documentation**: See README.md
- **Windows-Specific Issues**: Check this guide first
- **Docker Issues**: https://docs.docker.com/desktop/windows/
- **SQL Server Resources**: https://docs.microsoft.com/sql/

## Version Compatibility

| Component | Minimum Version | Recommended |
|-----------|----------------|-------------|
| Windows | 10 (2004) | 11 |
| Docker Desktop | 4.0 | Latest |
| Python | 3.11 | 3.12 |
| SQL Server | 2019 | 2022 |
| PostgreSQL | 13 | 15 |

## Updates and Maintenance

```powershell
# Update application
git pull origin main
.\start-ehs.ps1 -Build

# Update Docker images
docker compose -f docker-compose.windows.yml pull
```

Regular maintenance tasks:
- Weekly: Check application logs
- Monthly: Update Docker images
- Quarterly: Database maintenance and backup verification
- Annually: Security review and password rotation