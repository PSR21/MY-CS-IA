# --- ui/login.py ---
from __future__ import annotations

from PySide6 import QtCore, QtWidgets


class LoginPage(QtWidgets.QWidget):
    logged_in = QtCore.Signal(str)
    registered = QtCore.Signal(str)

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignCenter)

        title = QtWidgets.QLabel("Smart Study Schedule Generator")
        title.setObjectName("titleLabel")
        layout.addWidget(title)

        form = QtWidgets.QFormLayout()
        self.username = QtWidgets.QLineEdit()
        self.password = QtWidgets.QLineEdit()
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        form.addRow("Username", self.username)
        form.addRow("Password", self.password)

        layout.addLayout(form)

        self.message = QtWidgets.QLabel("")
        self.message.setObjectName("messageLabel")
        layout.addWidget(self.message)

        button_row = QtWidgets.QHBoxLayout()
        self.login_btn = QtWidgets.QPushButton("Login")
        self.register_btn = QtWidgets.QPushButton("Register")
        button_row.addWidget(self.login_btn)
        button_row.addWidget(self.register_btn)
        layout.addLayout(button_row)

        self.login_btn.clicked.connect(self._handle_login)
        self.register_btn.clicked.connect(self._handle_register)

    def _handle_login(self) -> None:
        self.logged_in.emit(self.username.text().strip())

    def _handle_register(self) -> None:
        self.registered.emit(self.username.text().strip())

    def set_message(self, text: str) -> None:
        self.message.setText(text)
