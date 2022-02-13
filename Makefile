.PHONY: format
format:
	autoflake --recursive --in-place --remove-all-unused-imports .
	isort .
	black .
	flake8

.PHONY: lint
lint:
	isort --check .
	black --check .
	flake8
