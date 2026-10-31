# -*- coding: utf-8 -*-
"""项目根入口：在项目根目录执行 `python run.py` 启动。

演示模式（无需脑电设备）：`python run.py --demo`，系统会自动随机决定每个选项结果。
"""
import sys
from app.main import main

if __name__ == '__main__':
    main(demo='--demo' in sys.argv)
