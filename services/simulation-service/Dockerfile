FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir fastapi uvicorn pydantic numpy scipy

# Copy whole repository root to access engines
COPY ./engines /app/engines
COPY ./services /app/services

EXPOSE 8002

CMD ["uvicorn", "services.simulation-service.main:app", "--host", "0.0.0.0", "--port", "8002"]
