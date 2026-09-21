# -*- coding: utf-8 -*-
"""
稠密向量库 vectorstore
=======================

作用：存储「块向量」并提供余弦相似度检索，是 RAG 混合检索的「向量」半边。

支持两种向量表示（透明、可切换）：
  - 稀疏字典 {词下标: 权重}：内置哈希向量（见 embedder.HashEmbedder）使用，
    存储紧凑、计算快；
  - 稠密列表 [浮点数...]：语义向量 API（见 embedder.ApiEmbedder）使用，
    维度通常 768~1536。

余弦相似度用最朴素的方式实现（点积 / 模长），不依赖 numpy 等任何库，
代码一眼可读、可修改。
"""

import json
import math

# 引入类型注解用的 Option（便于阅读，非必需）
from typing import Optional


def _norm(v) -> float:
    """
    计算向量的模长（L2 范数）。

    参数:
        v: 稀疏字典或稠密列表。

    返回:
        模长，用于余弦相似度分母。
    """
    # 稀疏字典表示：只对非零元素求和
    if isinstance(v, dict):
        return math.sqrt(sum(x * x for x in v.values()))
    # 稠密列表表示：对所有元素求和
    return math.sqrt(sum(x * x for x in v))


def _dot(a, b) -> float:
    """
    计算两个向量的点积（兼容稀疏/稠密任意组合）。

    参数:
        a, b: 向量，可为字典或列表。

    返回:
        点积结果。
    """
    # 两边都是稀疏字典：遍历较小的那个，取公共下标
    if isinstance(a, dict) and isinstance(b, dict):
        # 选元素少的遍历，减少计算量
        if len(a) > len(b):
            a, b = b, a
        # 只累加两边都存在的下标
        return sum(w * b[k] for k, w in a.items() if k in b)
    # 任意一边是稠密列表：转成「下标 -> 值」再统一按稀疏处理
    a = a if isinstance(a, dict) else {i: x for i, x in enumerate(a) if x}
    b = b if isinstance(b, dict) else {i: x for i, x in enumerate(b) if x}
    # 走稀疏相乘逻辑
    if len(a) > len(b):
        a, b = b, a
    return sum(w * b[k] for k, w in a.items() if k in b)


def cosine(a, b) -> float:
    """
    计算两个向量的余弦相似度，范围 [-1, 1]（通常为正）。

    参数:
        a, b: 向量（稀疏字典或稠密列表）。

    返回:
        余弦相似度；任一向量模长为 0 时返回 0。
    """
    # 先算两边模长
    na, nb = _norm(a), _norm(b)
    # 防除零：空向量相似度记为 0
    if na == 0 or nb == 0:
        return 0.0
    # 余弦 = 点积 / (模长乘积)
    return _dot(a, b) / (na * nb)


class VectorStore:
    """
    向量库：管理所有块向量与对应的元信息，支持检索与持久化。
    """

    def __init__(self):
        # 所有向量，顺序与 meta 一一对应（下标即向量 id）
        self.vectors = []
        # 每个向量的元信息（如所属文档、原文等）
        self.metas = []

    def __len__(self):
        # 返回向量数量，便于外部统计
        return len(self.vectors)

    def add(self, vector, meta: dict) -> int:
        """
        追加一个向量及其元信息。

        参数:
            vector: 稀疏字典或稠密列表。
            meta:   元信息字典（doc_id、原文等）。

        返回:
            新向量的 id（下标）。
        """
        # 记录向量
        self.vectors.append(vector)
        # 记录元信息
        self.metas.append(meta)
        # 返回新 id
        return len(self.vectors) - 1

    def search(self, qvec, top_k: int = 10) -> list:
        """
        检索与查询向量最相似的 top_k 个向量。

        参数:
            qvec: 查询向量（稀疏字典或稠密列表）。
            top_k: 返回条数。

        返回:
            列表，元素为 (cosine_score, vector_id)，按相似度降序。
        """
        # 逐个计算余弦相似度
        scored = []
        for i, v in enumerate(self.vectors):
            # 计算查询与第 i 个向量的相似度
            s = cosine(qvec, v)
            # 记录 (分数, id)
            scored.append((s, i))
        # 按分数降序排列
        scored.sort(key=lambda x: x[0], reverse=True)
        # 截取前 top_k 条
        return scored[:top_k]

    # ---------- 持久化 ----------

    def to_dict(self) -> dict:
        """
        序列化为 JSON 可用的字典。

        返回:
            {vectors, metas} 结构。
        """
        # 打包向量与元信息
        return {"vectors": self.vectors, "metas": self.metas}

    @classmethod
    def from_dict(cls, data: dict) -> "VectorStore":
        """
        从字典恢复（to_dict 的逆操作）。

        参数:
            data: to_dict 产出的字典。

        返回:
            恢复后的 VectorStore。
        """
        # 新建实例并回填
        vs = cls()
        vs.vectors = data["vectors"]
        vs.metas = data["metas"]
        return vs

    def save(self, path: str) -> None:
        """
        保存到 JSON 文件。

        参数:
            path: 输出路径。
        """
        # UTF-8 写入 JSON
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False)

    def load(self, path: str) -> None:
        """
        从 JSON 文件加载（覆盖当前内容）。

        参数:
            path: 输入路径。
        """
        # 读取并恢复
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        restored = self.from_dict(data)
        # 回填到当前实例
        self.__dict__.update(restored.__dict__)
