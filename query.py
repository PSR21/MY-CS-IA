# --- query.py ---
from __future__ import annotations

from datetime import date
from typing import List, Optional

from models import StudySession, parse_date


def search_sessions(
    sessions: List[StudySession],
    subject_query: str = "",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    status: Optional[str] = None,
) -> List[StudySession]:
    subject_query = subject_query.lower().strip()
    start = parse_date(start_date) if start_date else None
    end = parse_date(end_date) if end_date else None
    results = []
    for session in sessions:
        if subject_query and subject_query not in session.subject_name.lower():
            continue
        session_date = parse_date(session.date)
        if start and session_date < start:
            continue
        if end and session_date > end:
            continue
        if status and session.status != status:
            continue
        results.append(session)
    return results
