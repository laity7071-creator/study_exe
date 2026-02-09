# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QMessageBox

def show_info(title, text):
    """显示信息弹窗"""
    QMessageBox.information(None, title, text)

def show_warn(title, text):
    """显示警告弹窗"""
    QMessageBox.warning(None, title, text)

def show_error(title, text):
    """显示错误弹窗"""
    QMessageBox.critical(None, title, text)