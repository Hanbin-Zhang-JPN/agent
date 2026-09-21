# -*- coding: utf-8 -*-
"""
检索评测 eval
==============

作用：用一组「问题 + 标准答案来源」评测检索质量，给出量化指标。

为什么需要评测：
  - 「能不能实际解决问题」不能靠感觉，需要用指标说话；
  - 改动算法（切块大小、权重、是否用向量）后，跑一遍评测即可对比优劣。

评测指标（均为信息检索标准指标，纯标准库实现）：
  - Recall@k   ：前 k 条结果中命中标准来源的比例；
  - HitRate@k  ：top-1 命中率（前 k 条中有任意一条命中即为命中）;
  - MRR@k      ：第一个命中的倒排名次（第一名记 1 分、第二名记 1/2…）。

数据格式：一个 JSON 文件，形如
  [{"question": "...", "source": "文件名", "answer": "..."}, ...]
  source 用于判断检索是否命中。
"""

import json

# 引入类型提示
from typing import Optional


def _recall_at_k(hits: list, gold: str) -> float:
    """
    计算单条问题的 Recall@k。

    参数:
        hits: 检索返回的候选列表（每个含 meta）。
        gold: 标准来源文件名。

    返回:
        0 或 1（前 k 条中是否包含标准来源）。
    """
    # 遍历前 k 条结果，判断是否有命中的来源
    for c in hits:
        # 候选的来源文件名
        src = c.meta.get("path", "")
        # 命中判断：标准来源文件名是候选路径的一部分即可
        if gold and gold in src:
            return 1.0
    # 未命中返回 0
    return 0.0


def _mrr_at_k(hits: list, gold: str) -> float:
    """
    计算单条问题的 MRR@k。

    参数:
        hits: 检索返回的候选列表。
        gold: 标准来源文件名。

    返回:
        倒排名次的倒数；未命中返回 0。
    """
    # 遍历前 k 条结果
    for i, c in enumerate(hits, start=1):
        # 来源文件名
        src = c.meta.get("path", "")
        # 命中的位置即名次 i，取倒数
        if gold and gold in src:
            return 1.0 / i
    # 未命中返回 0
    return 0.0


def run_eval(pipeline, qa_path: str, top_k: int = 5) -> dict:
    """
    对一组「问题-来源」跑检索评测。

    参数:
        pipeline: 已构建/加载好索引的 RagPipeline。
        qa_path:  评测数据 JSON 文件路径。
        top_k:    检索返回条数（k）。

    返回:
        汇总字典，含各指标均值与逐条明细。
    """
    # 读取评测数据
    with open(qa_path, "r", encoding="utf-8") as f:
        qa = json.load(f)

    # 累计各指标
    recall_sum = 0.0   # Recall@k 累计
    mrr_sum = 0.0      # MRR@k 累计
    hit_sum = 0.0      # HitRate@k 累计
    details = []       # 逐条明细

    # 遍历每条评测样例
    for item in qa:
        # 取问题与标准来源
        q = item["question"]
        gold = item.get("source", "")
        # 执行检索（直接用原始查询，不做生成）
        # 检索路径：处理查询 -> 混合检索 -> 重排
        from .query import process_query
        final_q = process_query(q, pipeline.bm25, pipeline.llm)
        # 计算查询向量
        qvec = None
        if pipeline.embedder is not None:
            try:
                qvec = pipeline.embedder.embed([final_q])[0]
            except Exception:
                qvec = None
        # 混合检索
        cands = pipeline.retriever.retrieve(final_q, query_vec=qvec)
        # 重排取前 top_k
        ranked = pipeline.reranker.rerank(final_q, cands, top_n=top_k)

        # 计算本条的三项指标
        r = _recall_at_k(ranked, gold)   # Recall@k
        m = _mrr_at_k(ranked, gold)      # MRR@k
        h = r                            # HitRate@k 与 Recall 相同（0/1）
        # 累加
        recall_sum += r
        mrr_sum += m
        hit_sum += h
        # 记录明细
        details.append({"question": q, "recall": r, "mrr": m,
                        "hit": h, "gold": gold})

    # 计算样本数
    n = len(qa)
    # 汇总结果（样本为空时指标记 0）
    return {
        "samples": n,                                  # 评测样本数
        "recall@k": round(recall_sum / n, 4) if n else 0.0,   # Recall@k 均值
        "mrr@k": round(mrr_sum / n, 4) if n else 0.0,         # MRR@k 均值
        "hit@k": round(hit_sum / n, 4) if n else 0.0,         # Hit@k 均值
        "top_k": top_k,                                # k 值
        "details": details,                            # 逐条明细
    }
