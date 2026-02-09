# -*- coding: utf-8 -*-
import json
import os
import datetime


class ConfigManager:
    def __init__(self):
        # 配置文件路径
        self.config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")
        # 统计数据路径
        self.stats_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "stats.json")
        # SSH历史命令路径
        self.ssh_history_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ssh_history.json")

        # 默认配置
        self.default_config = {
            "theme": "light",
            "font_size": 14,  # 默认字体调大到14px
            "brightness": 10,
            "sql_timeout": 30,
            "ssh_timeout": 10,
            "log_level": "INFO",
            "auto_start": False,
            "remember_login": False
        }

        # 默认统计数据
        self.default_stats = {
            "db_connections": 0,  # 数据库连接次数
            "db_select_count": 0,  # 数据库查询次数
            "db_insert_count": 0,  # 数据库插入次数
            "db_update_count": 0,  # 数据库更新次数
            "db_delete_count": 0,  # 数据库删除次数
            "ssh_connections": 0,  # SSH连接次数
            "ssh_command_count": 0,  # SSH命令执行次数
            "cmd_script_count": 0,  # CMD脚本保存数
            "ps1_script_count": 0,  # PS1脚本保存数
            "last_update": str(datetime.date.today())
        }

        # 默认SSH历史命令
        self.default_ssh_history = {
            "commands": [],
            "max_count": 50  # 最多保存50条
        }

        # 加载所有配置
        self.load_config()
        self.load_stats()
        self.load_ssh_history()
        # 默认SQL历史命令
        self.default_sql_history = {
            "commands": [],
            "max_count": 50  # 最多保存50条
        }

        # 加载所有配置
        self.load_config()
        self.load_stats()
        self.load_ssh_history()
        self.load_sql_history()  # 新增

    # ========== 基础配置 ==========
    def load_config(self):
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
            else:
                self.config = self.default_config
                self.save_config()
        except:
            self.config = self.default_config
            self.save_config()

    def save_config(self):
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.config, f, ensure_ascii=False, indent=4)

    def get(self, key, default=None):
        return self.config.get(key, default or self.default_config.get(key))

    def set(self, key, value):
        self.config[key] = value
        self.save_config()

    # ========== 统计数据 ==========
    def load_stats(self):
        try:
            if os.path.exists(self.stats_path):
                with open(self.stats_path, "r", encoding="utf-8") as f:
                    self.stats = json.load(f)
            else:
                self.stats = self.default_stats
                self.save_stats()
        except:
            self.stats = self.default_stats
            self.save_stats()

    def save_stats(self):
        self.stats["last_update"] = str(datetime.date.today())
        with open(self.stats_path, "w", encoding="utf-8") as f:
            json.dump(self.stats, f, ensure_ascii=False, indent=4)

    def increment_stat(self, key):
        """增加统计计数"""
        if key in self.stats:
            self.stats[key] += 1
            self.save_stats()

    def get_stat(self, key):
        return self.stats.get(key, 0)

    # ========== SSH历史命令 ==========
    def load_ssh_history(self):
        try:
            if os.path.exists(self.ssh_history_path):
                with open(self.ssh_history_path, "r", encoding="utf-8") as f:
                    self.ssh_history = json.load(f)
            else:
                self.ssh_history = self.default_ssh_history
                self.save_ssh_history()
        except:
            self.ssh_history = self.default_ssh_history
            self.save_ssh_history()

    def save_ssh_history(self):
        # 限制最大条数
        if len(self.ssh_history["commands"]) > self.ssh_history["max_count"]:
            self.ssh_history["commands"] = self.ssh_history["commands"][-self.ssh_history["max_count"]:]
        with open(self.ssh_history_path, "w", encoding="utf-8") as f:
            json.dump(self.ssh_history, f, ensure_ascii=False, indent=4)

    def add_ssh_history(self, command):
        """添加SSH历史命令"""
        if command and command not in self.ssh_history["commands"]:
            self.ssh_history["commands"].append(command)
            self.save_ssh_history()

    def get_ssh_history(self):
        return self.ssh_history["commands"]

    def clear_ssh_history(self):
        self.ssh_history["commands"] = []
        self.save_ssh_history()

    # ========== 新增SQL历史命令 ==========
    def load_sql_history(self):
        try:
            self.sql_history_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sql_history.json")
            if os.path.exists(self.sql_history_path):
                with open(self.sql_history_path, "r", encoding="utf-8") as f:
                    self.sql_history = json.load(f)
            else:
                self.sql_history = self.default_sql_history
                self.save_sql_history()
        except:
            self.sql_history = self.default_sql_history
            self.save_sql_history()

    def save_sql_history(self):
        # 限制最大条数
        if len(self.sql_history["commands"]) > self.sql_history["max_count"]:
            self.sql_history["commands"] = self.sql_history["commands"][-self.sql_history["max_count"]:]
        with open(self.sql_history_path, "w", encoding="utf-8") as f:
            json.dump(self.sql_history, f, ensure_ascii=False, indent=4)

    def add_sql_history(self, command):
        """添加SQL历史命令"""
        if command and command not in self.sql_history["commands"]:
            self.sql_history["commands"].append(command)
            self.save_sql_history()

    def get_sql_history(self):
        return self.sql_history["commands"]

    def clear_sql_history(self):
        self.sql_history["commands"] = []
        self.save_sql_history()


# 全局实例
config_manager = ConfigManager()