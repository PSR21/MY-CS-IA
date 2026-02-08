# --- app.py ---
import os
import sys

from PySide6 import QtWidgets

from ui.main_window import MainWindow

QSS = """
QWidget {
    font-family: "Segoe UI", "Arial";
    font-size: 13px;
}
QMainWindow {
    background-color: #f6f7fb;
}
QListWidget {
    background-color: #ffffff;
    border: 1px solid #dcdfe6;
}
QTableWidget {
    background-color: #ffffff;
    border: 1px solid #dcdfe6;
}
QPushButton {
    background-color: #4c72b0;
    color: white;
    padding: 6px 12px;
    border-radius: 4px;
}
QPushButton:hover {
    background-color: #3d5f94;
}
#titleLabel {
    font-size: 20px;
    font-weight: 600;
}
#messageLabel {
    color: #c0392b;
}
"""


def main() -> None:
    os.makedirs("data", exist_ok=True)
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(QSS)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
