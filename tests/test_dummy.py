# tests/test_dummy.py

"""Placeholder test suite that always passes. Replace with real tests."""

import pytest


@pytest.mark.skip("No tests yet")
def test_placeholder() -> None:
    assert True

# TODO(student): Replace this placeholder with meaningful tests.
#   – Use `pytest-asyncio` to test each agent's `run()` coroutine end-to-end.
#   – Mock external calls (network, LLM) with `pytest-mocker` or `respx` to keep tests fast & deterministic.
#   – Aim for ≥80% coverage; run `pytest --cov` as part of CI.