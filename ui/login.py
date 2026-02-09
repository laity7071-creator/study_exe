
# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from core.user import UserManager
import random

def generate_code():
    return "".join(str(random.randint(0, 9)) for _ in range(4))

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.code = generate_code()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("登录")
        self.setFixedSize(400, 320)
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("系统登录")
        title.setStyleSheet("font-size:20px; font-weight:bold;")
        layout.addWidget(title, alignment=Qt.AlignCenter)

        self.user_edit = QLineEdit()
        self.user_edit.setPlaceholderText("账号")
        layout.addWidget(self.user_edit)

        self.pwd_edit = QLineEdit()
        self.pwd_edit.setPlaceholderText("密码")
        self.pwd_edit.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.pwd_edit)

        code_layout = QHBoxLayout()
        self.code_edit = QLineEdit()
        self.code_edit.setPlaceholderText("验证码")
        self.code_label = QLabel(self.code)
        self.code_label.setStyleSheet("background:#eee; padding:6px;")
        code_layout.addWidget(self.code_edit)
        code_layout.addWidget(self.code_label)
        layout.addLayout(code_layout)

        login_btn = QPushButton("登录")
        login_btn.clicked.connect(self.do_login)
        layout.addWidget(login_btn)

        self.setLayout(layout)

    def do_login(self):
        user = self.user_edit.text().strip()
        pwd = self.pwd_edit.text().strip()
        code = self.code_edit.text().strip()

        if not user or not pwd or not code:
            QMessageBox.warning(None, "提示", "请填写完整")
            return

        if code != self.code:
            QMessageBox.warning(None, "错误", "验证码错误")
            self.code = generate_code()
            self.code_label.setText(self.code)
            return

        if UserManager.login(user, pwd):
            QMessageBox.information(None, "成功", "登录成功")
            self.close()
        else:
            QMessageBox.warning(None, "错误", "账号或密码错误")