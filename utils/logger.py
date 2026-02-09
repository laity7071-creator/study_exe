# -*- coding: utf-8 -*-
import os
import sys
import logging
from datetime import datetime

def get_exe_dir():
    """获取exe所在目录（打包后也能正确获取）"""
    if getattr(sys, 'frozen', False):
        # 打包成exe后
        return os.path.dirname(sys.executable)
    else:
        # 开发环境
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def init_logger():
    """初始化日志系统，写入到exe目录下的log文件夹"""
    # 日志目录
    log_dir = os.path.join(get_exe_dir(), "log")
    os.makedirs(log_dir, exist_ok=True)

    # 日志文件名：按日期生成
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join(log_dir, f"app_{today}.log")

    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(sys.stdout)
        ]
    )

    # 全局异常捕获，写入日志
    def excepthook(exc_type, exc_value, exc_tb):
        import traceback
        tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        logging.critical(f"程序崩溃：\n{tb}")
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.critical(None, "程序崩溃", f"错误已记录到日志文件：\n{log_file}")
        sys.exit(1)

    sys.excepthook = excepthook

    logging.info("=" * 50)
    logging.info("程序启动，日志系统初始化完成")
    logging.info(f"日志文件路径：{log_file}")
    return logging

# 全局日志实例
logger = init_logger()