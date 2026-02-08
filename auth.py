# --- auth.py ---
from __future__ import annotations

import json
import os
import hashlib
import secrets
from datetime import datetime
from typing import Dict

from models import UserProfile

USERS_FILE = os.path.join("data", "users.json")


def _ensure_data_dir() -> None:
    os.makedirs("data", exist_ok=True)


def _load_users() -> Dict[str, dict]:
    _ensure_data_dir()
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _save_users(users: Dict[str, dict]) -> None:
    _ensure_data_dir()
    tmp = USERS_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as handle:
        json.dump(users, handle, indent=2)
    os.replace(tmp, USERS_FILE)


def _hash_password(password: str, salt: bytes) -> str:
    hashed = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    return hashed.hex()


def register(username: str, password: str) -> None:
    if not username.strip() or not password:
        raise ValueError("Username and password are required")
    users = _load_users()
    if username in users:
        raise ValueError("User already exists")
    salt = secrets.token_bytes(16)
    users[username] = {
        "salt": salt.hex(),
        "password_hash": _hash_password(password, salt),
        "created_at": datetime.utcnow().isoformat(),
    }
    _save_users(users)


def login(username: str, password: str) -> UserProfile:
    users = _load_users()
    record = users.get(username)
    if not record:
        raise ValueError("Invalid username or password")
    salt = bytes.fromhex(record["salt"])
    expected = record["password_hash"]
    if _hash_password(password, salt) != expected:
        raise ValueError("Invalid username or password")
    return UserProfile(username=username, created_at=record["created_at"])
