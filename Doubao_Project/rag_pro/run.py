# -*- coding: utf-8 -*-
"""
统一入口 run.py
================

作用：项目根目录的一键入口，把命令行能力转发给 rag.cli。

用法：
  python run.py build --dir data/sample      # 构建索引
  python run.py ask --q "什么是RAG"          # 单次问答
  python run.py chat                         # 交互式问答
  python run.py eval --qa data/sample/qa.json # 检索评测
  python run.py serve --port 8765            # 启动 HTTP 服务
  python run.py info                         # 查看索引信息

说明：
  - 本文件不包含任何业务逻辑，只是入口转发；
  - 核心代码全部在 rag/ 目录下，请以 rag/ 为主要阅读对象。
"""

import os
import sys

# 把项目根目录加入模块搜索路径，保证 `python run.py ...` 可用
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入命令行入口并执行
from rag.cli import main   # noqa: E402

# 程序入口
if __name__ == "__main__":
    main()
