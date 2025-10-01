set quiet

default:
    @just --list

install:
    uv sync --all-extras

test:
    uv run pytest

test-contract:
    uv run pytest -m contract

test-integration:
    uv run pytest -m integration

test-unit:
    uv run pytest -m unit

test-benchmark:
    uv run pytest -m benchmark --benchmark-only

test-property:
    uv run pytest -m property

lint:
    uv run ruff check .

format:
    uv run ruff format .

format-check:
    uv run ruff format --check .

typecheck:
    uv run python -m mypy src

clean:
    rm -rf chroma_data/
    rm -rf .pytest_cache
    rm -rf .ruff_cache
    rm -rf **/__pycache__

ci: lint format-check test
