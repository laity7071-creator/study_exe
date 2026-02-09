
# -*- coding: utf-8 -*-
from utils.json_util import read_json, write_json
import os

class AppConfig:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.load()
        return cls._instance

    def load(self):
        self.data = read_json("app_config.json", default=self.default_config())

    def save(self):
        write_json("app_config.json", self.data)

    def default_config(self):
        return {
            "admin": {"username": "admin", "password": "admin123"},
            "user_info": {"name": "", "age": "", "phone": "", "email": ""},
            "db_saved": [],
            "settings": {"bg_image": "", "brightness": 1.0, "splash_image": ""}
        }

config = AppConfig()