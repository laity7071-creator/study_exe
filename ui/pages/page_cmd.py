# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import (
    QWidget, QFormLayout, QLineEdit, QPushButton,
    QHBoxLayout, QVBoxLayout, QLabel, QTextEdit,
    QTextBrowser, QComboBox, QSplitter, QFrame,
    QScrollArea, QSizePolicy, QFileDialog
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont
from utils.ui_util import show_info, show_warn, show_error
from utils.logger import logger
from app.config_manager import config_manager
import subprocess
import os


# CMD执行线程
class CMDThread(QThread):
    output_received = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, command):
        super().__init__()
        self.command = command
        self.running = True

    def run(self):
        try:
            process = subprocess.Popen(
                self.command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                shell=True,
                encoding="gbk",
                errors="ignore"
            )

            while self.running and process.poll() is None:
                line = process.stdout.readline()
                if line:
                    self.output_received.emit(line.strip())

            remaining = process.stdout.read()
            if remaining:
                self.output_received.emit(remaining)
        except Exception as e:
            self.output_received.emit(f"执行错误：{str(e)}")
        finally:
            self.finished.emit()

    def stop(self):
        self.running = False


class CMDPage(QWidget):
    def __init__(self):
        super().__init__()
        self.cmd_thread = None
        self.init_ui()
        self.setFont(QFont("Microsoft YaHei", config_manager.get("font_size")))

    def init_ui(self):
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(20)
        main_layout.setAlignment(Qt.AlignTop)
        main_layout.setSizeConstraint(QVBoxLayout.SetMinAndMaxSize)

        # 标题栏
        title_bar = QHBoxLayout()
        title = QLabel("CMD 操作")
        title.setFont(QFont("Microsoft YaHei", 20, QFont.Bold))
        title.setStyleSheet("color: #2c3e50;")
        title_bar.addWidget(title)
        title_bar.addStretch()
        main_layout.addLayout(title_bar)

        # 分割面板
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(3)
        splitter.setStyleSheet("QSplitter::handle { background-color: #e0e0e0; }")
        splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # 左侧：命令编辑区
        cmd_card = self.create_cmd_card()
        splitter.addWidget(cmd_card)

        # 右侧：结果展示区
        result_card = self.create_result_card()
        splitter.addWidget(result_card)

        splitter.setSizes([500, 600])
        main_layout.addWidget(splitter, 1)

    def create_cmd_card(self):
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

        # 子标题 + 模板
        header = QHBoxLayout()
        sub_title = QLabel("CMD 命令编辑")
        sub_title.setFont(QFont("Microsoft YaHei", 16, QFont.Bold))
        sub_title.setStyleSheet("color: #34495e;")
        header.addWidget(sub_title)

        self.cmd_template_combo = QComboBox()
        self.cmd_template_combo.addItems([
            "选择命令模板",
            "ipconfig",
            "dir",
            "ping www.baidu.com",
            "netstat -ano",
            "tasklist"
        ])
        self.cmd_template_combo.setStyleSheet(self.combo_style())
        self.cmd_template_combo.setMaximumWidth(250)
        self.cmd_template_combo.currentTextChanged.connect(self.load_cmd_template)
        header.addWidget(self.cmd_template_combo)
        header.addStretch()
        layout.addLayout(header)

        # 命令编辑框
        self.cmd_edit = QTextEdit()
        self.cmd_edit.setPlaceholderText("请输入CMD命令或脚本内容...")
        self.cmd_edit.setStyleSheet("""
            QTextEdit {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 12px;
                font-family: Consolas, "Courier New", monospace;
                font-size: 14px;
                background-color: #fafafa;
                min-height: 300px;
            }
        """)
        self.cmd_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.cmd_edit, 1)

        # 操作按钮组
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.exec_btn = QPushButton("执行命令")
        self.exec_btn.setStyleSheet(self.primary_btn_style())
        self.exec_btn.clicked.connect(self.execute_cmd)
        btn_layout.addWidget(self.exec_btn)

        self.stop_btn = QPushButton("停止执行")
        self.stop_btn.setStyleSheet(self.warn_btn_style())
        self.stop_btn.clicked.connect(self.stop_cmd)
        self.stop_btn.setEnabled(False)
        btn_layout.addWidget(self.stop_btn)

        # 保存脚本按钮
        save_btn = QPushButton("保存脚本")
        save_btn.setStyleSheet(self.primary_btn_style())
        save_btn.clicked.connect(self.save_cmd_script)
        btn_layout.addWidget(save_btn)

        clear_btn = QPushButton("清空命令")
        clear_btn.setStyleSheet(self.secondary_btn_style())
        clear_btn.clicked.connect(lambda: self.cmd_edit.clear())
        btn_layout.addWidget(clear_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        return card

    def create_result_card(self):
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
        sub_title = QLabel("执行结果")
        sub_title.setFont(QFont("Microsoft YaHei", 16, QFont.Bold))
        sub_title.setStyleSheet("color: #34495e;")
        header.addWidget(sub_title)

        clear_log_btn = QPushButton("清空结果")
        clear_log_btn.setStyleSheet(self.secondary_btn_style())
        clear_log_btn.clicked.connect(lambda: self.result_browser.clear())
        header.addWidget(clear_log_btn)

        copy_log_btn = QPushButton("复制结果")
        copy_log_btn.setStyleSheet(self.secondary_btn_style())
        copy_log_btn.clicked.connect(self.copy_result)
        header.addWidget(copy_log_btn)

        header.addStretch()
        layout.addLayout(header)

        # 结果展示框
        self.result_browser = QTextBrowser()
        self.result_browser.setStyleSheet("""
            QTextBrowser {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 12px;
                font-family: Consolas, "Courier New", monospace;
                font-size: 14px;
                background-color: #fafafa;
                min-height: 300px;
            }
        """)
        self.result_browser.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.result_browser, 1)

        return card

    # ========== 样式方法 ==========
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

    # ========== 功能实现 ==========
    def load_cmd_template(self, text):
        if text != "选择命令模板":
            self.cmd_edit.setText(text)
            logger.info(f"加载CMD模板：{text}")

    def save_cmd_script(self):
        """保存CMD脚本（自动生成.bat后缀）"""
        content = self.cmd_edit.toPlainText().strip()
        if not content:
            show_warn("警告", "脚本内容不能为空！")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存CMD脚本",
            os.path.join(os.path.expanduser("~"), "cmd_script.bat"),
            "批处理文件 (*.bat);;所有文件 (*.*)"
        )

        if file_path:
            # 自动补全后缀
            if not file_path.endswith(".bat"):
                file_path += ".bat"

            try:
                with open(file_path, "w", encoding="gbk") as f:
                    f.write(content)
                config_manager.increment_stat("cmd_script_count")
                show_info("成功", f"CMD脚本已保存到：{file_path}")
                logger.info(f"保存CMD脚本：{file_path}")
            except Exception as e:
                show_error("失败", f"保存脚本失败：{str(e)}")

    def execute_cmd(self):
        cmd = self.cmd_edit.toPlainText().strip()
        if not cmd:
            show_warn("警告", "请输入CMD命令！")
            return

        self.cmd_thread = CMDThread(cmd)
        self.cmd_thread.output_received.connect(self.append_result)
        self.cmd_thread.finished.connect(self.on_cmd_finished)
        self.cmd_thread.start()

        self.exec_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.result_browser.clear()
        logger.info(f"执行CMD命令：{cmd}")

    def stop_cmd(self):
        if self.cmd_thread:
            self.cmd_thread.stop()
            self.exec_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            logger.info("停止CMD命令执行")

    def append_result(self, output):
        self.result_browser.append(output)
        self.result_browser.moveCursor(self.result_browser.textCursor().End)

    def on_cmd_finished(self):
        self.exec_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        logger.info("CMD命令执行完成")

    def copy_result(self):
        text = self.result_browser.toPlainText()
        if not text:
            show_warn("警告", "结果为空！")
            return
        from PyQt5.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        show_info("成功", "结果已复制到剪贴板")