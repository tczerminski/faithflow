PYTEST_PARAMS=-v -s --cov=alamo --cov-report=html --cov-report=term-missing --no-cov-on-fail\
 --cov-fail-under=72 --cov-branch --junitxml=test-results/junit.xml

.PHONY: compose
compose:
	podman compose up --build

.PHONY: run
run:
	uv run fastapi dev src/app.py

.PHONY: lint
lint:
	ruff check --fix
	ruff format
	uv run ruff check

.PHONY: tests
tests:
	uv run py.test src $(PYTEST_PARAMS) .