# EHS Electronic Journal - Windows Startup Script
# This script helps Windows users start the EHS Electronic Journal system using Docker

param(
    [string]$Mode = "production",
    [switch]$Build = $false,
    [switch]$Logs = $false,
    [switch]$Stop = $false,
    [switch]$Status = $false,
    [switch]$Help = $false
)

function Show-Help {
    Write-Host "EHS Electronic Journal - Windows Deployment Script" -ForegroundColor Green
    Write-Host ""
    Write-Host "Usage: .\start-ehs.ps1 [OPTIONS]" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Options:" -ForegroundColor Cyan
    Write-Host "  -Mode <mode>     Deployment mode: 'production', 'development', or 'simple'" -ForegroundColor White
    Write-Host "                   Default: production"
    Write-Host "  -Build           Force rebuild of Docker images"
    Write-Host "  -Logs            Show logs after starting services"
    Write-Host "  -Stop            Stop all services"
    Write-Host "  -Status          Show status of all services"
    Write-Host "  -Help            Show this help message"
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Cyan
    Write-Host "  .\start-ehs.ps1                    # Start in production mode"
    Write-Host "  .\start-ehs.ps1 -Mode development  # Start in development mode"
    Write-Host "  .\start-ehs.ps1 -Build             # Rebuild and start"
    Write-Host "  .\start-ehs.ps1 -Stop              # Stop all services"
    Write-Host "  .\start-ehs.ps1 -Status            # Check service status"
    Write-Host ""
}

function Test-DockerInstallation {
    try {
        $dockerVersion = docker --version
        Write-Host "✓ Docker found: $dockerVersion" -ForegroundColor Green
        
        $composeVersion = docker compose version
        Write-Host "✓ Docker Compose found: $composeVersion" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "✗ Docker not found. Please install Docker Desktop for Windows." -ForegroundColor Red
        Write-Host "Download from: https://docs.docker.com/desktop/install/windows-install/" -ForegroundColor Yellow
        return $false
    }
}

function Get-ComposeFile {
    param([string]$mode)
    
    switch ($mode.ToLower()) {
        "production" { return "docker-compose.yml" }
        "windows" { return "docker-compose.windows.yml" }
        "development" { return "docker-compose-simple.yml" }
        "simple" { return "docker-compose-simple.yml" }
        default { return "docker-compose.windows.yml" }
    }
}

function Start-Services {
    param([string]$composeFile, [bool]$rebuild)
    
    Write-Host "Starting EHS Electronic Journal services..." -ForegroundColor Green
    Write-Host "Using configuration: $composeFile" -ForegroundColor Cyan
    
    $buildFlag = if ($rebuild) { "--build" } else { "" }
    
    try {
        if ($rebuild) {
            Write-Host "Building services..." -ForegroundColor Yellow
            docker compose -f $composeFile up -d --build
        } else {
            docker compose -f $composeFile up -d
        }
        
        Write-Host "✓ Services started successfully!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Access points:" -ForegroundColor Cyan
        Write-Host "  • Application: http://localhost:8000" -ForegroundColor White
        Write-Host "  • HTTPS (if nginx): https://localhost" -ForegroundColor White
        Write-Host "  • Database: localhost:5432" -ForegroundColor White
        Write-Host ""
        Write-Host "To view logs: .\start-ehs.ps1 -Logs" -ForegroundColor Yellow
        Write-Host "To stop services: .\start-ehs.ps1 -Stop" -ForegroundColor Yellow
        
    } catch {
        Write-Host "✗ Failed to start services: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
}

function Stop-Services {
    Write-Host "Stopping EHS Electronic Journal services..." -ForegroundColor Yellow
    
    try {
        # Try to stop using all possible compose files
        $composeFiles = @("docker-compose.yml", "docker-compose.windows.yml", "docker-compose-simple.yml")
        
        foreach ($file in $composeFiles) {
            if (Test-Path $file) {
                docker compose -f $file down 2>$null
            }
        }
        
        Write-Host "✓ Services stopped successfully!" -ForegroundColor Green
    } catch {
        Write-Host "✗ Error stopping services: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Show-Status {
    Write-Host "EHS Electronic Journal - Service Status" -ForegroundColor Green
    Write-Host "=======================================" -ForegroundColor Green
    Write-Host ""
    
    try {
        docker compose ps
        Write-Host ""
        Write-Host "Container resource usage:" -ForegroundColor Cyan
        docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
    } catch {
        Write-Host "✗ Error getting status: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Show-Logs {
    Write-Host "Showing logs for all services (Press Ctrl+C to exit)..." -ForegroundColor Green
    docker compose logs -f
}

# Main script execution
if ($Help) {
    Show-Help
    exit 0
}

# Check if Docker is installed
if (-not (Test-DockerInstallation)) {
    exit 1
}

# Change to script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

Write-Host "EHS Electronic Journal - Windows Deployment" -ForegroundColor Green
Write-Host "===========================================" -ForegroundColor Green
Write-Host ""

if ($Stop) {
    Stop-Services
    exit 0
}

if ($Status) {
    Show-Status
    exit 0
}

if ($Logs) {
    Show-Logs
    exit 0
}

# Get the appropriate compose file
$composeFile = Get-ComposeFile -mode $Mode

if (-not (Test-Path $composeFile)) {
    Write-Host "✗ Compose file not found: $composeFile" -ForegroundColor Red
    Write-Host "Available modes: production, development, simple, windows" -ForegroundColor Yellow
    exit 1
}

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "⚠ No .env file found. Creating from template..." -ForegroundColor Yellow
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "✓ Created .env from .env.example" -ForegroundColor Green
        Write-Host "⚠ Please review and update .env file with your settings" -ForegroundColor Yellow
    } else {
        Write-Host "✗ No .env.example found. Please create .env file manually." -ForegroundColor Red
    }
}

# Start services
Start-Services -composeFile $composeFile -rebuild $Build