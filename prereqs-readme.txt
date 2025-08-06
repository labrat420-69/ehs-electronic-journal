Check that the computer you are using to deploy this has the following distributions downloaded and installed (or available in your environment):

----------------------------------------
DOCKER & DEPENDENCIES CHECKLIST
----------------------------------------

1. Docker Desktop
   # Check if Docker is installed
   docker --version

   # Download if missing:
   # https://www.docker.com/products/docker-desktop/

2. Docker Compose
   # Check if Docker Compose is installed (either command should work)
   docker-compose --version
docker compose version

3. Windows Subsystem for Linux (WSL2) [Windows Only]
   # Check if WSL2 is installed and which distros are present
   wsl --list --verbose

   # Install WSL2 (if missing; run in PowerShell as admin)
   wsl --install

   # Optional: Install Ubuntu from Microsoft Store
   # Search for "Ubuntu" in Microsoft Store and install

   # Update and install basic Linux packages in Ubuntu (run in Ubuntu terminal)
   sudo apt update
   sudo apt install git curl build-essential

4. Git
   # Check if Git is installed
   git --version

   # Download if missing:
   # https://git-scm.com/download/win

5. Node.js & npm (if using a Node.js frontend)
   # Check if Node and npm are installed
   node --version
   npm --version

   # Download if missing:
   # https://nodejs.org/en/download/

6. Python & pip (if using a Python backend)
   # Check if Python and pip are installed
   python --version
   pip --version

7. PostgreSQL Client Tools (optional, for database CLI access)
   # Check if psql is installed
   psql --version

----------------------------------------
Quick Reference: Common Docker Compose Commands (PowerShell)
----------------------------------------

# Change to project directory
Set-Location -Path "C:\Users\Admin\Desktop\ehs-electronic-journal"

# Build and start all services (see logs)
docker-compose up --build

# Build and start in the background (detached)
docker-compose up --build -d

# View logs when running in detached mode
docker-compose logs -f

# Stop all services
docker-compose down

# Build only the backend service (if needed)
docker-compose build backend

# Show running containers
docker-compose ps

----------------------------------------
If you encounter errors or missing tools, install them using the links above or contact your system administrator.