import copy
import json
import os
import tempfile
import threading
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.config import settings


def utcnow() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


class JsonStorage:
    """Mock DB JSON thread-safe. `path=None` => stockage purement en mémoire."""

    def __init__(self, path: Path | str | None = None) -> None:
        self._path = Path(path) if path else None
        self._lock = threading.RLock()
        self._data: dict[str, list[dict[str, Any]]] = {"users": [], "pins": []}
        if self._path and self._path.exists():
            self._data = json.loads(self._path.read_text(encoding="utf-8"))

    def reset(self, data: dict[str, list[dict[str, Any]]] | None = None) -> None:
        with self._lock:
            self._data = copy.deepcopy(data) if data else {"users": [], "pins": []}
            self._flush()

    def _flush(self) -> None:
        if not self._path:
            return
        self._path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=self._path.parent, suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)
        os.replace(tmp, self._path)  # écriture atomique

    def _next_id(self, table: str) -> int:
        return max((row["id"] for row in self._data[table]), default=0) + 1

    # --- users ---
    def get_user_by_id(self, user_id: int) -> dict[str, Any] | None:
        with self._lock:
            return next((copy.deepcopy(u) for u in self._data["users"] if u["id"] == user_id), None)

    def get_user_by_email(self, email: str) -> dict[str, Any] | None:
        with self._lock:
            return next(
                (
                    copy.deepcopy(u)
                    for u in self._data["users"]
                    if u["email"].lower() == email.lower()
                ),
                None,
            )

    def get_users(self) -> list[dict[str, Any]]:
        with self._lock:
            return copy.deepcopy(self._data["users"])

    def save_user(self, user: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            row = {"id": self._next_id("users"), **user, "created_at": utcnow()}
            self._data["users"].append(row)
            self._flush()
            return copy.deepcopy(row)

    def update_user(self, user_id: int, fields: dict[str, Any]) -> dict[str, Any] | None:
        with self._lock:
            for user in self._data["users"]:
                if user["id"] == user_id:
                    user.update(fields)
                    self._flush()
                    return copy.deepcopy(user)
            return None

    def delete_user(self, user_id: int) -> bool:
        """Supprime l'utilisateur et ses pins."""
        with self._lock:
            before = len(self._data["users"])
            self._data["users"] = [u for u in self._data["users"] if u["id"] != user_id]
            if len(self._data["users"]) == before:
                return False
            self._data["pins"] = [p for p in self._data["pins"] if p["user_id"] != user_id]
            self._flush()
            return True

    # --- pins ---
    def get_pins(self) -> list[dict[str, Any]]:
        with self._lock:
            return copy.deepcopy(self._data["pins"])

    def get_pin_by_id(self, pin_id: int) -> dict[str, Any] | None:
        with self._lock:
            return next((copy.deepcopy(p) for p in self._data["pins"] if p["id"] == pin_id), None)

    def save_pin(self, pin: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            row = {"id": self._next_id("pins"), **pin, "created_at": utcnow()}
            self._data["pins"].append(row)
            self._flush()
            return copy.deepcopy(row)

    def update_pin(self, pin_id: int, fields: dict[str, Any]) -> dict[str, Any] | None:
        with self._lock:
            for pin in self._data["pins"]:
                if pin["id"] == pin_id:
                    pin.update(fields)
                    self._flush()
                    return copy.deepcopy(pin)
            return None

    def delete_pin(self, pin_id: int) -> bool:
        with self._lock:
            before = len(self._data["pins"])
            self._data["pins"] = [p for p in self._data["pins"] if p["id"] != pin_id]
            deleted = len(self._data["pins"]) < before
            if deleted:
                self._flush()
            return deleted


_storage: JsonStorage | None = None


def get_storage() -> JsonStorage:
    """Dépendance FastAPI ; surchargée dans les tests via `dependency_overrides`."""
    global _storage
    if _storage is None:
        _storage = JsonStorage(settings.db_path)
    return _storage
