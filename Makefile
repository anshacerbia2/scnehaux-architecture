.PHONY: lint test install-hooks generate-docs all coverage docker-build docker-run

all: install-hooks generate-docs lint test

install-hooks:
	python 06-fitness-function/scripts/install-hooks.py

generate-docs:
	python 06-fitness-function/generators/generate_rules_doc.py
	python 06-fitness-function/generators/generate_functions_doc.py

lint:
	python 06-fitness-function/engine/cli.py --target .

test:
	python -m pytest

coverage:
	python -m pytest

docker-build:
	docker build -t scnehaux-linter:test .

docker-run:
	docker run --rm -v "$$(pwd):/docs" scnehaux-linter:test --target /docs
