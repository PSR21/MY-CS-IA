# --- models.py ---
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, date, time
from typing import Optional, List, Dict
import uuid

DATE_FMT = "%Y-%m-%d"
TIME_FMT = "%H:%M"


def _uuid() -> str:
    return str(uuid.uuid4())


def parse_date(value: str) -> date:
    return datetime.strptime(value, DATE_FMT).date()


def parse_time(value: str) -> time:
    return datetime.strptime(value, TIME_FMT).time()


def validate_date(value: str) -> None:
    parse_date(value)


def validate_time(value: str) -> None:
    parse_time(value)


def validate_difficulty(value: int) -> None:
    if not (1 <= value <= 5):
        raise ValueError("Difficulty must be between 1 and 5")


def validate_day_of_week(value: str) -> None:
    if value not in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]:
        raise ValueError("day_of_week must be Mon-Sun")


def validate_time_range(start: str, end: str) -> None:
    start_t = parse_time(start)
    end_t = parse_time(end)
    if start_t >= end_t:
        raise ValueError("start_time must be before end_time")


def validate_availability_no_overlap(slots: List["AvailabilitySlot"]) -> None:
    by_day: Dict[str, List[AvailabilitySlot]] = {}
    for slot in slots:
        by_day.setdefault(slot.day_of_week, []).append(slot)
    for day, items in by_day.items():
        sorted_items = sorted(items, key=lambda s: s.start_time)
        for i in range(1, len(sorted_items)):
            prev = sorted_items[i - 1]
            current = sorted_items[i]
            if parse_time(current.start_time) < parse_time(prev.end_time):
                raise ValueError(f"Availability overlap on {day}")


@dataclass
class Subject:
    id: str = field(default_factory=_uuid)
    name: str = ""
    exam_date: str = ""
    difficulty: int = 1
    notes: Optional[str] = None

    def validate(self) -> None:
        if not self.name.strip():
            raise ValueError("Subject name is required")
        validate_date(self.exam_date)
        validate_difficulty(self.difficulty)


@dataclass
class AvailabilitySlot:
    id: str = field(default_factory=_uuid)
    day_of_week: str = "Mon"
    start_time: str = ""
    end_time: str = ""

    def validate(self) -> None:
        validate_day_of_week(self.day_of_week)
        validate_time_range(self.start_time, self.end_time)


@dataclass
class StudySession:
    id: str = field(default_factory=_uuid)
    date: str = ""
    start_time: str = ""
    end_time: str = ""
    subject_id: str = ""
    subject_name: str = ""
    status: str = "PLANNED"
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    note: Optional[str] = None

    def validate(self) -> None:
        validate_date(self.date)
        validate_time_range(self.start_time, self.end_time)
        if self.status not in ["PLANNED", "COMPLETED", "MISSED"]:
            raise ValueError("Invalid session status")


@dataclass
class UserProfile:
    username: str
    created_at: str


@dataclass
class UserData:
    subjects: List[Subject] = field(default_factory=list)
    availability: List[AvailabilitySlot] = field(default_factory=list)
    sessions: List[StudySession] = field(default_factory=list)
    backlog: List[StudySession] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "subjects": [asdict(s) for s in self.subjects],
            "availability": [asdict(a) for a in self.availability],
            "sessions": [asdict(s) for s in self.sessions],
            "backlog": [asdict(b) for b in self.backlog],
        }

    @classmethod
    def from_dict(cls, payload: dict) -> "UserData":
        return cls(
            subjects=[Subject(**item) for item in payload.get("subjects", [])],
            availability=[AvailabilitySlot(**item) for item in payload.get("availability", [])],
            sessions=[StudySession(**item) for item in payload.get("sessions", [])],
            backlog=[StudySession(**item) for item in payload.get("backlog", [])],
        )
