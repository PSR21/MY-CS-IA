# --- scheduler.py ---
from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import List, Optional, Dict

from models import Subject, AvailabilitySlot, StudySession, parse_date, parse_time

DAY_ORDER = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def _day_name(d: date) -> str:
    return DAY_ORDER[d.weekday()]


def _session_slots_for_day(day: date, availability: List[AvailabilitySlot], session_length: int) -> List[tuple[str, str]]:
    slots: List[tuple[str, str]] = []
    day_name = _day_name(day)
    for slot in availability:
        if slot.day_of_week != day_name:
            continue
        start = parse_time(slot.start_time)
        end = parse_time(slot.end_time)
        current = datetime.combine(day, start)
        end_dt = datetime.combine(day, end)
        while current + timedelta(minutes=session_length) <= end_dt:
            next_dt = current + timedelta(minutes=session_length)
            slots.append((current.strftime("%H:%M"), next_dt.strftime("%H:%M")))
            current = next_dt
    return slots


def _score(subject: Subject, target_date: date) -> float:
    days_until = (parse_date(subject.exam_date) - target_date).days
    urgency = 1 / (days_until + 1)
    difficulty_weight = subject.difficulty / 5
    return 0.6 * urgency + 0.4 * difficulty_weight


def generate_schedule(
    subjects: List[Subject],
    availability: List[AvailabilitySlot],
    session_length: int,
    end_date: Optional[str] = None,
) -> List[StudySession]:
    if not subjects or not availability:
        return []

    today = date.today()
    last_exam = max(parse_date(s.exam_date) for s in subjects)
    schedule_end = parse_date(end_date) if end_date else last_exam
    if schedule_end < today:
        return []

    sessions: List[StudySession] = []
    current_day = today
    while current_day <= schedule_end:
        day_slots = _session_slots_for_day(current_day, availability, session_length)
        if not day_slots:
            current_day += timedelta(days=1)
            continue
        total_slots = len(day_slots)
        per_subject_limit = max(1, total_slots // 2)
        subject_counts: Dict[str, int] = {s.id: 0 for s in subjects}
        last_subject_id = None
        streak = 0
        for start, end in day_slots:
            candidates = [s for s in subjects if parse_date(s.exam_date) >= current_day]
            if not candidates:
                break
            ranked = sorted(candidates, key=lambda s: _score(s, current_day), reverse=True)
            chosen = None
            for subject in ranked:
                count = subject_counts[subject.id]
                over_limit = count >= per_subject_limit
                if over_limit and len(candidates) > 1:
                    continue
                if last_subject_id == subject.id and streak >= 2:
                    alternative_exists = any(s.id != subject.id for s in candidates)
                    if alternative_exists:
                        continue
                chosen = subject
                break
            if not chosen:
                chosen = ranked[0]
            subject_counts[chosen.id] += 1
            if last_subject_id == chosen.id:
                streak += 1
            else:
                streak = 1
                last_subject_id = chosen.id
            sessions.append(
                StudySession(
                    date=current_day.strftime("%Y-%m-%d"),
                    start_time=start,
                    end_time=end,
                    subject_id=chosen.id,
                    subject_name=chosen.name,
                    status="PLANNED",
                )
            )
        current_day += timedelta(days=1)
    return sessions
