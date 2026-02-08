# --- ui/sessions_page.py ---
from __future__ import annotations

from PySide6 import QtCore, QtWidgets

from services import StudyService


class SessionsPage(QtWidgets.QWidget):
    sessions_updated = QtCore.Signal()

    def __init__(self) -> None:
        super().__init__()
        self.service: StudyService | None = None
        layout = QtWidgets.QVBoxLayout(self)

        filters = QtWidgets.QHBoxLayout()
        self.search = QtWidgets.QLineEdit()
        self.search.setPlaceholderText("Subject search")
        self.status = QtWidgets.QComboBox()
        self.status.addItems(["", "PLANNED", "COMPLETED", "MISSED"])
        self.start_date = QtWidgets.QLineEdit()
        self.start_date.setPlaceholderText("Start YYYY-MM-DD")
        self.end_date = QtWidgets.QLineEdit()
        self.end_date.setPlaceholderText("End YYYY-MM-DD")
        self.filter_btn = QtWidgets.QPushButton("Filter")
        filters.addWidget(self.search)
        filters.addWidget(self.status)
        filters.addWidget(self.start_date)
        filters.addWidget(self.end_date)
        filters.addWidget(self.filter_btn)
        layout.addLayout(filters)

        self.table = QtWidgets.QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Date", "Start", "End", "Subject", "Status", "Note"])
        self.table.setSortingEnabled(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        buttons = QtWidgets.QHBoxLayout()
        self.complete_btn = QtWidgets.QPushButton("Mark Completed")
        self.missed_btn = QtWidgets.QPushButton("Mark Missed")
        buttons.addWidget(self.complete_btn)
        buttons.addWidget(self.missed_btn)
        layout.addLayout(buttons)

        self.message = QtWidgets.QLabel("")
        layout.addWidget(self.message)

        self.filter_btn.clicked.connect(self.refresh)
        self.complete_btn.clicked.connect(self._mark_completed)
        self.missed_btn.clicked.connect(self._mark_missed)

    def set_service(self, service: StudyService) -> None:
        self.service = service

    def refresh(self) -> None:
        if not self.service:
            return
        subject_query = self.search.text().strip()
        status = self.status.currentText() or None
        start = self._normalize_date(self.start_date.text())
        end = self._normalize_date(self.end_date.text())
        sessions = self.service.search_sessions(subject_query=subject_query, status=status, start_date=start, end_date=end)
        self.table.setRowCount(len(sessions))
        for row, session in enumerate(sessions):
            self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(session.date))
            self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(session.start_time))
            self.table.setItem(row, 2, QtWidgets.QTableWidgetItem(session.end_time))
            self.table.setItem(row, 3, QtWidgets.QTableWidgetItem(session.subject_name))
            self.table.setItem(row, 4, QtWidgets.QTableWidgetItem(session.status))
            self.table.setItem(row, 5, QtWidgets.QTableWidgetItem(session.note or ""))
            self.table.setVerticalHeaderItem(row, QtWidgets.QTableWidgetItem(session.id))

    def _normalize_date(self, text: str) -> str | None:
        value = text.strip()
        if not value:
            return None
        return value

    def _current_session_id(self) -> str | None:
        row = self.table.currentRow()
        if row < 0:
            return None
        return self.table.verticalHeaderItem(row).text()

    def _mark_completed(self) -> None:
        if not self.service:
            return
        session_id = self._current_session_id()
        if not session_id:
            self.message.setText("Select a session.")
            return
        self.service.mark_session_completed(session_id)
        self.message.setText("Session marked completed.")
        self.sessions_updated.emit()

    def _mark_missed(self) -> None:
        if not self.service:
            return
        session_id = self._current_session_id()
        if not session_id:
            self.message.setText("Select a session.")
            return
        warning = self.service.mark_session_missed(session_id)
        self.message.setText(warning or "Session marked missed and rescheduled.")
        self.sessions_updated.emit()
