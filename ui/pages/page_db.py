# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import (
    QWidget, QFormLayout, QLineEdit, QPushButton,
    QHBoxLayout, QVBoxLayout, QLabel, QTextEdit,
    QTextBrowser, QComboBox, QSplitter, QFrame,
    QSizePolicy, QListWidget  # 补全QListWidget导入，移除未使用的导入
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont
from utils.ui_util import show_info, show_warn, show_error
from utils.logger import logger
from app.config_manager import config_manager
import pymysql


# SQL执行线程（修复信号发射方式）
class SQLThread(QThread):
    result_signal = pyqtSignal(bool, str)
    finished_signal = pyqtSignal()

    def __init__(self, host, port, user, pwd, dbname, sql):
        super().__init__()
        self.host = host
        self.port = port
        self.user = user
        self.pwd = pwd
        self.dbname = dbname
        self.sql = sql

    def run(self):
        try:
            conn = pymysql.connect(
                host=self.host,
                port=int(self.port),
                user=self.user,
                password=self.pwd,
                database=self.dbname,
                charset='utf8mb4',
                connect_timeout=config_manager.get("sql_timeout")
            )
            cursor = conn.cursor()

            # 统计连接次数
            config_manager.increment_stat("db_connections")

            # 执行SQL并统计操作类型
            sql_upper = self.sql.strip().upper()
            if sql_upper.startswith("SELECT"):
                config_manager.increment_stat("db_select_count")
            elif sql_upper.startswith("INSERT"):
                config_manager.increment_stat("db_insert_count")
            elif sql_upper.startswith("UPDATE"):
                config_manager.increment_stat("db_update_count")
            elif sql_upper.startswith("DELETE"):
                config_manager.increment_stat("db_delete_count")

            cursor.execute(self.sql)
            conn.commit()

            # 获取结果
            if sql_upper.startswith("SELECT"):
                results = cursor.fetchall()
                result_text = "\n".join([str(row) for row in results])
            else:
                result_text = f"执行成功，影响行数：{cursor.rowcount}"

            # 修复：必须通过self.信号名.emit()发射信号
            self.result_signal.emit(True, result_text)
            cursor.close()
            conn.close()
        except Exception as e:
            self.result_signal.emit(False, str(e))
        finally:
            self.finished_signal.emit()


