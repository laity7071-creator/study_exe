# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import (
    QWidget, QFormLayout, QLineEdit, QPushButton,
    QHBoxLayout, QVBoxLayout, QLabel, QTextEdit,
    QTextBrowser, QComboBox, QDialog, QSplitter,
    QFrame, QSizePolicy, QListWidget, QListWidgetItem,
    QScrollArea, QMenu, QAction
)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor
from utils.ui_util import show_info, show_warn, show_error
from utils.logger import logger
from app.config_manager import config_manager
import paramiko
import time


# 实时日志读取线程
class SSHLogThread(QThread):
    log_received = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, ssh_client, command):
        super().__init__()
        self.ssh_client = ssh_client
        self.command = command
        self.running = True

    def run(self):
        try:
            stdin, stdout, stderr = self.ssh_client.exec_command(self.command)
            while self.running:
                line = stdout.readline()
                if line:
                    self.log_received.emit(line.strip())
                if stdout.channel.exit_status_ready():
                    break
                time.sleep(0.1)
            # 读取错误信息
            error = stderr.read().strip()
            if error:
                self.log_received.emit(f"错误：{error}")
        except Exception as e:
            self.log_received.emit(f"执行错误：{str(e)}")
        finally:
            self.finished.emit()

    def stop(self):
        self.running = False


