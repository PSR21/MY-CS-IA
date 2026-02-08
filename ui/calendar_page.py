# --- ui/calendar_page.py ---
from __future__ import annotations

from datetime import date, timedelta

from PySide6 import QtWidgets

from services import StudyService
from models import parse_date


class CalendarPage(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.service: StudyService | None = None
        layout = QtWidgets.QVBoxLayout(self)
        self.week_label = QtWidgets.QLabel("")
        layout.addWidget(self.week_label)
        self.table = QtWidgets.QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

    def set_service(self, service: StudyService) -> None:
        self.service = service

    def refresh(self) -> None:
        if not self.service:
            return
        today = date.today()
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)
        self.week_label.setText(f"Week: {start} - {end}")
        self.table.setRowCount(6)
        for row in range(6):
            for col in range(7):
                self.table.setItem(row, col, QtWidgets.QTableWidgetItem(""))
        sessions = [s for s in self.service.data.sessions if start <= parse_date(s.date) <= end]
        by_day = {}
        for session in sessions:
            by_day.setdefault(session.date, []).append(session)
        for col in range(7):
            day = start + timedelta(days=col)
            items = by_day.get(day.strftime("%Y-%m-%d"), [])
            for row, session in enumerate(items[:6]):
                self.table.setItem(
                    row,
                    col,
                    QtWidgets.QTableWidgetItem(f"{session.start_time}-{session.end_time}\n{session.subject_name}"),
                )
