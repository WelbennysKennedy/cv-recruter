import importlib
import json
import sys
from pathlib import Path


def _load_external_tinydb():
    current_dir = Path(__file__).resolve().parent
    current_module = sys.modules.get(__name__)
    original_path = list(sys.path)

    try:
        sys.path = [
            entry for entry in sys.path
            if entry and Path(entry).resolve() != current_dir
        ]
        sys.modules.pop(__name__, None)
        return importlib.import_module(__name__)
    except Exception:
        return None
    finally:
        sys.path = original_path
        if current_module:
            sys.modules[__name__] = current_module


_external_tinydb = _load_external_tinydb()

if _external_tinydb:
    TinyDB = _external_tinydb.TinyDB
    Query = _external_tinydb.Query
else:
    class _Condition:
        def __init__(self, field, expected):
            self.field = field
            self.expected = expected

        def __call__(self, item):
            return item.get(self.field) == self.expected

    class _QueryField:
        def __init__(self, name):
            self.name = name

        def __eq__(self, other):
            return _Condition(self.name, other)

    class Query:
        def __getattr__(self, name):
            return _QueryField(name)

    class _Table:
        def __init__(self, db, name):
            self.db = db
            self.name = name

        def _rows(self):
            self.db._data.setdefault(self.name, [])
            return self.db._data[self.name]

        def all(self):
            return list(self._rows())

        def insert(self, item):
            self._rows().append(dict(item))
            self.db._save()
            return len(self._rows())

        def search(self, condition):
            return [row for row in self._rows() if condition(row)]

        def update(self, fields, condition):
            count = 0
            for row in self._rows():
                if condition(row):
                    row.update(fields)
                    count += 1
            if count:
                self.db._save()
            return count

        def remove(self, condition):
            rows = self._rows()
            kept = [row for row in rows if not condition(row)]
            removed = len(rows) - len(kept)
            self.db._data[self.name] = kept
            if removed:
                self.db._save()
            return removed

    class TinyDB:
        def __init__(self, file_path="db.json"):
            self.file_path = Path(file_path)
            self._data = self._load()

        def _load(self):
            if not self.file_path.exists():
                return {}

            try:
                with self.file_path.open("r", encoding="utf-8") as file:
                    data = json.load(file)
                    return data if isinstance(data, dict) else {}
            except Exception:
                return {}

        def _save(self):
            self.file_path.write_text(
                json.dumps(self._data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

        def table(self, name):
            return _Table(self, name)
