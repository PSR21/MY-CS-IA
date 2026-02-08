# --- stats.py ---
from __future__ import annotations

from typing import Dict, List

from models import StudySession


def subject_progress(sessions: List[StudySession]) -> List[dict]:
    summary: Dict[str, dict] = {}
    for session in sessions:
        entry = summary.setdefault(
            session.subject_name,
            {"subject": session.subject_name, "total": 0, "completed": 0, "missed": 0},
        )
        entry["total"] += 1
        if session.status == "COMPLETED":
            entry["completed"] += 1
        elif session.status == "MISSED":
            entry["missed"] += 1
    for entry in summary.values():
        total = entry["total"]
        entry["completion_pct"] = round((entry["completed"] / total) * 100, 1) if total else 0.0
    return list(summary.values())
