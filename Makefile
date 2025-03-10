check-linting:
	poetry run isort --check --profile black typeid/ tests/
	poetry run flake8 --exit-zero typeid/ tests/ --exit-zero
	poetry run black --check --diff typeid/ tests/ --line-length 119
	poetry run mypy typeid/ --pretty


fix-linting:
	poetry run isort --profile black typeid/ tests/
	poetry run black typeid/ tests/ --line-length 119


artifacts: test
	python -m build


clean:
	rm -rf dist build *.egg-info


prepforbuild:
	pip install build


build:
	poetry build


test-release:
	twine upload --repository testpypi dist/* --verbose


release:
	twine upload --repository pypi dist/* --verbose


test:
	poetry run pytest -v
