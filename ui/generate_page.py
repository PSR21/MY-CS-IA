# --- ui/generate_page.py ---
from __future__ import annotations

from PySide6 import QtCore, QtWidgets

from services import StudyService


class GeneratePage(QtWidgets.QWidget):
    schedule_updated = QtCore.Signal()

    def __init__(self) -> None:
        super().__init__()
        self.service: StudyService | None = None
        layout = QtWidgets.QVBoxLayout(self)

        form = QtWidgets.QFormLayout()
        self.session_length = QtWidgets.QComboBox()
        self.session_length.addItems(["30", "60"])
        self.end_date = QtWidgets.QLineEdit()
        self.end_date.setPlaceholderText("YYYY-MM-DD (optional)")
        form.addRow("Session Length (min)", self.session_length)
        form.addRow("End Date", self.end_date)
        layout.addLayout(form)

        buttons = QtWidgets.QHBoxLayout()
        self.generate_btn = QtWidgets.QPushButton("Generate Schedule")
        self.regen_btn = QtWidgets.QPushButton("Regenerate Schedule")
        buttons.addWidget(self.generate_btn)
        buttons.addWidget(self.regen_btn)
        layout.addLayout(buttons)

        self.message = QtWidgets.QLabel("")
        layout.addWidget(self.message)

        self.generate_btn.clicked.connect(self._generate)
        self.regen_btn.clicked.connect(self._regenerate)

    def set_service(self, service: StudyService) -> None:
        self.service = service

    def refresh(self) -> None:
        pass

    def _generate(self) -> None:
        if not self.service:
            return
        try:
            count, _ = self.service.generate_schedule(int(self.session_length.currentText()), self._end_date())
            self.message.setText(f"Generated {count} sessions.")
            self.schedule_updated.emit()
        except Exception as exc:
            self.message.setText(str(exc))

    def _regenerate(self) -> None:
        if not self.service:
            return
        try:
            count, warning = self.service.regenerate_schedule(int(self.session_length.currentText()), self._end_date())
            text = f"Regenerated {count} sessions."
            if warning:
                text += f" {warning}"
            self.message.setText(text)
            self.schedule_updated.emit()
        except Exception as exc:
            self.message.setText(str(exc))

    def _end_date(self) -> str | None:
        value = self.end_date.text().strip()
        if not value:
            return None
        return value
