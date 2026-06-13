# SADS Monorepo Makefile

.PHONY: install dev test lint clean help docker-up docker-down

help:
	@echo "Available commands:"
	@echo "  install        - Install all workspace dependencies"
	@echo "  dev            - Start the API server serving both web assets and services"
	@echo "  test           - Run Python engine and service unit tests"
	@echo "  lint           - Run code style formatters and lints"
	@echo "  clean          - Remove build caches and temporary python files"
	@echo "  docker-up      - Run services using Docker Compose"
	@echo "  docker-down    - Tear down Docker Compose services"

install:
	pip install -r requirements.txt || pip install fastapi uvicorn pydantic pytest numpy scipy

dev:
	python -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload

test:
	python -m pytest tests/

lint:
	python -m black --check api/ engines/ services/ tests/
	python -m ruff check api/ engines/ services/ tests/

clean:
	python -c "import shutil, pathlib; [shutil.rmtree(p) for p in pathlib.Path('.').rglob('__pycache__')]"
	python -c "import shutil, pathlib; [shutil.rmtree(p) for p in pathlib.Path('.').rglob('.pytest_cache')]"
	python -c "import shutil, pathlib; [p.unlink() for p in pathlib.Path('.').rglob('*.pyc')]"

docker-up:
	docker-compose up --build -d

docker-down:
	docker-compose down
