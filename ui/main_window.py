# --- ui/main_window.py ---
from __future__ import annotations

from PySide6 import QtCore, QtWidgets

from auth import login, register
from services import StudyService
from ui.login import LoginPage
from ui.subjects_page import SubjectsPage
from ui.availability_page import AvailabilityPage
from ui.generate_page import GeneratePage
from ui.calendar_page import CalendarPage
from ui.sessions_page import SessionsPage
from ui.stats_page import StatsPage
from ui.settings_page import SettingsPage


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Smart Study Schedule Generator")
        self.resize(1100, 700)

        container = QtWidgets.QWidget()
        self.setCentralWidget(container)
        layout = QtWidgets.QHBoxLayout(container)

        self.sidebar = QtWidgets.QListWidget()
        self.sidebar.setFixedWidth(200)
        self.sidebar.addItems(
            [
                "Login",
                "Subjects",
                "Availability",
                "Generate",
                "Calendar",
                "Sessions",
                "Progress",
                "Settings",
                "Logout",
            ]
        )
        layout.addWidget(self.sidebar)

        self.stack = QtWidgets.QStackedWidget()
        layout.addWidget(self.stack)

        self.login_page = LoginPage()
        self.subjects_page = SubjectsPage()
        self.availability_page = AvailabilityPage()
        self.generate_page = GeneratePage()
        self.calendar_page = CalendarPage()
        self.sessions_page = SessionsPage()
        self.stats_page = StatsPage()
        self.settings_page = SettingsPage()
        self.logout_page = QtWidgets.QWidget()

        self.stack.addWidget(self.login_page)
        self.stack.addWidget(self.subjects_page)
        self.stack.addWidget(self.availability_page)
        self.stack.addWidget(self.generate_page)
        self.stack.addWidget(self.calendar_page)
        self.stack.addWidget(self.sessions_page)
        self.stack.addWidget(self.stats_page)
        self.stack.addWidget(self.settings_page)
        self.stack.addWidget(self.logout_page)

        self.service: StudyService | None = None

        self.sidebar.currentRowChanged.connect(self._switch_page)
        self.login_page.logged_in.connect(self._login)
        self.login_page.registered.connect(self._register)
        self._set_logged_out_state()

    def _switch_page(self, index: int) -> None:
        if index == 8:
            self._logout()
            return
        self.stack.setCurrentIndex(index)

    def _set_logged_out_state(self) -> None:
        self.sidebar.setCurrentRow(0)
        for i in range(1, 9):
            self.sidebar.item(i).setHidden(True)
        self.stack.setCurrentWidget(self.login_page)

    def _set_logged_in_state(self) -> None:
        for i in range(1, 9):
            self.sidebar.item(i).setHidden(False)
        self.sidebar.setCurrentRow(1)

    def _register(self, username: str) -> None:
        try:
            register(username, self.login_page.password.text())
            self.login_page.set_message("Registered. Please log in.")
        except Exception as exc:
            self.login_page.set_message(str(exc))

    def _login(self, username: str) -> None:
        try:
            login(username, self.login_page.password.text())
            self.service = StudyService(username)
            self._wire_pages()
            self._set_logged_in_state()
        except Exception as exc:
            self.login_page.set_message(str(exc))

    def _logout(self) -> None:
        self.service = None
        self._set_logged_out_state()

    def _wire_pages(self) -> None:
        if not self.service:
            return
        self.subjects_page.set_service(self.service)
        self.availability_page.set_service(self.service)
        self.generate_page.set_service(self.service)
        self.calendar_page.set_service(self.service)
        self.sessions_page.set_service(self.service)
        self.stats_page.set_service(self.service)
        self.settings_page.set_service(self.service)
        self.generate_page.schedule_updated.connect(self._refresh_all)
        self.sessions_page.sessions_updated.connect(self._refresh_all)
        self._refresh_all()

    def _refresh_all(self) -> None:
        if not self.service:
            return
        self.subjects_page.refresh()
        self.availability_page.refresh()
        self.generate_page.refresh()
        self.calendar_page.refresh()
        self.sessions_page.refresh()
        self.stats_page.refresh()
        self.settings_page.refresh()
