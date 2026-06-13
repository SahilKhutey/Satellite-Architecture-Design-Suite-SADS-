FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir fastapi uvicorn pydantic numpy scipy
COPY ./engines /app/engines
COPY ./scientific /app/scientific
COPY ./ai /app/ai
COPY ./services /app/services
EXPOSE 8006
CMD ["uvicorn", "services.ai-copilot-service.main:app", "--host", "0.0.0.0", "--port", "8006"]

