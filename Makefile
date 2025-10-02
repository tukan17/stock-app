.PHONY: help install dev test lint clean build

help:
	@echo "Available commands:"
	@echo "  install  - Install dependencies"
	@echo "  dev      - Run development server"
	@echo "  test     - Run tests"
	@echo "  lint     - Run linters"
	@echo "  clean    - Clean up temporary files"
	@echo "  build    - Build Docker image"

install:
	pip install -r requirements.txt

dev:
	uvicorn app.main:app --reload

test:
	pytest

lint:
	flake8 app tests
	black app tests
	isort app tests

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".eggs" -exec rm -rf {} +
	find . -type d -name "build" -exec rm -rf {} +
	find . -type d -name "dist" -exec rm -rf {} +

build:
	docker build -t stock-app .