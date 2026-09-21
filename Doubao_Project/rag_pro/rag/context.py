# -*- coding: utf-8 -*-
"""
上下文组装 context
===================

作用：把重排后的检索结果，组装成「送给大模型的上下文」，并控制长度与引用。

要解决的问题：
  1. 去重：同一段内容可能被多路检索同时召回，需要按文档去重；
  2. 长度：大模型有上下文上限，需要按 token 预算裁剪；
  3. 引用：给每段内容编号 [1][2]...，让答案可溯源；
  4. 可读：拼接成清晰的分段文本，标明来源。
"""

from .tokenizer import tokenize


def estimate_tokens(text: str) -> int:
    """
    粗略估算一段文本的 token 数（不调用外部 tokenizer）。

    方法：直接按分词结果长度估算（一个词条 ≈ 一个 token）。
    足够精确用于长度控制，无需引入复杂的 token 统计库。

    参数:
        text: 文本。

    返回:
        估算的 token 数。
    """
    # 按本项目的分词器统计词条数作为估算
    return len(tokenize(text))


def assemble_context(candidates: list, max_tokens: int = 1800,
                     top_n: int = 5):
    """
    把重排后的候选组装成上下文文本与最终选用列表。

    参数:
        candidates: 重排后的候选列表（已按分数降序）。
        max_tokens: 上下文的最大 token 预算。
        top_n:      最多使用前几条候选。

    返回:
        (context_str, used)
          context_str: 组装好的上下文文本。
          used:        实际使用的候选列表（含引用编号信息）。
    """
    # 用于去重的已见文档 id 集合
    seen_docs = set()
    # 实际选用的候选
    used = []
    # 累计已用 token 数
    total = 0

    # 遍历重排后的候选
    for c in candidates:
        # 达到预算或条数上限就停止
        if len(used) >= top_n or total >= max_tokens:
            break
        # 跳过与已选结果来自同一文档块的重复项
        key = (c.meta.get("path", ""), c.meta.get("chunk_idx", 0))
        if key in seen_docs:
            continue
        # 记录已见，避免重复
        seen_docs.add(key)
        # 估算本块 token 数
        tk = estimate_tokens(c.text)
        # 若加入后超预算则跳过（但要保证至少有一条）
        if total + tk > max_tokens and used:
            break
        # 加入候选并累计长度
        used.append(c)
        total += tk

    # 组装上下文文本：逐条编号并标注来源
    parts = []
    for i, c in enumerate(used, start=1):
        # 来源描述：优先用文件名，其次用路径
        src = c.meta.get("path", "未知来源")
        # 每条的格式：[编号] 来源：文件（块号）\n 内容
        parts.append(f"[{i}] 来源：{src}\n{c.text}")
    # 用空行连接各条
    context = "\n\n".join(parts)
    # 返回上下文与选用列表
    return context, used
