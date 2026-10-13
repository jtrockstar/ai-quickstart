"""Shared pytest setup for example-report: put scripts/ on the import path, skip sleeps."""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import example_report_rest  # noqa: E402


@pytest.fixture(autouse=True)
def _no_sleep(monkeypatch):
    monkeypatch.setattr(example_report_rest.time, "sleep", lambda *_: None)
