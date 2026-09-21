# -*- coding: utf-8 -*-
"""
rag_pro —— 现代化、可落地的「白箱」RAG 核心源码包
=================================================

本包是 rag_pro 项目的核心：一条完整的检索增强生成（RAG）链路，
从「文档读取 → 切块 → 建索引 → 混合检索 → 重排 → 生成」全部在此实现。

设计原则：
  1. 全程使用 Python 标准库，不依赖任何黑盒第三方库；
  2. 唯一的外部调用是可选的「大模型 / 语义向量 API」（OpenAI 兼容接口），
     何时调用、如何调用、参数含义都在对应模块里写清楚；
  3. 每个算法都从零实现并逐行中文注释，便于学习与二次开发。

对外最常用的入口是 RagPipeline（见 pipeline.py），一句话即可完成检索问答。
"""

# 把最常用的类直接提升到包顶层，方便用户 import
from .pipeline import RagPipeline      # RAG 主流程类：构建索引 + 问答
from .retriever import Candidate       # 检索候选结果的数据结构
from .tokenizer import tokenize        # 分词函数（中文友好）

# 包版本号，方便日志与排查
__version__ = "1.0.0"

# 包元信息：写明本包是什么、给谁用
__all__ = [
    "RagPipeline",     # 主入口：构建 + 问答
    "Candidate",       # 检索候选对象
    "tokenize",        # 分词工具
]
