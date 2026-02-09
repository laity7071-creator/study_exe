
from PyQt5.QtCore import QObject, pyqtSignal
import sys
import os
class AppSignals(QObject):
    # 登录成功
    login_success = pyqtSignal()
    # 退出登录
    logout = pyqtSignal()
    # 用户信息改变
    user_info_changed = pyqtSignal()

# 全局单例
signals = AppSignals()