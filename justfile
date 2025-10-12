set shell := ["bash", "-cu"]

init:
	uv run pre-commit install
	uv sync

test:
	uv run --env-file=tests.env pytest

test-update:
	uv run --env-file=tests.env pytest --snapshot-update

run:
	uv run tofuref

check:
	uv run pre-commit run --all-files
