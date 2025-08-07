# Windows Docker Deployment Guide

## Overview
This guide provides comprehensive instructions for deploying the EHS Electronic Journal on Windows using Docker Desktop.

## Prerequisites

### Required Software
1. **Docker Desktop for Windows** (latest version)
   - Download from: https://docs.docker.com/desktop/install/windows-install/
   - Ensure WSL 2 is installed and enabled
   - Minimum 4GB RAM allocated to Docker

2. **Git for Windows** (optional but recommended)
   - Download from: https://git-scm.com/download/win

### System Requirements
- Windows 10/11 Pro, Enterprise, or Education (64-bit)
- WSL 2 feature enabled
- Hyper-V enabled (if using Hyper-V backend)
- 8GB RAM minimum (16GB recommended)
- 10GB free disk space

## Installation Steps

### 1. Clone the Repository
```powershell
git clone https://github.com/labrat420-69/ehs-electronic-journal.git
cd ehs-electronic-journal
```

### 2. Environment Configuration
Copy the environment template:
```powershell
copy .env.example .env
```

Edit `.env` file with your preferred settings:
- Change `SECRET_KEY` to a secure random string
- Adjust database credentials if needed
- Set `DEBUG=false` for production

### 3. Windows-Specific Deployment

#### Option A: Production Deployment (Recommended)
```powershell
docker compose -f docker-compose.windows.yml up -d
```

#### Option B: Development Deployment
```powershell
docker compose -f docker-compose-simple.yml up -d
```

#### Option C: Full Production with Nginx
```powershell
docker compose up -d
```

### 4. Verify Deployment
Check all services are running:
```powershell
docker compose ps
```

Access the application:
- **HTTP**: http://localhost:8000
- **HTTPS**: https://localhost (if using nginx)
- **Database**: localhost:5432
- **Redis**: localhost:6379

## Windows-Specific Configurations

### Volume Mounts
The Windows deployment uses explicit bind mount syntax for better compatibility:
```yaml
volumes:
  - type: bind
    source: ./backend
    target: /app/backend
    read_only: true
```

### SSL Certificates
Self-signed certificates are included for development. For production:

1. Replace certificates in `docker/ssl/`:
   ```powershell
   # Generate new certificates
   openssl req -x509 -nodes -days 365 -newkey rsa:2048 ^
     -keyout docker/ssl/ehs-journal.key ^
     -out docker/ssl/ehs-journal.crt ^
     -subj "/C=US/ST=YourState/L=YourCity/O=YourOrg/CN=yourdomain.com"
   ```

### File Permissions
Windows file permissions are handled automatically by Docker Desktop. No manual configuration needed.

## Troubleshooting

### Common Issues

#### 1. Port Conflicts
If ports 80, 443, 5432, or 8000 are in use:
```powershell
# Check port usage
netstat -an | findstr :8000
```

Edit docker-compose files to use different ports:
```yaml
ports:
  - "8001:8000"  # Change host port
```

#### 2. Volume Mount Issues
Ensure Docker Desktop has access to the project directory:
1. Open Docker Desktop
2. Go to Settings > Resources > File Sharing
3. Add your project directory

#### 3. WSL 2 Issues
If experiencing slow performance:
1. Ensure project is in WSL 2 filesystem (not Windows filesystem)
2. Use `\\wsl$\Ubuntu\home\username\project` path structure

#### 4. Memory Issues
Increase Docker Desktop memory allocation:
1. Open Docker Desktop Settings
2. Go to Resources > Advanced
3. Increase Memory to 8GB or more

### Service-Specific Troubleshooting

#### Backend Service Issues
```powershell
# Check backend logs
docker compose logs backend

# Restart backend service
docker compose restart backend
```

#### Database Connection Issues
```powershell
# Check PostgreSQL status
docker compose logs postgres

# Test database connection
docker compose exec postgres psql -U ehs_user -d ehs_electronic_journal
```

#### SSL/HTTPS Issues
```powershell
# Check nginx logs
docker compose logs nginx

# Test SSL configuration
curl -k https://localhost
```

## Maintenance Commands

### Start Services
```powershell
docker compose up -d
```

### Stop Services
```powershell
docker compose down
```

### Update Application
```powershell
# Pull latest changes
git pull origin main

# Rebuild and restart
docker compose down
docker compose up -d --build
```

### Backup Database
```powershell
# Create backup
docker compose exec postgres pg_dump -U ehs_user ehs_electronic_journal > backup.sql

# Restore backup
docker compose exec -T postgres psql -U ehs_user ehs_electronic_journal < backup.sql
```

### View Logs
```powershell
# All services
docker compose logs

# Specific service
docker compose logs backend

# Follow logs
docker compose logs -f backend
```

## Production Deployment Checklist

- [ ] Change default passwords in `.env`
- [ ] Generate secure `SECRET_KEY`
- [ ] Replace self-signed SSL certificates
- [ ] Configure proper domain names
- [ ] Set up log rotation
- [ ] Configure backup procedures
- [ ] Enable firewall rules
- [ ] Configure monitoring

## Performance Optimization

### Docker Desktop Settings
1. **Memory**: Allocate 8GB+ RAM
2. **CPU**: Use all available cores
3. **Disk**: Use SSD storage
4. **WSL 2**: Keep files in Linux filesystem

### Application Settings
1. **Environment Variables**:
   - Set `DEBUG=false`
   - Configure proper `DATABASE_URL`
   - Set production `SECRET_KEY`

2. **Database Optimization**:
   - Use connection pooling
   - Configure PostgreSQL settings
   - Regular vacuum operations

## Security Considerations

### Network Security
- Use internal Docker networks
- Expose only necessary ports
- Configure firewall rules

### Application Security
- Regular security updates
- Strong authentication
- SSL/TLS encryption
- Regular backups

### Container Security
- Run as non-root user
- Use minimal base images
- Regular image updates
- Scan for vulnerabilities

## Support

### Getting Help
1. Check Docker Desktop logs
2. Review application logs
3. Check this documentation
4. Submit GitHub issues

### Useful Commands
```powershell
# System information
docker system info

# Container resource usage
docker stats

# Clean up unused resources
docker system prune -f

# Remove all containers and start fresh
docker compose down -v
docker system prune -a -f
```

## Version History
- v1.0: Initial Windows deployment configuration
- v1.1: Added SSL support and troubleshooting guide
- v1.2: Enhanced security and performance recommendations