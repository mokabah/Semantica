from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def benchmark_path() -> Path:
    return ROOT / "benchmarks" / "cases.json"
