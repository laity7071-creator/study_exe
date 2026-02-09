
# -*- coding: utf-8 -*-
import sys
import os

def get_root_path():
    if hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    else:
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_config_path():
    return os.path.join(get_root_path(), "config")