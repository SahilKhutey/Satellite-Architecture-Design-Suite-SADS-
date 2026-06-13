FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir fastapi uvicorn httpx pydantic

# Copy directories
COPY ./apps /app/apps
COPY ./services/gateway-service /app/services/gateway-service

EXPOSE 8000

CMD ["uvicorn", "services.gateway-service.main:app", "--host", "0.0.0.0", "--port", "8000"]
