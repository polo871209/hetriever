set quiet

default:
    @just --list

init:
    git submodule update --init --recursive
    uv sync --dev

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

clean:
    rm -rf chroma_data/
    rm -rf .pytest_cache
    rm -rf .ruff_cache
    rm -rf **/__pycache__
