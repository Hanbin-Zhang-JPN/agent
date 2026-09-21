# -*- coding: utf-8 -*-
"""
分词器 tokenizer
================

作用：把一段原始文字切成「词条（token）」列表。
这些词条会同时用于两处：
  1. BM25 关键词检索（见 bm25.py）；
  2. 内置哈希向量化（见 embedder.py）。

为什么自己写而不是用 jieba 等库：
  - jieba 属于外部黑盒依赖，维护复杂、行为不透明；
  - RAG 检索并不需要真正意义上的「语义分词」，用简单规则即可获得很好的效果；
  - 本项目采用「中文单字 + 二字组 + 英文整词」的混合策略：
      · 中文：同时产出单字和相邻二字组，能天然匹配新词、表意组合；
      · 英文/数字：按空白与非字母数字切分并转小写，天然免疫大小写差异。
"""

import re

# 预编译常用正则，避免每次调用都重新编译（性能优化）
_CJK = re.compile(r"[\u4e00-\u9fff]")            # 匹配单个中文字符（基本区）
_WORD = re.compile(r"[a-zA-Z0-9]+")              # 匹配一段连续的英文/数字


def tokenize(text: str) -> list:
    """
    把一段文字切分为词条列表。

    参数:
        text: 原始文本，可为任意字符串。

    返回:
        词条列表，例如 "RAG检索真好用" -> ["rag", "检索", "索引", ...]
    """
    # 空文本直接返回空列表，避免无谓计算
    if not text:
        return []

    # 结果收集器：先存到一个列表，最后一次性返回
    tokens = []

    # 先用正则按「中文 / 非中文」把整段文字切块，逐块处理
    # 正则：中文字符作为一个独立块，其余字符（含英文、标点）作为另一类块
    for block in re.split(r"([\u4e00-\u9fff])", text):
        # 该块是单个中文字符（注意 split 捕获组会保留中文）
        if _CJK.fullmatch(block):
            # 单字本身作为一个词条（对短查询很关键）
            tokens.append(block)
        # 该块是纯英文/数字段（如 "RAG"、"2024"、"abc_def"）
        elif _WORD.fullmatch(block):
            # 统一转小写，让 "RAG" 与 "rag" 相互命中
            tokens.append(block.lower())
        # 该块是混合字符或标点，进一步按单词正则切分
        else:
            # 用单词正则捞出其中的英文/数字片段
            for w in _WORD.findall(block):
                # 同样转小写后加入词条
                tokens.append(w.lower())

    # 二次扫描：为相邻的中文单字生成「二字组」，提升中文匹配质量
    bigrams = []
    for i in range(len(tokens) - 1):
        # 仅当前后两个词条都是单个中文字符时才组二字组
        if _CJK.fullmatch(tokens[i]) and _CJK.fullmatch(tokens[i + 1]):
            bigrams.append(tokens[i] + tokens[i + 1])

    # 单字 + 二字组 一起返回（二字组追加在末尾）
    return tokens + bigrams


def unique_tokens(text: str) -> set:
    """
    返回去重后的词条集合，常用于快速判重或统计词频。

    参数:
        text: 原始文本。

    返回:
        去重后的词条集合。
    """
    # 用 set 对分词结果去重后返回
    return set(tokenize(text))
