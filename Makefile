check-linting:
	isort --check --profile black src/ tests/ examples/
	flake8 --exit-zero src/ tests/ examples/ --exit-zero
	black --check --diff src/ tests/ examples/ --line-length 119
	mypy src/ --pretty


fix-linting:
	isort --profile black src/ tests/ examples/
	black src/ tests/ examples/ --line-length 119


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
