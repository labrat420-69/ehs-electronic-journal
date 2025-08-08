FROM python:3.11-slim
WORKDIR /app

# Copy requirements first for Docker cache efficiency
COPY requirements.txt .

# Install Python dependencies with SSL cert bypass for environments with cert issues
RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt

# Copy the launch script if it exists
COPY launch.py ./launch.py

# Copy your backend code, frontend templates, and static files
COPY backend ./backend
COPY frontend/templates ./frontend/templates
COPY frontend/static ./frontend/static

EXPOSE 8000

# Use uvicorn to start the FastAPI app
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
