# -*- coding: utf-8 -*-
import sys
import os
from utils.logger import logger  # 导入日志系统
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow
from app.signals import signals

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
main_window = None

def main():
    global main_window
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)

    # 临时：跳过登录，直接打开主窗口（方便调试）
    logger.info("调试模式：跳过登录，直接打开主窗口")
    main_window = MainWindow()
    main_window.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()