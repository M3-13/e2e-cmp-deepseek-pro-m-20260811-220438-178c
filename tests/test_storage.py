import json
from datetime import datetime, timezone

from todo.models import Task
from todo.storage import ensure_storage_dir, load_tasks, save_tasks


def _make_task(**overrides):
    import uuid

    defaults = {
        "id": str(uuid.uuid4()),
        "description": "Storage test task",
        "status": "pending",
        "priority": "medium",
        "due_date": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    defaults.update(overrides)
    return Task(**defaults)


class TestEnsureStorageDir:
    def test_creates_directory(self, temp_storage_dir):
        storage_dir = temp_storage_dir / "subdir"
        file_path = storage_dir / "tasks.json"
        import todo.storage as storage_mod

        orig_dir = storage_mod.STORAGE_DIR
        orig_file = storage_mod.STORAGE_FILE
        try:
            storage_mod.STORAGE_DIR = storage_dir
            storage_mod.STORAGE_FILE = file_path
            ensure_storage_dir()
            assert storage_dir.exists()
            assert storage_dir.is_dir()
        finally:
            storage_mod.STORAGE_DIR = orig_dir
            storage_mod.STORAGE_FILE = orig_file

    def test_existing_directory_no_error(self, temp_storage_dir):
        import todo.storage as storage_mod

        orig_dir = storage_mod.STORAGE_DIR
        try:
            storage_mod.STORAGE_DIR = temp_storage_dir
            ensure_storage_dir()
            ensure_storage_dir()
        finally:
            storage_mod.STORAGE_DIR = orig_dir
            assert True


class TestLoadTasks:
    def test_empty_on_missing_file(self, temp_storage_dir):
        import todo.storage as storage_mod

        orig_file = storage_mod.STORAGE_FILE
        try:
            storage_mod.STORAGE_FILE = temp_storage_dir / "nonexistent.json"
            tasks = load_tasks()
            assert tasks == []
        finally:
            storage_mod.STORAGE_FILE = orig_file

    def test_empty_on_empty_file(self, temp_storage_dir):
        tasks_file = temp_storage_dir / "tasks.json"
        tasks_file.write_text("", encoding="utf-8")
        import todo.storage as storage_mod

        orig_file = storage_mod.STORAGE_FILE
        try:
            storage_mod.STORAGE_FILE = tasks_file
            tasks = load_tasks()
            assert tasks == []
        finally:
            storage_mod.STORAGE_FILE = orig_file

    def test_empty_on_malformed_json(self, temp_storage_dir, capsys):
        tasks_file = temp_storage_dir / "tasks.json"
        tasks_file.write_text("{not valid json", encoding="utf-8")
        import todo.storage as storage_mod

        orig_file = storage_mod.STORAGE_FILE
        try:
            storage_mod.STORAGE_FILE = tasks_file
            tasks = load_tasks()
            assert tasks == []
            stderr = capsys.readouterr().err
            assert "invalid JSON" in stderr
        finally:
            storage_mod.STORAGE_FILE = orig_file

    def test_loads_valid_tasks(self, temp_storage_dir, capsys):
        task = _make_task()
        tasks_file = temp_storage_dir / "tasks.json"
        tasks_file.write_text(json.dumps([task.to_dict()], ensure_ascii=False), encoding="utf-8")
        import todo.storage as storage_mod

        orig_file = storage_mod.STORAGE_FILE
        try:
            storage_mod.STORAGE_FILE = tasks_file
            loaded = load_tasks()
            assert len(loaded) == 1
            assert loaded[0].id == task.id
            assert loaded[0].description == task.description
            stderr = capsys.readouterr().err
            assert stderr == ""
        finally:
            storage_mod.STORAGE_FILE = orig_file

    def test_skips_invalid_entries(self, temp_storage_dir, capsys):
        task = _make_task()
        bad_entry = {"id": "no-description", "status": "pending", "priority": "low"}
        tasks_file = temp_storage_dir / "tasks.json"
        data = [task.to_dict(), bad_entry]
        tasks_file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        import todo.storage as storage_mod

        orig_file = storage_mod.STORAGE_FILE
        try:
            storage_mod.STORAGE_FILE = tasks_file
            loaded = load_tasks()
            assert len(loaded) == 1
            assert loaded[0].id == task.id
            stderr = capsys.readouterr().err
            assert "skipping" in stderr.lower() or "Error" in stderr
        finally:
            storage_mod.STORAGE_FILE = orig_file

    def test_empty_on_non_list_json(self, temp_storage_dir, capsys):
        tasks_file = temp_storage_dir / "tasks.json"
        tasks_file.write_text('{"not": "a list"}', encoding="utf-8")
        import todo.storage as storage_mod

        orig_file = storage_mod.STORAGE_FILE
        try:
            storage_mod.STORAGE_FILE = tasks_file
            tasks = load_tasks()
            assert tasks == []
            stderr = capsys.readouterr().err
            assert "array" in stderr.lower()
        finally:
            storage_mod.STORAGE_FILE = orig_file


class TestSaveTasks:
    def test_saves_and_loads_tasks(self, temp_storage_dir):
        import todo.storage as storage_mod

        tasks_file = temp_storage_dir / "tasks.json"
        orig_dir = storage_mod.STORAGE_DIR
        orig_file = storage_mod.STORAGE_FILE
        try:
            storage_mod.STORAGE_DIR = temp_storage_dir
            storage_mod.STORAGE_FILE = tasks_file
            task = _make_task()
            save_tasks([task])
            assert tasks_file.exists()
            loaded = load_tasks()
            assert len(loaded) == 1
            assert loaded[0].id == task.id
        finally:
            storage_mod.STORAGE_DIR = orig_dir
            storage_mod.STORAGE_FILE = orig_file

    def test_overwrites_existing_file(self, temp_storage_dir):
        import todo.storage as storage_mod

        tasks_file = temp_storage_dir / "tasks.json"
        orig_dir = storage_mod.STORAGE_DIR
        orig_file = storage_mod.STORAGE_FILE
        try:
            storage_mod.STORAGE_DIR = temp_storage_dir
            storage_mod.STORAGE_FILE = tasks_file

            task1 = _make_task(description="First")
            save_tasks([task1])
            task2 = _make_task(description="Second")
            save_tasks([task1, task2])

            loaded = load_tasks()
            assert len(loaded) == 2
        finally:
            storage_mod.STORAGE_DIR = orig_dir
            storage_mod.STORAGE_FILE = orig_file

    def test_file_permissions(self, temp_storage_dir):
        import todo.storage as storage_mod

        tasks_file = temp_storage_dir / "tasks.json"
        orig_dir = storage_mod.STORAGE_DIR
        orig_file = storage_mod.STORAGE_FILE
        try:
            storage_mod.STORAGE_DIR = temp_storage_dir
            storage_mod.STORAGE_FILE = tasks_file

            task = _make_task()
            save_tasks([task])
            assert tasks_file.exists()
        finally:
            storage_mod.STORAGE_DIR = orig_dir
            storage_mod.STORAGE_FILE = orig_file
