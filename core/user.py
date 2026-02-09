# -*- coding: utf-8 -*-
from app.config import config
from app.signals import signals

class UserManager:
    @staticmethod
    def login(username, password):
        admin = config.data.get("admin", {})
        if username == admin.get("username") and password == admin.get("password"):
            print("登录成功，触发login_success信号！")  # 新增打印
            signals.login_success.emit()
            return True
        return False

    @staticmethod
    def get_user_info():
        return config.data.get("user_info", {})

    @staticmethod
    def save_user_info(info):
        config.data["user_info"] = info
        config.save()
        signals.user_info_changed.emit()

    @staticmethod
    def change_password(new_pwd):
        config.data["admin"]["password"] = new_pwd
        config.save()