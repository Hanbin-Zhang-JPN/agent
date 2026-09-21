# -*- coding: utf-8 -*-
"""
文档切块器 chunker
==================

作用：把一篇长文档切成多个大小合适的「块（chunk）」。
为什么要切块：
  - 大模型上下文有长度限制，不能把整篇文档都塞进去；
  - 检索时以「块」为最小单元，命中更精确、引用更可追溯；
  - 块的大小与质量直接决定 RAG 的检索准确率。

切块策略（本实现）：
  1. 先按「空行 / 段落」切分，尊重文档的自然结构；
  2. 段落过长时再按「句号等句子边界」细分；
  3. 相邻块之间保留少量「重叠（overlap）」，避免关键句被切断在块边界。

全部用标准库实现，无任何外部依赖，逻辑完全透明。
"""

import re

# 句子边界正则：中文句号、感叹号、问号、英文句号等
_SENT_END = re.compile(r"(?<=[。！？!?；;])\s*")
# 段落边界正则：连续两个及以上换行（空行分段）
_PARA_SPLIT = re.compile(r"\n\s*\n")


def _split_sentences(text: str) -> list:
    """
    把一段文字按句子边界切成句子列表（保留标点）。

    参数:
        text: 待切分的段落文字。

    返回:
        句子列表。
    """
    # 用句子边界正则切分，并过滤掉空白句
    parts = _SENT_END.split(text)
    # 去掉首尾空白，丢弃完全为空的片段
    return [p.strip() for p in parts if p and p.strip()]


def _make_chunk(sentences: list, start: int, end: int) -> str:
    """
    把句子列表的 [start, end) 区间拼接成一个文本块。

    参数:
        sentences: 句子列表。
        start: 起始下标（含）。
        end: 结束下标（不含）。

    返回:
        拼接后的块文本。
    """
    # 用空串把该区间的句子拼起来，并清理多余空白
    return "".join(sentences[start:end]).strip()


def chunk_text(text: str, chunk_size: int = 400, overlap: int = 60) -> list:
    """
    把整篇文档切成若干文本块，返回块列表。

    参数:
        text:     整篇文档文本。
        chunk_size: 目标块大小（字符数，粗略控制）。
        overlap:  相邻块之间重叠的字符数。

    返回:
        文本块列表。
    """
    # 空文档直接返回空列表
    if not text or not text.strip():
        return []

    # 第一步：按空行切分成段落，保留自然结构
    paragraphs = [p.strip() for p in _PARA_SPLIT.split(text) if p.strip()]

    # 最终收集所有文本块
    chunks = []

    # 遍历每个段落，逐段处理
    for para in paragraphs:
        # 若段落很短（不超过块大小），直接整段作为一个块
        if len(para) <= chunk_size:
            chunks.append(para)
            continue

        # 段落较长：先切成句子，再按「句子窗口 + 重叠」组装块
        sents = _split_sentences(para)
        # 段落没有任何可切句子时，做硬切兜底，避免丢内容
        if not sents:
            # 直接按固定字符长度硬切
            for i in range(0, len(para), chunk_size):
                chunks.append(para[i:i + chunk_size])
            continue

        # 滑动窗口组块：start 指向当前块的第一句
        start = 0
        while start < len(sents):
            # 从 start 开始累加句子，直到达到目标块大小
            end = start
            cur_len = 0
            while end < len(sents) and cur_len < chunk_size:
                # 计入当前句子的长度（含句号，+1 是标点余量）
                cur_len += len(sents[end]) + 1
                end += 1

            # 取出当前块
            block = _make_chunk(sents, start, end)
            # 非空块才收集（避免全空白）
            if block:
                chunks.append(block)

            # 若已经到末尾，结束本段
            if end >= len(sents):
                break

            # 计算下一块起点：以「重叠」为对齐目标，回退若干句子
            # 简单做法：从 end 前移，使重叠长度接近 overlap
            back = 0
            used = 0
            while back < (end - start) and used < overlap:
                # 从后往前累计句子长度
                used += len(sents[end - 1 - back]) + 1
                back += 1
            # 下一块起点 = 当前块结束位置 - 回退句数（保证重叠）
            start = end - back

    # 返回所有块
    return chunks


def chunk_document(text: str, chunk_size: int = 400, overlap: int = 60) -> list:
    """
    文档级切块的对外统一入口（语义与 chunk_text 相同）。

    参数:
        text: 文档全文。
        chunk_size: 块大小。
        overlap: 重叠长度。

    返回:
        文本块列表。
    """
    # 直接委托给 chunk_text 完成
    return chunk_text(text, chunk_size, overlap)
