# -*- coding: utf-8 -*-
"""
查询处理 query
===============

作用：在检索之前，对用户的提问做「改写 / 扩展」，提升召回效果。

包含两种手段：
  1. 语料关联扩展（离线，必做）
     - 从 BM25 的倒排索引里，找出与查询词共现最多的相关词，追加到查询；
     - 让「提离职」也能命中「辞职」「离职流程」等文档说法。

  2. 大模型改写（可选）
     - 若配置了 LLM，可让模型把口语化提问改写为更规范、更适合检索的问法；
     - 不配置 LLM 时自动跳过，不影响主流程。
"""

from .tokenizer import tokenize


def expand_query(query: str, bm25, top_n: int = 4) -> str:
    """
    基于语料的查询扩展：找出与查询词相关的词并追加到查询末尾。

    原理：
      - 对查询的每个有效词条，调用 bm25.related_terms 找共现词；
      - 把所有扩展词按共现强度排序，取前 top_n 个；
      - 追加到查询末尾（用空格分隔），让检索覆盖更广的说法。

    参数:
        query: 原始查询。
        bm25:  已拟合的 BM25 索引（提供语料统计）。
        top_n: 追加的相关词数量。

    返回:
        扩展后的查询字符串。
    """
    # 对查询分词
    terms = tokenize(query)
    # 收集扩展词（去重）
    extra = []
    seen = set()
    # 遍历每个查询词条
    for t in terms:
        # 跳过单字，避免引入噪音（二字组/英文词更有意义）
        if len(t) == 1:
            continue
        # 获取该词的相关词
        for w in bm25.related_terms(t, n=top_n):
            # 只追加新词，且跳过无意义短词
            if w not in seen and len(w) > 1:
                extra.append(w)
                seen.add(w)
    # 没有有效扩展词时，返回原查询
    if not extra:
        return query
    # 扩展词与原始查询拼接（原始查询保留在最前，权重更高）
    return query + " " + " ".join(extra[:top_n])


def rewrite_query(query: str, llm, system: str = "") -> str:
    """
    用大模型改写查询（可选）。

    参数:
        query:  原始查询。
        llm:    LLM 客户端（无则返回原查询）。
        system: 可选的系统提示。

    返回:
        改写后的查询；无 LLM 或改写失败时返回原查询。
    """
    # 没有 LLM 时直接返回原查询
    if llm is None:
        return query
    # 组装系统提示：明确要求输出精简、适合检索的问法
    sys_msg = system or (
        "你是查询改写助手。请把用户的问题改写为更规范、更便于检索的"
        "问句，只输出改写结果，不要任何解释。"
    )
    # 调用 LLM 生成改写
    new_q = llm.chat([
        {"role": "system", "content": sys_msg},
        {"role": "user", "content": query},
    ], max_tokens=64)
    # 改写失败（None 或空）时回退原查询
    if not new_q or not new_q.strip():
        return query
    # 去掉可能的多余换行，返回单行
    return new_q.strip().replace("\n", " ")


def process_query(query: str, bm25, llm=None) -> str:
    """
    查询处理的统一入口：先大模型改写（可选），再做语料扩展。

    参数:
        query: 原始查询。
        bm25:  BM25 索引（供扩展用）。
        llm:   LLM 客户端（可选）。

    返回:
        最终用于检索的查询字符串。
    """
    # 第一步：可选的大模型改写（失败自动回退）
    q = rewrite_query(query, llm)
    # 第二步：基于语料的关联扩展（总是执行）
    q = expand_query(q, bm25)
    # 返回处理后的查询
    return q