class SSHPage(QWidget):
    def __init__(self):
        super().__init__()
        self.ssh_client = None
        self.log_thread = None
        self.init_ui()
        # 设置全局字体
        self.setFont(QFont("Microsoft YaHei", config_manager.get("font_size")))
        # 加载历史命令
        self.load_ssh_history()

    def init_ui(self):
        # 全局自适应
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(20)
        main_layout.setAlignment(Qt.AlignTop)
        main_layout.setSizeConstraint(QVBoxLayout.SetMinAndMaxSize)

        # 标题栏
        title_bar = QHBoxLayout()
        title = QLabel("SSH 操作")
        title.setFont(QFont("Microsoft YaHei", 20, QFont.Bold))
        title.setStyleSheet("color: #2c3e50;")
        title_bar.addWidget(title)
        title_bar.addStretch()
        main_layout.addLayout(title_bar)

        # 连接信息卡片（自适应）
        conn_card = self.create_conn_card()
        main_layout.addWidget(conn_card)

        # 分割面板（跟随窗口缩放）
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(3)
        splitter.setStyleSheet("QSplitter::handle { background-color: #e0e0e0; }")
        splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # 左侧：命令编辑+历史命令
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(15)

        # 命令编辑区
        cmd_card = self.create_cmd_card()
        left_layout.addWidget(cmd_card)

        # 历史命令区
        history_card = self.create_history_card()
        left_layout.addWidget(history_card, 1)

        splitter.addWidget(left_widget)

        # 右侧：实时日志区
        log_card = self.create_log_card()
        splitter.addWidget(log_card)

        # 设置初始分割比例
        splitter.setSizes([500, 600])
        main_layout.addWidget(splitter, 1)

    def create_conn_card(self):
        """连接信息卡片（一键连接本地）"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 12px;
                border: 1px solid #e8e8e8;
                padding: 20px;
                font-size: 14px;
            }
        """)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        layout = QVBoxLayout(card)
        layout.setSpacing(15)

        # 子标题
        sub_title = QLabel("SSH连接信息")
        sub_title.setFont(QFont("Microsoft YaHei", 16, QFont.Bold))
        sub_title.setStyleSheet("color: #34495e; margin-bottom: 10px;")
        layout.addWidget(sub_title)

        # 表单布局
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)

        # 输入框样式
        input_style = """
            QLineEdit {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 10px 12px;
                font-size: 14px;
                background-color: #fafafa;
                min-width: 200px;
                max-width: 400px;
                min-height: 40px;
            }
            QLineEdit:focus {
                border-color: #4285f4;
                background-color: #ffffff;
            }
        """

        # 连接信息输入框
        self.host_edit = QLineEdit("localhost")
        self.host_edit.setStyleSheet(input_style)
        form_layout.addRow(self.create_label("主机"), self.host_edit)

        self.port_edit = QLineEdit("22")
        self.port_edit.setStyleSheet(input_style)
        self.port_edit.setFixedWidth(100)
        form_layout.addRow(self.create_label("端口"), self.port_edit)

        self.user_edit = QLineEdit("root")
        self.user_edit.setStyleSheet(input_style)
        form_layout.addRow(self.create_label("用户名"), self.user_edit)

        self.pwd_edit = QLineEdit("root")  # 默认密码root
        self.pwd_edit.setEchoMode(QLineEdit.Password)
        self.pwd_edit.setStyleSheet(input_style)
        form_layout.addRow(self.create_label("密码"), self.pwd_edit)

        layout.addLayout(form_layout)

        # 按钮组
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        # 一键连接本地按钮
        local_btn = QPushButton("一键连接本地SSH")
        local_btn.setStyleSheet("""
            QPushButton {
                background-color: #34a853;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 500;
                min-width: 180px;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #2d8f46;
            }
        """)
        local_btn.clicked.connect(self.connect_local_ssh)
        btn_layout.addWidget(local_btn)

        # 测试连接按钮
        test_btn = QPushButton("测试连接")
        test_btn.setStyleSheet(self.primary_btn_style())
        test_btn.clicked.connect(self.test_connection)
        btn_layout.addWidget(test_btn)

        # 清空按钮
        clear_btn = QPushButton("清空信息")
        clear_btn.setStyleSheet(self.secondary_btn_style())
        clear_btn.clicked.connect(self.clear_connection)
        btn_layout.addWidget(clear_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        return card

    def create_cmd_card(self):
        """命令编辑卡片"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 12px;
                border: 1px solid #e8e8e8;
                padding: 20px;
                font-size: 14px;
            }
        """)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        layout = QVBoxLayout(card)
        layout.setSpacing(15)

        # 子标题 + 模板
        header = QHBoxLayout()
        sub_title = QLabel("SSH 命令编辑")
        sub_title.setFont(QFont("Microsoft YaHei", 16, QFont.Bold))
        sub_title.setStyleSheet("color: #34495e;")
        header.addWidget(sub_title)

        self.cmd_template_combo = QComboBox()
        self.cmd_template_combo.addItems([
            "选择命令模板",
            "tail -f /var/log/nginx/access.log",
            "ls -l /root",
            "df -h",
            "top -n 1",
            "netstat -tulpn"
        ])
        self.cmd_template_combo.setStyleSheet(self.combo_style())
        self.cmd_template_combo.setMaximumWidth(250)
        self.cmd_template_combo.currentTextChanged.connect(self.load_cmd_template)
        header.addWidget(self.cmd_template_combo)
        header.addStretch()
        layout.addLayout(header)

        # 命令编辑框
        self.cmd_edit = QTextEdit()
        self.cmd_edit.setPlaceholderText("请输入要执行的SSH命令...")
        self.cmd_edit.setStyleSheet("""
                QTextEdit {
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                    padding: 12px;
                    font-family: Consolas, "Courier New", monospace;
                    font-size: 14px;
                    background-color: #fafafa;
                    min-height: 150px;
                }
            """)
        layout.addWidget(self.cmd_edit)

        # 操作按钮组
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.start_btn = QPushButton("开始执行")
        self.start_btn.setStyleSheet(self.primary_btn_style())
        self.start_btn.clicked.connect(self.start_realtime_log)
        btn_layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("停止执行")
        self.stop_btn.setStyleSheet(self.warn_btn_style())
        self.stop_btn.clicked.connect(self.stop_realtime_log)
        self.stop_btn.setEnabled(False)
        btn_layout.addWidget(self.stop_btn)

        clear_cmd_btn = QPushButton("清空命令")
        clear_cmd_btn.setStyleSheet(self.secondary_btn_style())
        clear_cmd_btn.clicked.connect(lambda: self.cmd_edit.clear())
        btn_layout.addWidget(clear_cmd_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        return card

    def create_history_card(self):
        """历史命令卡片"""
        card = QFrame()
        card.setStyleSheet("""
                QFrame {
                    background-color: #ffffff;
                    border-radius: 12px;
                    border: 1px solid #e8e8e8;
                    padding: 20px;
                    font-size: 14px;
                }
            """)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        layout = QVBoxLayout(card)
        layout.setSpacing(15)

        # 子标题
        sub_title = QLabel("SSH 历史命令")
        sub_title.setFont(QFont("Microsoft YaHei", 16, QFont.Bold))
        sub_title.setStyleSheet("color: #34495e;")
        layout.addWidget(sub_title)

        # 历史命令列表
        self.history_list = QListWidget()
        self.history_list.setStyleSheet("""
                QListWidget {
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                    padding: 8px;
                    font-size: 14px;
                    background-color: #fafafa;
                }
                QListWidget::item {
                    padding: 8px;
                    border-bottom: 1px solid #f0f0f0;
                }
                QListWidget::item:selected {
                    background-color: #4285f4;
                    color: white;
                }
            """)
        self.history_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.history_list.itemClicked.connect(self.select_history_command)
        layout.addWidget(self.history_list, 1)

        # 历史命令操作按钮
        history_btn_layout = QHBoxLayout()
        clear_history_btn = QPushButton("清空历史")
        clear_history_btn.setStyleSheet(self.warn_btn_style())
        clear_history_btn.clicked.connect(self.clear_ssh_history)
        history_btn_layout.addWidget(clear_history_btn)

        refresh_history_btn = QPushButton("刷新历史")
        refresh_history_btn.setStyleSheet(self.secondary_btn_style())
        refresh_history_btn.clicked.connect(self.load_ssh_history)
        history_btn_layout.addWidget(refresh_history_btn)

        history_btn_layout.addStretch()
        layout.addLayout(history_btn_layout)

        return card

    def create_log_card(self):
        """实时日志卡片"""
        card = QFrame()
        card.setStyleSheet("""
                QFrame {
                    background-color: #ffffff;
                    border-radius: 12px;
                    border: 1px solid #e8e8e8;
                    padding: 20px;
                    font-size: 14px;
                }
            """)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        layout = QVBoxLayout(card)
        layout.setSpacing(15)

        # 子标题 + 操作
        header = QHBoxLayout()
        sub_title = QLabel("实时日志输出")
        sub_title.setFont(QFont("Microsoft YaHei", 16, QFont.Bold))
        sub_title.setStyleSheet("color: #34495e;")
        header.addWidget(sub_title)

        clear_log_btn = QPushButton("清空日志")
        clear_log_btn.setStyleSheet(self.secondary_btn_style())
        clear_log_btn.clicked.connect(lambda: self.log_browser.clear())
        header.addWidget(clear_log_btn)

        copy_log_btn = QPushButton("复制日志")
        copy_log_btn.setStyleSheet(self.secondary_btn_style())
        copy_log_btn.clicked.connect(self.copy_log)
        header.addWidget(copy_log_btn)

        header.addStretch()
        layout.addLayout(header)

        # 日志展示框
        self.log_browser = QTextBrowser()
        self.log_browser.setStyleSheet("""
                QTextBrowser {
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                    padding: 12px;
                    font-family: Consolas, "Courier New", monospace;
                    font-size: 14px;
                    background-color: #fafafa;
                    min-height: 400px;
                }
            """)
        self.log_browser.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.log_browser, 1)

        return card

    # ========== 工具方法 ==========
    def create_label(self, text):
        label = QLabel(f"{text}：")
        label.setFixedWidth(80)
        label.setFont(QFont("Microsoft YaHei", 14))
        return label

    def primary_btn_style(self):
        return """
                QPushButton {
                    background-color: #4285f4;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 10px 20px;
                    font-size: 14px;
                    font-weight: 500;
                    min-height: 40px;
                }
                QPushButton:hover {
                    background-color: #3367d6;
                }
            """

    def secondary_btn_style(self):
        return """
                QPushButton {
                    background-color: #f1f3f4;
                    color: #202124;
                    border: none;
                    border-radius: 8px;
                    padding: 10px 20px;
                    font-size: 14px;
                    font-weight: 500;
                    min-height: 40px;
                }
                QPushButton:hover {
                    background-color: #e8eaed;
                }
            """

    def warn_btn_style(self):
        return """
                QPushButton {
                    background-color: #f57c00;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 10px 20px;
                    font-size: 14px;
                    font-weight: 500;
                    min-height: 40px;
                }
                QPushButton:hover {
                    background-color: #e06c00;
                }
            """

    def combo_style(self):
        return """
                QComboBox {
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                    padding: 10px 12px;
                    font-size: 14px;
                    background-color: #fafafa;
                    min-height: 40px;
                }
            """

    # ========== 核心功能 ==========
    def connect_local_ssh(self):
        """一键连接本地SSH"""
        self.host_edit.setText("localhost")
        self.port_edit.setText("22")
        self.user_edit.setText("root")
        self.pwd_edit.setText("root")
        show_info("提示", "已填充本地SSH连接信息（默认密码root）！")

    def load_cmd_template(self, text):
        if text != "选择命令模板":
            self.cmd_edit.setText(text)
            logger.info(f"加载SSH命令模板：{text}")

    def load_ssh_history(self):
        """加载SSH历史命令"""
        self.history_list.clear()
        history_commands = config_manager.get_ssh_history()
        for cmd in reversed(history_commands):  # 最新的在上面
            self.history_list.addItem(cmd)

    def select_history_command(self, item):
        """选择历史命令"""
        self.cmd_edit.setText(item.text())

    def clear_ssh_history(self):
        """清空SSH历史命令"""
        config_manager.clear_ssh_history()
        self.load_ssh_history()
        show_info("成功", "SSH历史命令已清空！")

    def clear_connection(self):
        """清空连接信息"""
        self.host_edit.clear()
        self.port_edit.clear()
        self.user_edit.clear()
        self.pwd_edit.clear()
        self.cmd_edit.clear()
        self.log_browser.clear()
        if self.ssh_client:
            self.ssh_client.close()
            self.ssh_client = None
        logger.info("清空SSH连接信息")

    def test_connection(self):
        """测试SSH连接"""
        host = self.host_edit.text().strip()
        port = self.port_edit.text().strip()
        user = self.user_edit.text().strip()
        pwd = self.pwd_edit.text().strip()

        if not host or not port or not user:
            show_warn("警告", "主机/端口/用户名不能为空！")
            return

        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh_client.connect(
                hostname=host,
                port=int(port),
                username=user,
                password=pwd,
                timeout=config_manager.get("ssh_timeout")
            )
            show_info("成功", "SSH连接成功！")
            config_manager.increment_stat("ssh_connections")
            logger.info(f"SSH连接成功：{host}:{port}")
        except Exception as e:
            show_error("失败", f"SSH连接失败：{str(e)}")
            logger.error(f"SSH连接失败：{str(e)}")

    def start_realtime_log(self):
        """开始实时日志查看"""
        if not self.ssh_client:
            show_warn("警告", "请先建立SSH连接！")
            return
        cmd = self.cmd_edit.toPlainText().strip()
        if not cmd:
            show_warn("警告", "请输入要执行的命令！")
            return

        # 保存到历史命令
        config_manager.add_ssh_history(cmd)
        self.load_ssh_history()
        config_manager.increment_stat("ssh_command_count")

        self.log_thread = SSHLogThread(self.ssh_client, cmd)
        self.log_thread.log_received.connect(self.append_log)
        self.log_thread.finished.connect(self.on_log_finished)
        self.log_thread.start()
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.log_browser.clear()
        logger.info(f"开始执行SSH命令：{cmd}")

    def stop_realtime_log(self):
        """停止实时日志查看"""
        if self.log_thread:
            self.log_thread.stop()
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            logger.info("停止SSH命令执行")

    def append_log(self, log):
        """追加日志"""
        self.log_browser.append(log)
        self.log_browser.moveCursor(self.log_browser.textCursor().End)

    def on_log_finished(self):
        """日志执行完成"""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        logger.info("SSH命令执行完成")

    def copy_log(self):
        """复制日志"""
        text = self.log_browser.toPlainText()
        if not text:
            show_warn("警告", "日志为空！")
            return
        from PyQt5.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        show_info("成功", "日志已复制到剪贴板")