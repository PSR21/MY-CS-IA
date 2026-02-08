# --- ui/stats_page.py ---
from __future__ import annotations

from PySide6 import QtWidgets

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from services import StudyService


class StatsPage(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.service: StudyService | None = None
        layout = QtWidgets.QVBoxLayout(self)

        self.table = QtWidgets.QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Subject", "Total", "Completed", "Missed", "% Complete"])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        self.figure = Figure(figsize=(5, 3))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

    def set_service(self, service: StudyService) -> None:
        self.service = service

    def refresh(self) -> None:
        if not self.service:
            return
        stats = self.service.get_stats()
        self.table.setRowCount(len(stats))
        for row, entry in enumerate(stats):
            self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(entry["subject"]))
            self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(str(entry["total"])))
            self.table.setItem(row, 2, QtWidgets.QTableWidgetItem(str(entry["completed"])))
            self.table.setItem(row, 3, QtWidgets.QTableWidgetItem(str(entry["missed"])))
            self.table.setItem(row, 4, QtWidgets.QTableWidgetItem(str(entry["completion_pct"])))
        self._render_chart(stats)

    def _render_chart(self, stats: list[dict]) -> None:
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        subjects = [s["subject"] for s in stats]
        values = [s["completion_pct"] for s in stats]
        ax.bar(subjects, values, color="#4c72b0")
        ax.set_ylim(0, 100)
        ax.set_ylabel("Completion %")
        ax.set_title("Study Progress")
        self.figure.tight_layout()
        self.canvas.draw()
