check-linting:
	uv run ruff check typeid/ tests/
	uv run black --check --diff typeid/ tests/ --line-length 119
	uv run mypy typeid/ --pretty


fix-linting:
	uv run ruff check --fix typeid/ tests/
	uv run black typeid/ tests/ --line-length 119


.PHONY: build-sdist
build-sdist:
	@rm -rf dist build *.egg-info .venv
	@uv build --sdist -o dist
	@ls -la dist


test-release:
	uv run twine upload --repository testpypi dist/* --verbose


release:
	uv run twine upload --repository pypi dist/* --verbose


test:
	uv run pytest -v


test-docs:
	uv run pytest README.md docs/ --markdown-docs


docs:
	mkdocs serve


docs-build: 
	mkdocs build

