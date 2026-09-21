# ============================================================
# 索引：同时维护 BM25 倒排索引 + 稠密向量表
#
#   - 倒排索引：词元 → [(文档号, 词频)]，检索时只碰相关文档，速度很快
#   - 稠密向量：每篇文档一个向量，供余弦相似度检索，容错表记差异
#   - 持久化：支持保存 / 加载到磁盘（pickle），下次启动免重建
#
# 可选加速：若环境装了 numpy 就用矩阵乘法批量算余弦，
#           没装则用纯 Python 兜底，二者结果一致，只是速度不同
# ============================================================

import math
import os
import pickle

# numpy 是可选项：只在它存在时用于加速，绝不强制依赖
try:
    import numpy as np
    _HAS_NUMPY = True                              # 标记：可用 numpy 加速
except ImportError:
    _HAS_NUMPY = False                             # 没有就纯 Python 兜底

from .tokenize import tokenize                     # 分词
from .embed import embed_tokens, normalize, dot    # 向量化


class Index:
    """本地检索索引：支持批量入库、BM25/稠密检索、保存与加载"""

    def __init__(self, dim=2048, k1=1.5, b=0.75):
        self.dim = dim                             # 稠密向量维度
        self.k1 = k1                               # BM25 词频饱和参数
        self.b = b                                 # BM25 长度归一化参数
        self.docs = []                             # 文档列表：[{id,text,meta,tokens}]
        self.postings = {}                         # 倒排：词元 → [(文档号, 词频)]
        self.doc_freq = {}                         # 词元 → 出现该词的文档数
        self.doc_len = []                          # 每篇文档的词元数
        self.avgdl = 0.0                           # 全部文档的平均长度
        self.idf = {}                              # 词元 → 逆文档频率
        self.vectors = []                          # 每篇文档的稠密向量
        self._finalized = False                    # 是否已完成统计（idf/归一化）

    # ---------------- 建库 ----------------
    def add_documents(self, doc_list):
        """批量加入文档，doc_list 的元素为 {text, meta} 字典"""
        for doc in doc_list:
            toks = tokenize(doc["text"])           # 先做分词
            idx = len(self.docs)                   # 新文档的编号
            self.docs.append({                     # 存下原始信息
                "id": doc.get("id", idx),          # 有 id 用 id，否则用序号
                "text": doc["text"],               # 原文
                "meta": doc.get("meta", {}),       # 附加元信息（如来源文件）
                "tokens": toks,                    # 分词结果
            })
            tf = {}                                # 统计该文档内词频
            for t in toks:
                tf[t] = tf.get(t, 0) + 1
            seen = set()                           # 记录本文档已出现过的词
            for t, c in tf.items():
                self.postings.setdefault(t, []).append((idx, c))  # 挂到倒排链
                if t not in seen:                  # 每个词只计一次文档频率
                    seen.add(t)
                    self.doc_freq[t] = self.doc_freq.get(t, 0) + 1
            self.doc_len.append(len(toks))         # 记录文档长度
        self._finalized = False                    # 有新数据，需重新统计

    def finalize(self):
        """收尾统计：计算 IDF、平均长度，并生成全部归一化向量"""
        n = len(self.docs)                         # 文档总数
        if n == 0:                                 # 空库无需处理
            return
        self.avgdl = sum(self.doc_len) / n         # 平均文档长度
        # IDF 平滑公式：ln((N - df + 0.5) / (df + 0.5) + 1)
        for t, df in self.doc_freq.items():
            self.idf[t] = math.log((n - df + 0.5) / (df + 0.5) + 1)
        # 逐篇生成稠密向量并归一化
        self.vectors = [
            normalize(embed_tokens(d["tokens"], self.dim, self.idf))
            for d in self.docs
        ]
        self._finalized = True                     # 标记统计完成

    def ensure_finalized(self):
        """确保索引已完成统计后再进行检索"""
        if not self._finalized:
            self.finalize()

    # ---------------- 检索 ----------------
    def search_bm25(self, query_tokens, top_k=20):
        """BM25 检索：只遍历查询词所在的倒排链，避免全表扫描"""
        self.ensure_finalized()
        n = len(self.docs)                         # 文档总数
        scores = {}                                # 文档号 → 累加得分
        for t in set(query_tokens):                # 对查询词去重遍历
            if t not in self.postings:             # 库里没有这个词就跳过
                continue
            idf_t = self.idf.get(t, 0.0)           # 该词的 IDF
            for doc_idx, tf in self.postings[t]:   # 遍历这个词的倒排链
                dl = self.doc_len[doc_idx]         # 目标文档长度
                # BM25 核心公式：词频饱和 + 长度归一化
                denom = tf + self.k1 * (1 - self.b + self.b * dl / self.avgdl)
                scores[doc_idx] = scores.get(doc_idx, 0.0) \
                    + idf_t * tf * (self.k1 + 1) / denom
        # 按得分降序排序，取前 top_k 个
        ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)[:top_k]
        return ranked                              # 返回 [(文档号, 得分)]

    def search_dense(self, query_vec, top_k=20):
        """稠密向量检索：按余弦相似度取前 top_k"""
        self.ensure_finalized()
        if not self.vectors:                       # 空库直接返回空
            return []
        if _HAS_NUMPY:                             # numpy 加速路径
            mat = np.array(self.vectors, dtype=np.float32)   # 拼成矩阵
            q = np.array(query_vec, dtype=np.float32)        # 查询向量
            sims = mat.dot(q)                      # 一次矩阵乘法算全部相似度
            order = np.argsort(-sims)[:top_k]      # 取相似度最高的前 top_k
            return [(int(i), float(sims[i])) for i in order]
        # 纯 Python 兜底：逐篇点积再排序
        scored = [(i, dot(query_vec, v)) for i, v in enumerate(self.vectors)]
        scored.sort(key=lambda kv: kv[1], reverse=True)
        return scored[:top_k]

    # ---------------- 持久化 ----------------
    def save(self, path):
        """把整个索引保存到磁盘（pickle 格式）"""
        d = {                                      # 组装成普通字典再存
            "dim": self.dim, "k1": self.k1, "b": self.b,
            "docs": self.docs, "postings": self.postings,
            "doc_freq": self.doc_freq, "doc_len": self.doc_len,
            "avgdl": self.avgdl, "idf": self.idf,
            "vectors": [list(v) for v in self.vectors],
            "finalized": self._finalized,
        }
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "wb") as f:                # 二进制写入
            pickle.dump(d, f)                      # 序列化

    @staticmethod
    def load(path):
        """从磁盘载入索引"""
        with open(path, "rb") as f:
            d = pickle.load(f)                     # 反序列化
        idx = Index(d["dim"], d["k1"], d["b"])     # 用保存的参数重建
        idx.docs = d["docs"]                       # 恢复各字段
        idx.postings = d["postings"]
        idx.doc_freq = d["doc_freq"]
        idx.doc_len = d["doc_len"]
        idx.avgdl = d["avgdl"]
        idx.idf = d["idf"]
        idx.vectors = d["vectors"]
        idx._finalized = d.get("finalized", True)  # 兼容旧版本
        return idx
