.PHONY: help install install-dev test test-cov lint format type-check clean run setup build publish publish-test

help: ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	pip install -r requirements.txt

install-dev: ## Install development dependencies
	pip install -r requirements-dev.txt
	pip install build twine

test: ## Run tests
	pytest tests/

test-cov: ## Run tests with coverage
	pytest tests/ --cov=linkding_mcp_server --cov-report=term-missing --cov-report=html

lint: ## Run linting
	ruff check linkding_mcp_server/ tests/

format: ## Format code with black and ruff
	black linkding_mcp_server/ tests/
	ruff check --fix linkding_mcp_server/ tests/

type-check: ## Run type checking with mypy
	mypy linkding_mcp_server/ --ignore-missing-imports

clean: ## Clean up generated files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info
	rm -rf linkding_mcp_server.egg-info

run: ## Run the server
	python -m linkding_mcp_server

setup: ## Initial setup (install deps and create .env)
	pip install -r requirements.txt
	@if [ ! -f .env ]; then \
		cp .env.sample .env; \
		echo "Created .env file. Please edit it with your LinkDing configuration."; \
	else \
		echo ".env file already exists."; \
	fi

build: clean ## Build distribution packages
	python -m build

publish-test: build ## Publish to TestPyPI
	python -m twine upload --repository testpypi dist/*

publish: build ## Publish to PyPI
	python -m twine upload dist/*