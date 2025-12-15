.PHONY: install test lint run clean

install:
	uv sync

test:
	uv run pytest tests/ -v

lint:
	uv run ruff check src/ tests/
	uv run ruff format --check src/ tests/

format:
	uv run ruff format src/ tests/

run:
	uv run claude-md-research --help

clean:
	rm -rf results/raw/* results/metrics/* results/charts/*
	find . -type d -name __pycache__ -exec rm -rf {} +
