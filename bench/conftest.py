import pytest

@pytest.fixture(scope="session")
def benchmark_config():
    return {
        "min_rounds": 10,
        "warmup": True,
    }
