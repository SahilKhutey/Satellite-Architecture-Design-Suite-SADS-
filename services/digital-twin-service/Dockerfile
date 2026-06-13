FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir fastapi uvicorn pydantic numpy scipy
COPY ./engines /app/engines
COPY ./scientific /app/scientific
COPY ./services /app/services
EXPOSE 8005
CMD ["uvicorn", "services.digital-twin-service.main:app", "--host", "0.0.0.0", "--port", "8005"]

