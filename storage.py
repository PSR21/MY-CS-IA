# --- storage.py ---
from __future__ import annotations

import json
import os
from typing import Any

from models import UserData


def _data_file(username: str) -> str:
    return os.path.join("data", f"{username}.json")


def _ensure_data_dir() -> None:
    os.makedirs("data", exist_ok=True)


def load_user_data(username: str) -> UserData:
    _ensure_data_dir()
    path = _data_file(username)
    if not os.path.exists(path):
        return UserData()
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return UserData.from_dict(payload)


def save_user_data(username: str, data: UserData) -> None:
    _ensure_data_dir()
    path = _data_file(username)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as handle:
        json.dump(data.to_dict(), handle, indent=2)
    os.replace(tmp, path)
