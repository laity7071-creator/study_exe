# -*- coding: utf-8 -*-
import random

def generate_code(length=4):
    """生成4位数字验证码"""
    return "".join(str(random.randint(0, 9)) for _ in range(length))