# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QGridLayout, QScrollArea, QSizePolicy, QPushButton
)
from PyQt5.QtGui import QFont, QColor, QPixmap
from PyQt5.QtCore import Qt, QTimer
from app.config_manager import config_manager
from utils.ui_util import show_info


class MyPage(QWidget):
    def __init__(self):
        super().__init__()
        # 先初始化空布局，延迟加载内容（彻底解决卡顿）
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(QLabel("加载统计数据中...", alignment=Qt.AlignCenter))

        # 延迟100ms加载内容，避免初始化卡顿
        QTimer.singleShot(100, self.init_ui)

    def init_ui(self):
        # 清空临时布局
        for i in reversed(range(self.main_layout.count())):
            self.main_layout.itemAt(i).widget().deleteLater()

        # 设置全局自适应
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # 主布局（滚动+自适应）
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(25)
        main_layout.setAlignment(Qt.AlignTop)
        main_layout.setSizeConstraint(QVBoxLayout.SetMinAndMaxSize)

        # 标题栏（加大字体）
        title = QLabel("使用统计中心")
        title.setFont(QFont("Microsoft YaHei", 22, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 15px;")
        main_layout.addWidget(title)

        # 滚动容器（自适应窗口）
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; }")
        scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # 内容容器
        content_widget = QWidget()
        content_layout = QGridLayout(content_widget)  # 网格布局，更规整
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(20)
        content_layout.setSizeConstraint(QGridLayout.SetMinAndMaxSize)

        # ========== 统计卡片 ==========
        # 1. 数据库统计卡片
        db_card = self.create_stat_card(
            "数据库操作统计",
            [
                ("累计连接次数", config_manager.get_stat("db_connections")),
                ("查询操作次数", config_manager.get_stat("db_select_count")),
                ("插入操作次数", config_manager.get_stat("db_insert_count")),
                ("更新操作次数", config_manager.get_stat("db_update_count")),
                ("删除操作次数", config_manager.get_stat("db_delete_count"))
            ],
            "#4285f4"
        )
        content_layout.addWidget(db_card, 0, 0)

        # 2. SSH统计卡片
        ssh_card = self.create_stat_card(
            "SSH操作统计",
            [
                ("累计连接次数", config_manager.get_stat("ssh_connections")),
                ("命令执行次数", config_manager.get_stat("ssh_command_count")),
                ("历史命令条数", len(config_manager.get_ssh_history())),
                ("最大保存条数", 50)
            ],
            "#f57c00"
        )
        content_layout.addWidget(ssh_card, 0, 1)

        # 3. 脚本统计卡片
        script_card = self.create_stat_card(
            "脚本保存统计",
            [
                ("CMD脚本数", config_manager.get_stat("cmd_script_count")),
                ("PS1脚本数", config_manager.get_stat("ps1_script_count")),
                ("总计脚本数",
                 config_manager.get_stat("cmd_script_count") + config_manager.get_stat("ps1_script_count")),
                ("最后更新时间", config_manager.stats.get("last_update", "暂无"))
            ],
            "#34a853"
        )
        content_layout.addWidget(script_card, 1, 0, 1, 2)  # 跨两列

        # 4. 重置统计按钮
        reset_btn = QPushButton("重置所有统计数据")
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 15px 30px;
                font-size: 16px;
                font-weight: 500;
                min-height: 50px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        reset_btn.clicked.connect(self.reset_stats)
        content_layout.addWidget(reset_btn, 2, 0, 1, 2, Qt.AlignCenter)

        # 组装滚动容器
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

    def create_stat_card(self, title, stats, color):
        """创建统一风格的统计卡片"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #ffffff;
                border-radius: 15px;
                border: 1px solid #e8e8e8;
                padding: 20px;
                font-size: 14px;
                border-left: 5px solid {color};
            }}
            QLabel#card_title {{
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 15px;
            }}
            QLabel#stat_label {{
                font-size: 15px;
                color: #666;
                min-width: 120px;
            }}
            QLabel#stat_value {{
                font-size: 15px;
                font-weight: bold;
                color: {color};
            }}
        """)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        card.setMinimumWidth(400)

        layout = QVBoxLayout(card)
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignTop)

        # 卡片标题
        title_label = QLabel(title)
        title_label.setObjectName("card_title")
        layout.addWidget(title_label)

        # 统计项
        for label_text, value in stats:
            row_layout = QHBoxLayout()
            row_layout.setSpacing(10)

            label = QLabel(f"{label_text}：")
            label.setObjectName("stat_label")
            row_layout.addWidget(label)

            value_label = QLabel(str(value))
            value_label.setObjectName("stat_value")
            row_layout.addWidget(value_label)

            row_layout.addStretch()
            layout.addLayout(row_layout)

        layout.addStretch()
        return card

    def reset_stats(self):
        """重置统计数据"""
        config_manager.stats = config_manager.default_stats
        config_manager.save_stats()
        show_info("成功", "所有统计数据已重置！")
        # 刷新页面
        self.init_ui()