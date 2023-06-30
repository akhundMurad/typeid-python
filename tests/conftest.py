import pytest
import requests
import yaml


@pytest.fixture(scope="session")
def invalid_spec() -> list:
    url = "https://raw.githubusercontent.com/jetpack-io/typeid/main/spec/invalid.yml"
    response = requests.get(url, timeout=5)
    invalid_yaml = response.content
    return yaml.safe_load(invalid_yaml)


@pytest.fixture(scope="session")
def valid_spec() -> list:
    url = "https://raw.githubusercontent.com/jetpack-io/typeid/main/spec/valid.yml"
    response = requests.get(url, timeout=5)
    invalid_yaml = response.content
    return yaml.safe_load(invalid_yaml)
