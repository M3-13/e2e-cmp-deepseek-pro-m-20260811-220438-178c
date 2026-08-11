import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_storage_dir(monkeypatch):
    with tempfile.TemporaryDirectory() as tmpdir:
        dir_path = Path(tmpdir)
        file_path = dir_path / "tasks.json"
        monkeypatch.setattr("todo.storage.STORAGE_DIR", dir_path)
        monkeypatch.setattr("todo.storage.STORAGE_FILE", file_path)
        yield dir_path


@pytest.fixture
def mock_ensure_storage_dir(monkeypatch):
    monkeypatch.setattr("todo.storage.ensure_storage_dir", lambda: None)
