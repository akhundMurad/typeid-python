check-linting:
	uv run ruff check typeid/ tests/
	uv run black --check --diff typeid/ tests/ --line-length 119
	uv run mypy typeid/ --pretty


fix-linting:
	uv run ruff check --fix typeid/ tests/
	uv run black typeid/ tests/ --line-length 119


# Build sdist + wheel using the configured PEP517 backend
artifacts: test
	uv build


clean:
	rm -rf dist build *.egg-info .venv


# Ensure local dev env is ready (installs deps according to uv.lock / pyproject)
prepforbuild:
	uv sync --all-groups


# Alias if you still want a 'build' target name
build:
	uv build


test-release:
	uv run twine upload --repository testpypi dist/* --verbose


release:
	uv run twine upload --repository pypi dist/* --verbose


test:
	uv run pytest -v
