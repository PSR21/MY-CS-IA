# --- services.py ---
from __future__ import annotations

from datetime import datetime, date
from typing import List, Optional, Tuple

from models import (
    Subject,
    AvailabilitySlot,
    StudySession,
    UserData,
    validate_availability_no_overlap,
)
from storage import load_user_data, save_user_data
from scheduler import generate_schedule
from rescheduler import redistribute_missed
from query import search_sessions
from stats import subject_progress


class StudyService:
    def __init__(self, username: str):
        self.username = username
        self.data = load_user_data(username)

    def _save(self) -> None:
        save_user_data(self.username, self.data)

    def _validate_availability(self) -> None:
        for slot in self.data.availability:
            slot.validate()
        validate_availability_no_overlap(self.data.availability)

    # Subjects
    def add_subject(self, subject: Subject) -> None:
        subject.validate()
        self.data.subjects.append(subject)
        self._save()

    def update_subject(self, subject: Subject) -> None:
        subject.validate()
        for idx, existing in enumerate(self.data.subjects):
            if existing.id == subject.id:
                self.data.subjects[idx] = subject
                break
        else:
            raise ValueError("Subject not found")
        self._save()

    def delete_subject(self, subject_id: str) -> None:
        self.data.subjects = [s for s in self.data.subjects if s.id != subject_id]
        self.data.sessions = [s for s in self.data.sessions if s.subject_id != subject_id]
        self._save()

    # Availability
    def add_availability(self, slot: AvailabilitySlot) -> None:
        slot.validate()
        self.data.availability.append(slot)
        self._validate_availability()
        self._save()

    def update_availability(self, slot: AvailabilitySlot) -> None:
        slot.validate()
        for idx, existing in enumerate(self.data.availability):
            if existing.id == slot.id:
                self.data.availability[idx] = slot
                break
        else:
            raise ValueError("Availability slot not found")
        self._validate_availability()
        self._save()

    def delete_availability(self, slot_id: str) -> None:
        self.data.availability = [s for s in self.data.availability if s.id != slot_id]
        self._save()

    # Scheduling
    def generate_schedule(self, session_length: int, end_date: Optional[str] = None) -> Tuple[int, Optional[str]]:
        new_sessions = generate_schedule(self.data.subjects, self.data.availability, session_length, end_date)
        self.data.sessions = new_sessions
        self._save()
        return len(new_sessions), None

    def regenerate_schedule(self, session_length: int, end_date: Optional[str] = None, preserve_status: bool = True) -> Tuple[int, Optional[str]]:
        existing = {self._session_identity(s): s for s in self.data.sessions}
        new_sessions = generate_schedule(self.data.subjects, self.data.availability, session_length, end_date)
        warning = None
        if preserve_status:
            for session in new_sessions:
                key = self._session_identity(session)
                if key in existing:
                    session.status = existing[key].status
                    session.updated_at = datetime.utcnow().isoformat()
        completed_missing = [s for s in self.data.sessions if s.status in {"COMPLETED", "MISSED"} and self._session_identity(s) not in {self._session_identity(n) for n in new_sessions}]
        if completed_missing:
            warning = "Some completed/missed sessions no longer exist in the regenerated schedule."
        self.data.sessions = new_sessions
        self._save()
        return len(new_sessions), warning

    def mark_session_completed(self, session_id: str) -> None:
        session = self._find_session(session_id)
        session.status = "COMPLETED"
        session.updated_at = datetime.utcnow().isoformat()
        self._save()

    def mark_session_missed(self, session_id: str) -> Optional[str]:
        session = self._find_session(session_id)
        session.status = "MISSED"
        session.updated_at = datetime.utcnow().isoformat()
        schedule_end = self._schedule_end_date()
        rescheduled = redistribute_missed(session, self.data.availability, self.data.sessions, schedule_end)
        if rescheduled:
            self.data.sessions.append(rescheduled)
        else:
            self.data.backlog.append(session)
        self._save()
        return None if rescheduled else "No available slot found. Added to backlog."

    def search_sessions(self, **kwargs) -> List[StudySession]:
        return search_sessions(self.data.sessions, **kwargs)

    def get_stats(self) -> List[dict]:
        return subject_progress(self.data.sessions)

    def seed_demo_data(self) -> None:
        if self.data.subjects or self.data.availability:
            return
        self.add_subject(Subject(name="Math", exam_date=(date.today()).strftime("%Y-%m-%d"), difficulty=4))
        self.add_subject(Subject(name="History", exam_date=(date.today()).strftime("%Y-%m-%d"), difficulty=3))
        self.add_availability(AvailabilitySlot(day_of_week="Mon", start_time="16:00", end_time="18:00"))
        self.add_availability(AvailabilitySlot(day_of_week="Wed", start_time="17:00", end_time="19:00"))

    def _find_session(self, session_id: str) -> StudySession:
        for session in self.data.sessions:
            if session.id == session_id:
                return session
        raise ValueError("Session not found")

    def _schedule_end_date(self) -> date:
        if self.data.sessions:
            return max(date.fromisoformat(s.date) for s in self.data.sessions)
        if self.data.subjects:
            return max(date.fromisoformat(s.exam_date) for s in self.data.subjects)
        return date.today()

    @staticmethod
    def _session_identity(session: StudySession) -> tuple:
        return (session.date, session.start_time, session.end_time, session.subject_id)