class DBPage(QWidget):
    def __init__(self):
        super().__init__()
        self.sql_thread = None
        self.init_ui()
        # 设置全局字体
        self.setFont(QFont("Microsoft YaHei", config_manager.get("font_size")))

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
        title = QLabel("数据库操作")
        title.setFont(QFont("Microsoft YaHei", 20, QFont.Bold))  # QFont.Bold是int，忽略类型提示误报
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

        # 左侧容器（SQL编辑 + 历史记录）
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)

        # SQL编辑区（自适应）
        sql_edit_card = self.create_sql_edit_card()
        left_layout.addWidget(sql_edit_card)

        # SQL历史记录区（新增）
        sql_history_card = self.create_sql_history_card()
        left_layout.addWidget(sql_history_card, 1)

        splitter.addWidget(left_widget)

        # 右侧：结果展示区（自适应）
        result_card = self.create_result_card()
        splitter.addWidget(result_card)

        # 设置初始分割比例
        splitter.setSizes([500, 600])
        main_layout.addWidget(splitter, 1)  # 占满剩余空间

    def create_conn_card(self):
        """连接信息卡片（添加一键连接本地）"""
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
        sub_title = QLabel("数据库连接信息")
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

        self.port_edit = QLineEdit("3306")
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

        self.dbname_edit = QLineEdit()
        self.dbname_edit.setPlaceholderText("请输入数据库名")
        self.dbname_edit.setStyleSheet(input_style)
        form_layout.addRow(self.create_label("数据库名"), self.dbname_edit)

        layout.addLayout(form_layout)

        # 按钮组（恢复美观样式）
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        btn_layout.setAlignment(Qt.AlignCenter)

        # 一键连接本地按钮（主色调）
        local_btn = QPushButton("一键连接本地MySQL")
        local_btn.setStyleSheet("""
            QPushButton {
                background-color: #4285f4;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 28px;
                font-size: 14px;
                font-weight: 600;
                min-width: 200px;
                min-height: 45px;
                box-shadow: 0 2px 5px rgba(66, 133, 244, 0.3);
            }
            QPushButton:hover {
                background-color: #3367d6;
                box-shadow: 0 3px 8px rgba(66, 133, 244, 0.4);
            }
            QPushButton:pressed {
                background-color: #2850a7;
                box-shadow: 0 1px 3px rgba(66, 133, 244, 0.3);
            }
        """)
        local_btn.clicked.connect(self.connect_local_mysql)
        btn_layout.addWidget(local_btn)

        # 测试连接按钮（成功色）
        test_btn = QPushButton("测试连接")
        test_btn.setStyleSheet("""
            QPushButton {
                background-color: #34a853;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 28px;
                font-size: 14px;
                font-weight: 600;
                min-width: 120px;
                min-height: 45px;
                box-shadow: 0 2px 5px rgba(52, 168, 83, 0.3);
            }
            QPushButton:hover {
                background-color: #2d8f46;
                box-shadow: 0 3px 8px rgba(52, 168, 83, 0.4);
            }
            QPushButton:pressed {
                background-color: #237d36;
                box-shadow: 0 1px 3px rgba(52, 168, 83, 0.3);
            }
        """)
        test_btn.clicked.connect(self.test_connection)
        btn_layout.addWidget(test_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        return card

    def create_sql_edit_card(self):
        """SQL编辑卡片（自适应）"""
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
        sub_title = QLabel("SQL 编辑区")
        sub_title.setFont(QFont("Microsoft YaHei", 16, QFont.Bold))
        sub_title.setStyleSheet("color: #34495e;")
        header.addWidget(sub_title)

        self.sql_template_combo = QComboBox()
        self.sql_template_combo.addItems([
            "选择SQL模板",
            "SELECT * FROM table LIMIT 10;",
            "INSERT INTO table (col1, col2) VALUES ('val1', 'val2');",
            "UPDATE table SET col1='val1' WHERE id=1;",
            "DELETE FROM table WHERE id=1;"
        ])
        self.sql_template_combo.setStyleSheet(self.combo_style())
        self.sql_template_combo.setMaximumWidth(250)
        self.sql_template_combo.currentTextChanged.connect(self.load_sql_template)
        header.addWidget(self.sql_template_combo)
        header.addStretch()
        layout.addLayout(header)

        # SQL编辑框（滚动+自适应）
        self.sql_edit = QTextEdit()
        self.sql_edit.setPlaceholderText("请输入SQL语句...")
        self.sql_edit.setStyleSheet("""
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
        self.sql_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.sql_edit, 1)

        # 执行按钮
        exec_btn = QPushButton("执行SQL")
        exec_btn.setStyleSheet(self.primary_btn_style())
        exec_btn.clicked.connect(self.execute_sql)
        layout.addWidget(exec_btn)

        return card

    def create_sql_history_card(self):
        """SQL历史记录卡片（修复QListWidget导入）"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 12px;
                border: 1px solid #e8e8e8;
                padding: 15px;
                font-size: 14px;
            }
        """)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        layout = QVBoxLayout(card)
        layout.setSpacing(10)

        # 子标题
        header_layout = QHBoxLayout()
        sub_title = QLabel("SQL 历史记录")
        sub_title.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        sub_title.setStyleSheet("color: #34495e;")
        header_layout.addWidget(sub_title)

        # 清空按钮
        clear_btn = QPushButton("清空历史")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #f1f3f4;
                color: #202124;
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 12px;
                min-height: 30px;
            }
        """)
        clear_btn.clicked.connect(self.clear_sql_history)
        header_layout.addWidget(clear_btn)

        header_layout.addStretch()
        layout.addLayout(header_layout)

        # 历史记录列表（QListWidget已导入）
        self.sql_history_list = QListWidget()
        self.sql_history_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 8px;
                font-size: 13px;
                background-color: #fafafa;
                min-height: 150px;
            }
            QListWidget::item {
                padding: 6px;
                border-bottom: 1px solid #f0f0f0;
            }
            QListWidget::item:selected {
                background-color: #4285f4;
                color: white;
            }
        """)
        self.sql_history_list.itemClicked.connect(self.select_sql_history)
        layout.addWidget(self.sql_history_list, 1)

        # 加载历史记录
        self.load_sql_history()

        return card

    def create_result_card(self):
        """结果展示卡片（自适应）"""
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

        clear_btn = QPushButton("清空结果")
        clear_btn.setStyleSheet(self.secondary_btn_style())
        clear_btn.clicked.connect(lambda: self.result_browser.clear())
        header.addWidget(clear_btn)

        copy_btn = QPushButton("复制结果")
        copy_btn.setStyleSheet(self.secondary_btn_style())
        copy_btn.clicked.connect(self.copy_result)
        header.addWidget(copy_btn)

        header.addStretch()
        layout.addLayout(header)

        # 结果展示框（滚动+自适应）
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
    def connect_local_mysql(self):
        """一键连接本地MySQL（默认root/root）"""
        self.host_edit.setText("localhost")
        self.port_edit.setText("3306")
        self.user_edit.setText("root")
        self.pwd_edit.setText("root")
        show_info("提示", "已填充本地MySQL连接信息（默认密码root）！")

    def load_sql_template(self, text):
        if text != "选择SQL模板":
            self.sql_edit.setText(text)
            logger.info(f"加载SQL模板：{text}")

    def load_sql_history(self):
        """加载SQL历史记录"""
        self.sql_history_list.clear()
        history_commands = config_manager.get_sql_history()
        for cmd in reversed(history_commands):  # 最新的在上面
            self.sql_history_list.addItem(cmd)

    def select_sql_history(self, item):
        """选择历史SQL"""
        self.sql_edit.setText(item.text())

    def clear_sql_history(self):
        """清空SQL历史记录"""
        config_manager.clear_sql_history()
        self.load_sql_history()
        show_info("成功", "SQL历史记录已清空！")

    def test_connection(self):
        host = self.host_edit.text().strip()
        port = self.port_edit.text().strip()
        user = self.user_edit.text().strip()
        pwd = self.pwd_edit.text().strip()
        dbname = self.dbname_edit.text().strip()

        if not host or not port or not user:
            show_warn("警告", "主机/端口/用户名不能为空！")
            return

        try:
            conn = pymysql.connect(
                host=host,
                port=int(port),
                user=user,
                password=pwd,
                database=dbname if dbname else None,
                connect_timeout=5
            )
            conn.close()
            show_info("成功", "数据库连接成功！")
            config_manager.increment_stat("db_connections")
            logger.info(f"数据库连接成功：{host}:{port}")
        except Exception as e:
            show_error("失败", f"数据库连接失败：{str(e)}")
            logger.error(f"数据库连接失败：{str(e)}")

    def execute_sql(self):
        host = self.host_edit.text().strip()
        port = self.port_edit.text().strip()
        user = self.user_edit.text().strip()
        pwd = self.pwd_edit.text().strip()
        dbname = self.dbname_edit.text().strip()
        sql = self.sql_edit.toPlainText().strip()

        if not host or not port or not user or not dbname:
            show_warn("警告", "连接信息和数据库名不能为空！")
            return
        if not sql:
            show_warn("警告", "SQL语句不能为空！")
            return

        # 保存到历史记录
        config_manager.add_sql_history(sql)
        self.load_sql_history()

        # 显示加载状态
        self.result_browser.setText("正在执行SQL...")
        self.sql_thread = SQLThread(host, port, user, pwd, dbname, sql)
        self.sql_thread.result_signal.connect(self.show_sql_result)
        self.sql_thread.finished_signal.connect(lambda: logger.info("SQL执行完成"))
        self.sql_thread.start()

    def show_sql_result(self, success, result):
        if success:
            self.result_browser.setText(result)
            show_info("成功", "SQL执行成功")
        else:
            self.result_browser.setText(f"执行失败：{result}")
            show_error("失败", f"SQL执行失败：{result}")

    def copy_result(self):
        text = self.result_browser.toPlainText()
        if not text:
            show_warn("警告", "结果为空！")
            return
        from PyQt5.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        show_info("成功", "结果已复制到剪贴板")