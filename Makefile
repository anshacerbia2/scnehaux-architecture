.PHONY: lint test install-hooks generate-docs all

all: install-hooks generate-docs lint test

install-hooks:
	python scripts/install-hooks.py

generate-docs:
	python scripts/generate_rules_doc.py

lint:
	python linter.py --target .

test:
	pytest validators/tests/
