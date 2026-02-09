# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QMainWindow, QTabWidget, QWidget, QLabel, QVBoxLayout, QScrollArea
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont  # 补全缺失的导入！
from app.signals import signals

# 延迟导入页面（避免初始化卡顿）
def lazy_import_page_my():
    from ui.pages.page_my import MyPage
    return MyPage()

def lazy_import_page_db():
    from ui.pages.page_db import DBPage
    return DBPage()

def lazy_import_page_ssh():
    from ui.pages.page_ssh import SSHPage
    return SSHPage()

def lazy_import_page_cmd():
    from ui.pages.page_cmd import CMDPage
    return CMDPage()

def lazy_import_page_ps1():
    from ui.pages.page_ps1 import PS1Page
    return PS1Page()

def lazy_import_page_settings():
    from ui.pages.page_settings import SettingsPage
    return SettingsPage()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Python多功能工具")
        self.setMinimumSize(1000, 700)  # 最小窗口尺寸，避免缩太小
        self.init_ui()
        self.bind_signals()

    def init_ui(self):
        # 创建标签页容器
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        # 先添加占位页，切换时再加载真实页面
        self.tab_widget.addTab(self.create_placeholder("我的"), "我的")
        self.tab_widget.addTab(self.create_placeholder("数据库操作"), "数据库操作")
        self.tab_widget.addTab(self.create_placeholder("SSH操作"), "SSH操作")
        self.tab_widget.addTab(self.create_placeholder("CMD操作"), "CMD操作")
        self.tab_widget.addTab(self.create_placeholder("PS1操作"), "PS1操作")
        self.tab_widget.addTab(self.create_placeholder("设置"), "设置")

        # 绑定标签页切换事件
        self.tab_widget.currentChanged.connect(self.on_tab_changed)

    def create_placeholder(self, text):
        """创建自适应占位页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignCenter)
        label = QLabel(f"加载{text}中...")
        label.setFont(QFont("Microsoft YaHei", 14))  # 现在QFont已导入，不会报错
        layout.addWidget(label)
        return widget

    def on_tab_changed(self, index):
        """切换标签页时加载真实页面"""
        tab_text = self.tab_widget.tabText(index)
        current_widget = self.tab_widget.widget(index)

        # 避免重复加载
        if tab_text == "我的" and "MyPage" not in str(type(current_widget)):
            self.tab_widget.removeTab(index)
            self.tab_widget.insertTab(index, lazy_import_page_my(), "我的")
            self.tab_widget.setCurrentIndex(index)

        elif tab_text == "数据库操作" and "DBPage" not in str(type(current_widget)):
            self.tab_widget.removeTab(index)
            self.tab_widget.insertTab(index, lazy_import_page_db(), "数据库操作")
            self.tab_widget.setCurrentIndex(index)

        elif tab_text == "SSH操作" and "SSHPage" not in str(type(current_widget)):
            self.tab_widget.removeTab(index)
            self.tab_widget.insertTab(index, lazy_import_page_ssh(), "SSH操作")
            self.tab_widget.setCurrentIndex(index)

        elif tab_text == "CMD操作" and "CMDPage" not in str(type(current_widget)):
            self.tab_widget.removeTab(index)
            self.tab_widget.insertTab(index, lazy_import_page_cmd(), "CMD操作")
            self.tab_widget.setCurrentIndex(index)

        elif tab_text == "PS1操作" and "PS1Page" not in str(type(current_widget)):
            self.tab_widget.removeTab(index)
            self.tab_widget.insertTab(index, lazy_import_page_ps1(), "PS1操作")
            self.tab_widget.setCurrentIndex(index)

        elif tab_text == "设置" and "SettingsPage" not in str(type(current_widget)):
            self.tab_widget.removeTab(index)
            self.tab_widget.insertTab(index, lazy_import_page_settings(), "设置")
            self.tab_widget.setCurrentIndex(index)

    def bind_signals(self):
        signals.logout.connect(self.close)