check-linting:
	isort --check --profile black typeid/ tests/
	flake8 --exit-zero typeid/ tests/ --exit-zero
	black --check --diff typeid/ tests/ --line-length 119
	mypy typeid/ --pretty


fix-linting:
	isort --profile black typeid/ tests/
	black typeid/ tests/ --line-length 119


artifacts: test
	python -m build


clean:
	rm -rf dist/


prepforbuild:
	pip install build


build:
	python -m build


test-release:
	twine upload --repository testpypi dist/* --verbose


release:
	twine upload --repository pypi dist/* --verbose


test:
	pytest -v
