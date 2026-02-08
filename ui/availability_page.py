# --- ui/availability_page.py ---
from __future__ import annotations

from PySide6 import QtCore, QtWidgets

from models import AvailabilitySlot
from services import StudyService


class AvailabilityDialog(QtWidgets.QDialog):
    def __init__(self, slot: AvailabilitySlot | None = None, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Availability Slot")
        self.slot = slot
        layout = QtWidgets.QFormLayout(self)

        self.day = QtWidgets.QComboBox()
        self.day.addItems(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
        if slot:
            self.day.setCurrentText(slot.day_of_week)
        self.start = QtWidgets.QLineEdit(slot.start_time if slot else "")
        self.start.setPlaceholderText("HH:MM")
        self.end = QtWidgets.QLineEdit(slot.end_time if slot else "")
        self.end.setPlaceholderText("HH:MM")

        layout.addRow("Day", self.day)
        layout.addRow("Start", self.start)
        layout.addRow("End", self.end)

        buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_slot(self) -> AvailabilitySlot:
        slot = self.slot or AvailabilitySlot()
        slot.day_of_week = self.day.currentText()
        slot.start_time = self.start.text().strip()
        slot.end_time = self.end.text().strip()
        return slot


class AvailabilityPage(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.service: StudyService | None = None
        layout = QtWidgets.QVBoxLayout(self)

        self.table = QtWidgets.QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Day", "Start", "End"])
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
        slots = self.service.data.availability
        self.table.setRowCount(len(slots))
        for row, slot in enumerate(slots):
            self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(slot.day_of_week))
            self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(slot.start_time))
            self.table.setItem(row, 2, QtWidgets.QTableWidgetItem(slot.end_time))
            self.table.setVerticalHeaderItem(row, QtWidgets.QTableWidgetItem(slot.id))

    def _current_slot(self) -> AvailabilitySlot | None:
        if not self.service:
            return None
        row = self.table.currentRow()
        if row < 0:
            return None
        slot_id = self.table.verticalHeaderItem(row).text()
        for slot in self.service.data.availability:
            if slot.id == slot_id:
                return slot
        return None

    def _add(self) -> None:
        if not self.service:
            return
        dialog = AvailabilityDialog(parent=self)
        if dialog.exec() == QtWidgets.QDialog.Accepted:
            try:
                self.service.add_availability(dialog.get_slot())
                self.message.setText("Availability added.")
                self.refresh()
            except Exception as exc:
                self.message.setText(str(exc))

    def _edit(self) -> None:
        if not self.service:
            return
        slot = self._current_slot()
        if not slot:
            self.message.setText("Select a slot to edit.")
            return
        dialog = AvailabilityDialog(slot=slot, parent=self)
        if dialog.exec() == QtWidgets.QDialog.Accepted:
            try:
                self.service.update_availability(dialog.get_slot())
                self.message.setText("Availability updated.")
                self.refresh()
            except Exception as exc:
                self.message.setText(str(exc))

    def _delete(self) -> None:
        if not self.service:
            return
        slot = self._current_slot()
        if not slot:
            self.message.setText("Select a slot to delete.")
            return
        self.service.delete_availability(slot.id)
        self.message.setText("Availability deleted.")
        self.refresh()
