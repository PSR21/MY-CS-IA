# --- rescheduler.py ---
from __future__ import annotations

from datetime import datetime, timedelta, date
from typing import List, Tuple, Optional

from models import StudySession, AvailabilitySlot, parse_date, parse_time
from scheduler import _session_slots_for_day


def _session_key(session: StudySession) -> Tuple[str, str, str]:
    return session.date, session.start_time, session.end_time


def redistribute_missed(
    missed_session: StudySession,
    availability: List[AvailabilitySlot],
    existing_sessions: List[StudySession],
    schedule_end: date,
) -> Optional[StudySession]:
    start_date = parse_date(missed_session.date)
    start_time = parse_time(missed_session.start_time)
    existing_keys = {_session_key(s) for s in existing_sessions}
    current_day = start_date
    while current_day <= schedule_end:
        slots = _session_slots_for_day(current_day, availability, _session_length(missed_session))
        for start, end in slots:
            if current_day == start_date and parse_time(start) <= start_time:
                continue
            candidate_key = (current_day.strftime("%Y-%m-%d"), start, end)
            if candidate_key in existing_keys:
                continue
            return StudySession(
                date=current_day.strftime("%Y-%m-%d"),
                start_time=start,
                end_time=end,
                subject_id=missed_session.subject_id,
                subject_name=missed_session.subject_name,
                status="PLANNED",
                note=f"Rescheduled from {missed_session.date} {missed_session.start_time}",
            )
        current_day += timedelta(days=1)
    return None


def _session_length(session: StudySession) -> int:
    start = datetime.strptime(session.start_time, "%H:%M")
    end = datetime.strptime(session.end_time, "%H:%M")
    return int((end - start).total_seconds() / 60)
