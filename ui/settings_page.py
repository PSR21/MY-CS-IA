# --- ui/settings_page.py ---
from __future__ import annotations

from PySide6 import QtWidgets

from services import StudyService


class SettingsPage(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.service: StudyService | None = None
        layout = QtWidgets.QVBoxLayout(self)

        self.session_length = QtWidgets.QComboBox()
        self.session_length.addItems(["30", "60"])
        self.theme_toggle = QtWidgets.QCheckBox("Dark theme")

        layout.addWidget(QtWidgets.QLabel("Default Session Length"))
        layout.addWidget(self.session_length)
        layout.addWidget(self.theme_toggle)
        layout.addStretch()

    def set_service(self, service: StudyService) -> None:
        self.service = service

    def refresh(self) -> None:
        pass
