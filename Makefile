type-check:
	poetry run mypy **/*.py

auto-format:
	poetry run black --check .
