# -*- coding: utf-8 -*-
"""
混合检索器 retriever
=====================

作用：把 BM25 关键词检索与向量检索的结果融合在一起，产出最终候选列表。

为什么做「混合」：
  - 只用 BM25：精确但不懂语义；
  - 只用向量：懂语义但对精确术语、低频词不敏感；
  - 两者互补，融合后对各类查询都更稳。

融合算法：RRF（Reciprocal Rank Fusion，倒数排名融合）。
  - 对每个结果，根据它在两份榜单中的名次计算融合分：
      融合分 += 1 / (名次 + 常数)
  - 常数一般取 60，作用是让榜首与次席的差距不至于过大。
  - RRF 只需名次、不需要原始分数，天然可比，实现简单且效果稳定。
"""

from dataclasses import dataclass, field


@dataclass
class Candidate:
    """
    一条检索候选结果。

    字段:
        doc_id:   对应文档在索引中的 id。
        text:     命中的文本块原文。
        meta:     元信息（来源路径、序号等）。
        bm25:     BM25 原始分数（重排会用到）。
        vec:      向量相似度（重排会用到）。
        score:    融合后的最终分数（越高越相关）。
    """
    doc_id: int                # 文档 id
    text: str                  # 块原文
    meta: dict = field(default_factory=dict)   # 元信息
    bm25: float = 0.0          # BM25 分数
    vec: float = 0.0           # 向量相似度
    score: float = 0.0         # 融合分


class Retriever:
    """
    混合检索器：BM25 + 向量 双路召回，RRF 融合。
    """

    def __init__(self, bm25, vectorstore, top_lex: int = 20,
                 top_vec: int = 20, rrf_k: int = 60):
        """
        参数:
            bm25:        已拟合的 BM25 索引。
            vectorstore: 已填充的向量库。
            top_lex:     从 BM25 召回多少条（粗召回数）。
            top_vec:     从向量召回多少条（粗召回数）。
            rrf_k:       RRF 融合常数。
        """
        # 保存两个检索器
        self.bm25 = bm25
        self.vs = vectorstore
        # 记录召回数量配置
        self.top_lex = top_lex
        self.top_vec = top_vec
        # RRF 常数
        self.rrf_k = rrf_k

    def retrieve(self, query: str, query_vec=None) -> list:
        """
        执行混合检索，返回融合排序后的候选列表。

        参数:
            query:     查询文本。
            query_vec: 查询向量（可选；不传则跳过向量路）。

        返回:
            Candidate 列表，按融合分降序。
        """
        # ---------- 第一路：BM25 关键词检索 ----------
        # 记录每个 doc_id 的 BM25 分数
        lex_scores = {}
        # 执行 BM25 检索，返回 [(doc_id, score)]
        for doc_id, s in self.bm25.search(query, top_k=self.top_lex):
            # 保存该文档的 BM25 分数
            lex_scores[doc_id] = s

        # ---------- 第二路：向量检索 ----------
        # 记录每个 doc_id 的向量相似度
        vec_scores = {}
        # 若提供了查询向量，执行向量检索
        if query_vec is not None:
            # 返回 [(cosine, vector_id)]，vector_id 即 doc_id
            for s, vid in self.vs.search(query_vec, top_k=self.top_vec):
                # 保存向量相似度
                vec_scores[vid] = s

        # ---------- 用 RRF 融合两路结果 ----------
        # 收集所有被任一查询召回的文档 id（并集）
        all_ids = set(lex_scores) | set(vec_scores)
        # 构建候选：统计每一路中的名次并累计 RRF 分
        fused = {}
        for doc_id in all_ids:
            # 初始化融合分
            rrf = 0.0
            # 若该文档在 BM25 榜单中，按其名次累加
            if doc_id in lex_scores:
                # 名次 = 按分数降序排序后的位置（从 1 开始）
                rank_lex = self._rank_of(lex_scores, doc_id)
                rrf += 1.0 / (self.rrf_k + rank_lex)
            # 若该文档在向量榜单中，按其名次累加
            if doc_id in vec_scores:
                rank_vec = self._rank_of(vec_scores, doc_id)
                rrf += 1.0 / (self.rrf_k + rank_vec)
            # 组装候选对象（暂存原始分数供重排使用）
            fused[doc_id] = Candidate(
                doc_id=doc_id,                  # 文档 id
                text=self.bm25.docs[doc_id],    # 块原文
                meta=self.vs.metas[doc_id],     # 元信息
                bm25=lex_scores.get(doc_id, 0.0),   # BM25 原始分
                vec=vec_scores.get(doc_id, 0.0),    # 向量原始分
                score=rrf,                          # 融合分
            )

        # 按融合分降序排列后返回
        ordered = sorted(fused.values(), key=lambda c: c.score, reverse=True)
        return ordered

    @staticmethod
    def _rank_of(scores: dict, target: int) -> int:
        """
        计算某个 doc_id 在分数字典中的名次（1 表示最高分）。

        参数:
            scores:  {doc_id: 分数} 字典。
            target:  目标 doc_id。

        返回:
            名次（从 1 开始）。
        """
        # 按分数降序排序所有 doc_id
        ordered = sorted(scores, key=lambda k: scores[k], reverse=True)
        # 找到目标位置并 +1（下标从 0 开始）
        return ordered.index(target) + 1
