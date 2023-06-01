type-check:
	mypy **/*.py

auto-format:
	black --check .
