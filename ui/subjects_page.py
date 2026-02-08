# --- ui/subjects_page.py ---
from __future__ import annotations

from PySide6 import QtCore, QtWidgets

from models import Subject
from services import StudyService


class SubjectDialog(QtWidgets.QDialog):
    def __init__(self, subject: Subject | None = None, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Subject")
        self.subject = subject
        layout = QtWidgets.QFormLayout(self)

        self.name = QtWidgets.QLineEdit(subject.name if subject else "")
        self.exam_date = QtWidgets.QLineEdit(subject.exam_date if subject else "")
        self.exam_date.setPlaceholderText("YYYY-MM-DD")
        self.difficulty = QtWidgets.QSpinBox()
        self.difficulty.setRange(1, 5)
        if subject:
            self.difficulty.setValue(subject.difficulty)
        self.notes = QtWidgets.QLineEdit(subject.notes if subject and subject.notes else "")

        layout.addRow("Name", self.name)
        layout.addRow("Exam Date", self.exam_date)
        layout.addRow("Difficulty", self.difficulty)
        layout.addRow("Notes", self.notes)

        buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_subject(self) -> Subject:
        subject = self.subject or Subject()
        subject.name = self.name.text().strip()
        subject.exam_date = self.exam_date.text().strip()
        subject.difficulty = self.difficulty.value()
        subject.notes = self.notes.text().strip() or None
        return subject


class SubjectsPage(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.service: StudyService | None = None
        layout = QtWidgets.QVBoxLayout(self)

        self.table = QtWidgets.QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Name", "Exam Date", "Difficulty", "Notes"])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        buttons = QtWidgets.QHBoxLayout()
        self.add_btn = QtWidgets.QPushButton("Add")
        self.edit_btn = QtWidgets.QPushButton("Edit")
        self.delete_btn = QtWidgets.QPushButton("Delete")
        buttons.addWidget(self.add_btn)
        buttons.addWidget(self.edit_btn)
        buttons.addWidget(self.delete_btn)
        layout.addLayout(buttons)

        self.message = QtWidgets.QLabel("")
        layout.addWidget(self.message)

        self.add_btn.clicked.connect(self._add)
        self.edit_btn.clicked.connect(self._edit)
        self.delete_btn.clicked.connect(self._delete)

    def set_service(self, service: StudyService) -> None:
        self.service = service

    def refresh(self) -> None:
        if not self.service:
            return
        subjects = self.service.data.subjects
        self.table.setRowCount(len(subjects))
        for row, subject in enumerate(subjects):
            self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(subject.name))
            self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(subject.exam_date))
            self.table.setItem(row, 2, QtWidgets.QTableWidgetItem(str(subject.difficulty)))
            self.table.setItem(row, 3, QtWidgets.QTableWidgetItem(subject.notes or ""))
            self.table.setVerticalHeaderItem(row, QtWidgets.QTableWidgetItem(subject.id))

    def _current_subject(self) -> Subject | None:
        if not self.service:
            return None
        row = self.table.currentRow()
        if row < 0:
            return None
        subject_id = self.table.verticalHeaderItem(row).text()
        for subject in self.service.data.subjects:
            if subject.id == subject_id:
                return subject
        return None

    def _add(self) -> None:
        if not self.service:
            return
        dialog = SubjectDialog(parent=self)
        if dialog.exec() == QtWidgets.QDialog.Accepted:
            try:
                self.service.add_subject(dialog.get_subject())
                self.message.setText("Subject added.")
                self.refresh()
            except Exception as exc:
                self.message.setText(str(exc))

    def _edit(self) -> None:
        if not self.service:
            return
        subject = self._current_subject()
        if not subject:
            self.message.setText("Select a subject to edit.")
            return
        dialog = SubjectDialog(subject=subject, parent=self)
        if dialog.exec() == QtWidgets.QDialog.Accepted:
            try:
                self.service.update_subject(dialog.get_subject())
                self.message.setText("Subject updated.")
                self.refresh()
            except Exception as exc:
                self.message.setText(str(exc))

    def _delete(self) -> None:
        if not self.service:
            return
        subject = self._current_subject()
        if not subject:
            self.message.setText("Select a subject to delete.")
            return
        self.service.delete_subject(subject.id)
        self.message.setText("Subject deleted.")
        self.refresh()
