import contextlib
import json
import os
import sys
import tempfile
from pathlib import Path

from todo.models import Task

STORAGE_DIR = Path("~/.todo").expanduser()
STORAGE_FILE = STORAGE_DIR / "tasks.json"


def ensure_storage_dir() -> None:
    os.makedirs(STORAGE_DIR, mode=0o700, exist_ok=True)


def load_tasks() -> list[Task]:
    if not STORAGE_FILE.exists():
        return []
    try:
        content = STORAGE_FILE.read_text(encoding="utf-8")
    except OSError:
        print(f"Fehler: konnte {STORAGE_FILE} nicht lesen", file=sys.stderr)
        return []
    if not content.strip():
        return []
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        print(f"Fehler: {STORAGE_FILE} enthält ungültiges JSON", file=sys.stderr)
        return []
    if not isinstance(data, list):
        print(f"Fehler: {STORAGE_FILE} enthält kein JSON-Array", file=sys.stderr)
        return []
    tasks: list[Task] = []
    for item in data:
        if not isinstance(item, dict):
            print(f"Fehler: überspringe nicht-Objekt-Eintrag in {STORAGE_FILE}", file=sys.stderr)
            continue
        try:
            tasks.append(Task.from_dict(item))
        except (KeyError, ValueError, TypeError) as exc:
            print(
                f"Fehler: überspringe ungültigen Aufgabeneintrag in {STORAGE_FILE}: {exc}",
                file=sys.stderr,
            )
            continue
    return tasks


def save_tasks(tasks: list[Task]) -> None:
    ensure_storage_dir()
    data = [t.to_dict() for t in tasks]
    json_text = json.dumps(data, ensure_ascii=False, indent=2)
    fd, tmp_path = tempfile.mkstemp(dir=str(STORAGE_DIR), suffix=".tmp")
    try:
        os.write(fd, json_text.encode("utf-8"))
        os.fsync(fd)
        os.close(fd)
        fd = -1
        os.chmod(tmp_path, 0o600)
        os.replace(tmp_path, STORAGE_FILE)
    except Exception:
        if fd >= 0:
            os.close(fd)
        with contextlib.suppress(OSError):
            os.unlink(tmp_path)
        raise
