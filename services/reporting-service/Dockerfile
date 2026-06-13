FROM python:3.11-slim
WORKDIR /app/services/reporting-service
RUN pip install --no-cache-dir fastapi uvicorn pydantic
COPY ./services/reporting-service /app/services/reporting-service
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
