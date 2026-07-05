.PHONY: lint lint-code format test install-hooks generate-docs all coverage docker-build docker-run clean

# Run all processes (setup, generate docs, linting, and testing)
all: install install-hooks generate-docs lint test

# Install Python dependencies into the local environment
install:
	pip install -e .[dev]

# Install the Git hook script to block dirty/unformatted commits
install-hooks:
	python 06-fitness-function/scripts/install-hooks.py

# Automatically build/update all Markdown documents sourced from JSON Schemas or scripts
generate-docs:
	python 06-fitness-function/generators/generate_rules_doc.py
	python 06-fitness-function/generators/generate_functions_doc.py
	python 06-fitness-function/generators/generate_engine_topography.py
	python 06-fitness-function/generators/generate_adr_index.py
	python 06-fitness-function/generators/generate_pad_sad_index.py
	python 06-fitness-function/generators/generate_traceability_graph.py

# Run the core architecture linter to validate document compliance (C4, NFRs, etc.)
lint:
	python 06-fitness-function/engine/cli.py --target .

# Run the architecture linter and output the results in SARIF format (for GitHub Code Scanning)
lint-sarif:
	python 06-fitness-function/engine/cli.py --format sarif > linter.sarif

# Check for expired architecture exception waivers based on the current date
check-waivers:
	python 06-fitness-function/scripts/waiver-expiry-check.py

# Auto-format Python code using Ruff
format-code:
	ruff check --fix 06-fitness-function/
	ruff format 06-fitness-function/

# Auto-format Markdown & JSON documents using Prettier
format-docs:
	npx prettier --write "**/*.md" "**/*.json"

# Auto-format ALL files (Python, Markdown, and JSON) at once
format: format-code format-docs

# Check Python code formatting (no auto-fix, used by CI/CD & Git hooks)
lint-code:
	ruff check 06-fitness-function/
	ruff format --check 06-fitness-function/

# Check document formatting (no auto-fix, used by CI/CD & Git hooks)
lint-docs-format:
	npx prettier --check "**/*.md" "**/*.json"

# Run unit tests for the linter engine (using pytest)
test:
	python -m pytest

# Run unit tests and generate an HTML coverage report
coverage:
	python -m pytest --cov-report html
	@echo "Open htmlcov/index.html in your browser to view the detailed results."

# Clean up cache and junk files (pycache, pytest_cache, coverage data)
clean:
ifeq ($(OS),Windows_NT)
	if exist .pytest_cache rd /s /q .pytest_cache
	if exist .coverage del .coverage
	if exist htmlcov rd /s /q htmlcov
	if exist .ruff_cache rd /s /q .ruff_cache
	for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
else
	rm -rf .pytest_cache .coverage htmlcov .ruff_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
endif

# Build a Docker Image for the linter (for isolated execution)
docker-build:
	docker build -t scnehaux-linter:test .

# Run the linter inside the Docker container
docker-run:
	docker run --rm -v "$$(pwd):/docs" scnehaux-linter:test --target /docs
