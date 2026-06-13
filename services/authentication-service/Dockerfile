FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir fastapi uvicorn PyJWT pydantic cryptography

# Copy app code
COPY ./services/authentication-service /app/services/authentication-service

EXPOSE 8001

CMD ["uvicorn", "services.authentication-service.main:app", "--host", "0.0.0.0", "--port", "8001"]
