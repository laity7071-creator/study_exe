# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFrame, QListWidget, QListWidgetItem,
    QStackedWidget, QSlider, QCheckBox, QComboBox,
    QLineEdit, QScrollArea, QSizePolicy
)
from PyQt5.QtCore import Qt, QSize, QEvent
from PyQt5.QtGui import QFont, QPalette, QColor, QBrush
from app.signals import signals
from utils.ui_util import show_info, show_warn
from app.config_manager import config_manager


class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_saved_settings()
        # 监听全局字体变化
        self.setFont(QFont("Microsoft YaHei", config_manager.get("font_size")))
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        """全局字体更新事件"""
        if event.type() == QEvent.FontChange:
            self.update_all_fonts()
        return super().eventFilter(obj, event)

    def update_all_fonts(self):
        """更新所有子控件字体"""
        font = self.font()
        for child in self.findChildren(QWidget):
            child.setFont(font)

    def init_ui(self):
        # 设置全局大小策略（跟随窗口缩放）
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # 主布局：水平分割（左侧导航 + 右侧滚动内容）
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.setSizeConstraint(QVBoxLayout.SetMinAndMaxSize)

        # 左侧导航栏（固定宽度，自适应高度）
        nav_bar = QListWidget()
        nav_bar.setStyleSheet("""
            QListWidget {
                background-color: #f5f5f5;
                border-right: 1px solid #e0e0e0;
                padding: 10px;
                font-size: 14px;  # 调大字体
            }
            QListWidgetItem {
                height: 45px;
                border-radius: 8px;
                padding-left: 16px;
                margin: 4px 0;
                font-size: 14px;
            }
            QListWidgetItem:selected {
                background-color: #4285f4;
                color: white;
            }
        """)
        nav_bar.setFixedWidth(200)
        nav_bar.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        # 导航项
        nav_items = ["通用设置", "外观与体验", "工具设置", "关于我们"]
        for item in nav_items:
            QListWidgetItem(item, nav_bar)

        # 右侧滚动容器（自适应窗口）
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; }")
        scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # 右侧内容栈（自适应）
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.stacked_widget.setMinimumWidth(700)
        self.general_page = self.create_general_page()
        self.appearance_page = self.create_appearance_page()
        self.tools_page = self.create_tools_page()
        self.about_page = self.create_about_page()

        self.stacked_widget.addWidget(self.general_page)
        self.stacked_widget.addWidget(self.appearance_page)
        self.stacked_widget.addWidget(self.tools_page)
        self.stacked_widget.addWidget(self.about_page)

        scroll_area.setWidget(self.stacked_widget)
        nav_bar.currentRowChanged.connect(self.stacked_widget.setCurrentIndex)

        # 组装布局
        main_layout.addWidget(nav_bar)
        main_layout.addWidget(scroll_area)

    def load_saved_settings(self):
        """加载已保存的设置"""
        # 通用设置
        self.auto_start_cb.setChecked(config_manager.get("auto_start"))
        self.remember_login_cb.setChecked(config_manager.get("remember_login"))

        # 外观设置
        theme = config_manager.get("theme")
        self.theme_combo.setCurrentText({"light": "浅色", "dark": "深色", "system": "跟随系统"}.get(theme, "浅色"))

        font_size = config_manager.get("font_size")
        self.font_slider.setValue(font_size)
        self.font_value.setText(f"{font_size}px")

        brightness = config_manager.get("brightness")
        self.brightness_slider.setValue(brightness)
        self.brightness_value.setText(f"{brightness * 10}%")

        # 工具设置
        self.sql_timeout_edit.setText(str(config_manager.get("sql_timeout")))
        self.ssh_timeout_edit.setText(str(config_manager.get("ssh_timeout")))
        self.log_level_combo.setCurrentText(config_manager.get("log_level"))

    def create_general_page(self):
        """通用设置（修复显示问题）"""
        page = QWidget()
        page.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(24)
        layout.setAlignment(Qt.AlignTop)
        layout.setSizeConstraint(QVBoxLayout.SetMinAndMaxSize)

        # 标题（加大字体）
        title = QLabel("通用设置")
        title.setFont(QFont("Microsoft YaHei", 20, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        layout.addWidget(title)

        # 功能组1：账号相关
        group1 = QFrame()
        group1.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 12px;
                border: 1px solid #e8e8e8;
                padding: 20px;
                font-size: 14px;
            }
        """)
        group1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        group1_layout = QVBoxLayout(group1)
        group1_layout.setSpacing(20)

        logout_btn = QPushButton("退出登录")
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 500;
                max-width: 200px;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        logout_btn.clicked.connect(self.logout)
        group1_layout.addWidget(logout_btn)

        # 开机自启
        self.auto_start_cb = QCheckBox("开机自动启动程序")
        self.auto_start_cb.setStyleSheet("QCheckBox { font-size: 14px; margin: 10px 0; }")
        self.auto_start_cb.stateChanged.connect(
            lambda: config_manager.set("auto_start", self.auto_start_cb.isChecked()))
        group1_layout.addWidget(self.auto_start_cb)

        # 记住登录
        self.remember_login_cb = QCheckBox("记住登录状态（下次免登录）")
        self.remember_login_cb.setStyleSheet("QCheckBox { font-size: 14px; margin: 10px 0; }")
        self.remember_login_cb.stateChanged.connect(
            lambda: config_manager.set("remember_login", self.remember_login_cb.isChecked()))
        group1_layout.addWidget(self.remember_login_cb)

        # 保存按钮
        save_btn = QPushButton("保存通用设置")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4285f4;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                max-width: 200px;
                min-height: 40px;
            }
        """)
        save_btn.clicked.connect(lambda: show_info("成功", "通用设置已保存！"))
        group1_layout.addWidget(save_btn)

        layout.addWidget(group1)
        layout.addStretch()
        return page

    def create_appearance_page(self):
        """外观设置（修复字体/颜色生效）"""
        page = QWidget()
        page.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(24)
        layout.setAlignment(Qt.AlignTop)
        layout.setSizeConstraint(QVBoxLayout.SetMinAndMaxSize)

        title = QLabel("外观与体验")
        title.setFont(QFont("Microsoft YaHei", 20, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        layout.addWidget(title)

        # 功能组：外观设置
        group = QFrame()
        group.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 12px;
                border: 1px solid #e8e8e8;
                padding: 20px;
                font-size: 14px;
            }
        """)
        group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(20)

        # 主题切换（修复显示/生效）
        theme_layout = QHBoxLayout()
        theme_layout.setSpacing(15)
        theme_label = QLabel("界面主题：")
        theme_label.setFixedWidth(100)
        theme_label.setFont(QFont("Microsoft YaHei", 14))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["浅色", "深色", "跟随系统"])
        self.theme_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 10px 15px;
                font-size: 14px;
                min-width: 200px;
                max-width: 250px;
                min-height: 40px;
            }
            QComboBox QAbstractItemView {
                font-size: 14px;
                padding: 10px;
            }
        """)
        self.theme_combo.currentTextChanged.connect(self.change_theme)
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        group_layout.addLayout(theme_layout)

        # 字体大小（全局生效）
        font_layout = QHBoxLayout()
        font_layout.setSpacing(15)
        font_label = QLabel("字体大小：")
        font_label.setFixedWidth(100)
        font_label.setFont(QFont("Microsoft YaHei", 14))
        self.font_slider = QSlider(Qt.Horizontal)
        self.font_slider.setRange(12, 18)  # 扩大范围
        self.font_slider.setValue(config_manager.get("font_size"))
        self.font_slider.setFixedWidth(300)
        self.font_slider.setStyleSheet("QSlider { height: 20px; }")
        self.font_value = QLabel(f"{config_manager.get('font_size')}px")
        self.font_value.setFixedWidth(80)
        self.font_value.setFont(QFont("Microsoft YaHei", 14))
        self.font_slider.valueChanged.connect(self.change_font_size)
        font_layout.addWidget(font_label)
        font_layout.addWidget(self.font_slider)
        font_layout.addWidget(self.font_value)
        font_layout.addStretch()
        group_layout.addLayout(font_layout)

        # 亮度调节（修复逻辑）
        brightness_layout = QHBoxLayout()
        brightness_layout.setSpacing(15)
        brightness_label = QLabel("界面亮度：")
        brightness_label.setFixedWidth(100)
        brightness_label.setFont(QFont("Microsoft YaHei", 14))
        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setRange(1, 20)
        self.brightness_slider.setValue(config_manager.get("brightness"))
        self.brightness_slider.setFixedWidth(300)
        self.brightness_value = QLabel(f"{config_manager.get('brightness') * 10}%")
        self.brightness_value.setFixedWidth(80)
        self.brightness_value.setFont(QFont("Microsoft YaHei", 14))
        self.brightness_slider.valueChanged.connect(self.change_brightness)
        brightness_layout.addWidget(brightness_label)
        brightness_layout.addWidget(self.brightness_slider)
        brightness_layout.addWidget(self.brightness_value)
        brightness_layout.addStretch()
        group_layout.addLayout(brightness_layout)

        # 保存按钮
        save_btn = QPushButton("保存外观设置")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4285f4;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                max-width: 200px;
                min-height: 40px;
            }
        """)
        save_btn.clicked.connect(self.save_appearance_settings)
        group_layout.addWidget(save_btn)

        layout.addWidget(group)
        layout.addStretch()
        return page

    def create_tools_page(self):
        """工具设置（修复显示）"""
        page = QWidget()
        page.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(24)
        layout.setAlignment(Qt.AlignTop)
        layout.setSizeConstraint(QVBoxLayout.SetMinAndMaxSize)

        title = QLabel("工具设置")
        title.setFont(QFont("Microsoft YaHei", 20, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        layout.addWidget(title)

        # 功能组：工具配置
        group = QFrame()
        group.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 12px;
                border: 1px solid #e8e8e8;
                padding: 20px;
                font-size: 14px;
            }
        """)
        group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(20)

        # SQL超时时间
        timeout_layout = QHBoxLayout()
        timeout_layout.setSpacing(15)
        timeout_label = QLabel("SQL执行超时：")
        timeout_label.setFixedWidth(120)
        timeout_label.setFont(QFont("Microsoft YaHei", 14))
        self.sql_timeout_edit = QLineEdit()
        self.sql_timeout_edit.setStyleSheet("""
            QLineEdit {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 10px 15px;
                font-size: 14px;
                min-width: 100px;
                max-width: 120px;
                min-height: 40px;
            }
        """)
        timeout_unit = QLabel("秒")
        timeout_unit.setFixedWidth(50)
        timeout_unit.setFont(QFont("Microsoft YaHei", 14))
        timeout_layout.addWidget(timeout_label)
        timeout_layout.addWidget(self.sql_timeout_edit)
        timeout_layout.addWidget(timeout_unit)
        timeout_layout.addStretch()
        group_layout.addLayout(timeout_layout)

        # SSH超时时间
        ssh_timeout_layout = QHBoxLayout()
        ssh_timeout_layout.setSpacing(15)
        ssh_timeout_label = QLabel("SSH连接超时：")
        ssh_timeout_label.setFixedWidth(120)
        ssh_timeout_label.setFont(QFont("Microsoft YaHei", 14))
        self.ssh_timeout_edit = QLineEdit()
        self.ssh_timeout_edit.setStyleSheet("""
            QLineEdit {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 10px 15px;
                font-size: 14px;
                min-width: 100px;
                max-width: 120px;
                min-height: 40px;
            }
        """)
        ssh_timeout_unit = QLabel("秒")
        ssh_timeout_unit.setFixedWidth(50)
        ssh_timeout_unit.setFont(QFont("Microsoft YaHei", 14))
        ssh_timeout_layout.addWidget(ssh_timeout_label)
        ssh_timeout_layout.addWidget(self.ssh_timeout_edit)
        ssh_timeout_layout.addWidget(ssh_timeout_unit)
        ssh_timeout_layout.addStretch()
        group_layout.addLayout(ssh_timeout_layout)

        # 日志级别
        log_level_layout = QHBoxLayout()
        log_level_layout.setSpacing(15)
        log_level_label = QLabel("日志级别：")
        log_level_label.setFixedWidth(120)
        log_level_label.setFont(QFont("Microsoft YaHei", 14))
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        self.log_level_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 10px 15px;
                font-size: 14px;
                min-width: 150px;
                max-width: 200px;
                min-height: 40px;
            }
        """)
        log_level_layout.addWidget(log_level_label)
        log_level_layout.addWidget(self.log_level_combo)
        log_level_layout.addStretch()
        group_layout.addLayout(log_level_layout)

        # 保存按钮
        save_btn = QPushButton("保存工具设置")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4285f4;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                max-width: 200px;
                min-height: 40px;
            }
        """)
        save_btn.clicked.connect(self.save_tools_settings)
        group_layout.addWidget(save_btn)

        layout.addWidget(group)
        layout.addStretch()
        return page

    def create_about_page(self):
        """关于我们（修复显示）"""
        page = QWidget()
        page.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)
        layout.setAlignment(Qt.AlignCenter)

        version_label = QLabel("Python多功能工具 v1.0.0")
        version_label.setFont(QFont("Microsoft YaHei", 22, QFont.Bold))
        version_label.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        layout.addWidget(version_label)

        copyright_label = QLabel("© 2026 豆包助手 | 基于PyQt5开发")
        copyright_label.setStyleSheet("color: #666; font-size: 16px; margin-bottom: 15px;")
        layout.addWidget(copyright_label)

        link_label = QLabel('<a href="https://www.example.com">访问官网获取更多帮助</a>')
        link_label.setOpenExternalLinks(True)
        link_label.setStyleSheet("color: #4285f4; font-size: 16px;")
        layout.addWidget(link_label)

        layout.addStretch()
        return page

    # ========== 核心功能修复 ==========
    def change_theme(self, text):
        """修复主题切换（全局生效+回退正常）"""
        theme_map = {"浅色": "light", "深色": "dark", "跟随系统": "system"}
        theme = theme_map.get(text, "light")
        config_manager.set("theme", theme)

        # 实时切换全局主题
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtGui import QPalette, QColor
        app = QApplication.instance()

        # 保存原始调色板（用于回退）
        if not hasattr(self, 'original_palette'):
            self.original_palette = app.palette()

        palette = QPalette()

        if theme == "dark":
            # 深色主题（修复颜色值，确保所有控件生效）
            palette.setColor(QPalette.Window, QColor(30, 30, 30))
            palette.setColor(QPalette.WindowText, QColor(240, 240, 240))
            palette.setColor(QPalette.Base, QColor(40, 40, 40))
            palette.setColor(QPalette.AlternateBase, QColor(50, 50, 50))
            palette.setColor(QPalette.Text, QColor(240, 240, 240))
            palette.setColor(QPalette.Button, QColor(50, 50, 50))
            palette.setColor(QPalette.ButtonText, QColor(240, 240, 240))
            palette.setColor(QPalette.Highlight, QColor(66, 133, 244))
            palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
            palette.setColor(QPalette.ToolTipBase, QColor(50, 50, 50))
            palette.setColor(QPalette.ToolTipText, QColor(240, 240, 240))
        elif theme == "light":
            # 浅色主题（恢复原始调色板，解决回退失败）
            palette = self.original_palette
        else:  # 跟随系统
            # 使用系统默认调色板
            palette = QApplication.style().standardPalette()

        # 全局应用调色板
        app.setPalette(palette)

        # 强制刷新所有窗口和控件
        for window in app.topLevelWidgets():
            window.setPalette(palette)
            window.update()
            for child in window.findChildren(QWidget):
                child.setPalette(palette)
                child.update()

    def change_font_size(self, value):
        """修复字体全局生效"""
        self.font_value.setText(f"{value}px")
        config_manager.set("font_size", value)

        # 全局更新字体
        from PyQt5.QtWidgets import QApplication
        app = QApplication.instance()
        font = QFont("Microsoft YaHei", value)
        app.setFont(font)

        # 强制刷新所有控件
        self.update_all_fonts()
        for window in app.topLevelWidgets():
            window.setFont(font)
            for child in window.findChildren(QWidget):
                child.setFont(font)

    def change_brightness(self, value):
        """修复亮度调节"""
        self.brightness_value.setText(f"{value * 10}%")
        config_manager.set("brightness", value)

        # 亮度生效逻辑（通过调整窗口透明度）
        from PyQt5.QtWidgets import QApplication
        app = QApplication.instance()
        brightness = value / 10  # 0.1-2.0
        for window in app.topLevelWidgets():
            window.setWindowOpacity(min(max(brightness, 0.5), 1.0))

    def save_appearance_settings(self):
        config_manager.set("theme",
                           {"浅色": "light", "深色": "dark", "跟随系统": "system"}.get(self.theme_combo.currentText(),
                                                                                       "light"))
        config_manager.set("font_size", self.font_slider.value())
        config_manager.set("brightness", self.brightness_slider.value())
        show_info("成功", "外观设置已保存，所有修改实时生效！")

    def save_tools_settings(self):
        try:
            sql_timeout = int(self.sql_timeout_edit.text().strip())
            ssh_timeout = int(self.ssh_timeout_edit.text().strip())
            log_level = self.log_level_combo.currentText()

            config_manager.set("sql_timeout", sql_timeout)
            config_manager.set("ssh_timeout", ssh_timeout)
            config_manager.set("log_level", log_level)

            # 实时修改日志级别
            import logging
            logger = logging.getLogger()
            logger.setLevel(getattr(logging, log_level))

            show_info("成功", "工具设置已保存！")
        except:
            show_warn("错误", "请输入有效的数字！")

    def logout(self):
        show_info("提示", "已退出登录，即将返回登录页！")
        signals.logout.emit()