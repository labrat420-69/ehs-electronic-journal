FROM python:3.11-slim
WORKDIR /app
COPY frontend/templates ./frontend/templates
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8000
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
