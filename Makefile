.PHONY: lint test install-hooks generate-docs all

all: install-hooks generate-docs lint test

install-hooks:
	python scripts/install-hooks.py

generate-docs:
	python scripts/generate_rules_doc.py

lint:
	python linter.py --target .

test:
	python -m pytest

coverage:
	python -m pytest --cov=validators --cov=linter --cov-fail-under=94 --cov-report=term-missing validators/tests/

docker-build:
	docker build -t scnehaux-linter:test .

docker-run:
	docker run --rm -v "$$(pwd):/docs" scnehaux-linter:test --target /docs
