
# -*- coding: utf-8 -*-
import json
import os
from utils.paths import get_config_path

def read_json(filename, default=None):
    path = os.path.join(get_config_path(), filename)
    if not os.path.exists(path):
        return default if default is not None else {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return default if default is not None else {}

def write_json(filename, data):
    path = os.path.join(get_config_path(), filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)