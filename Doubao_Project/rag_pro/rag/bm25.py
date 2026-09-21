# -*- coding: utf-8 -*-
"""
BM25 关键词检索器 bm25
=======================

作用：实现经典的信息检索算法 Okapi BM25，用于「关键词级」检索。
它是 RAG 混合检索的「词法」半边（另外半边是向量检索，见 vectorstore.py）。

为什么需要 BM25：
  - 向量检索擅长语义相近，但面对精确术语、专有名词、稀有词时容易失灵；
  - BM25 对精确词匹配非常稳健、计算快、可解释；
  - 与向量检索融合后（见 retriever.py），整体准确率显著提升。

算法要点（从零实现，完全透明）：
  - 倒排索引：词条 -> 出现该词的文档集合；
  - TF（词频）+ IDF（逆文档频率）+ 长度归一化，三者的加权组合打分。
"""

import math
import json

# BM25 的经典超参数（业界常用默认值）
K1 = 1.5   # 词频饱和参数：越大，词频带来的分数增长越缓和
B = 0.75   # 长度归一化参数：越大，对长文档惩罚越明显


class BM25:
    """
    Okapi BM25 检索器。

    用法：
        bm = BM25()
        bm.fit(doc_list)            # 用文档列表建立索引
        hits = bm.search(query)     # 检索，返回 [(doc_id, score)]
    """

    def __init__(self):
        # 倒排索引：词条 -> {文档id: 该文档中该词出现次数}
        self.postings = {}
        # 每个文档的原始文本（按文档id保存，便于回取内容）
        self.docs = []
        # 每个文档的单词条数（用于长度归一化）
        self.doc_lens = []
        # 文档总数
        self.num_docs = 0
        # 所有文档的平均词条数
        self.avgdl = 0.0
        # 是否已完成拟合的标志
        self.fitted = False

    # ---------- 构建索引 ----------

    def fit(self, docs: list) -> None:
        """
        用一组文档建立 BM25 索引。

        参数:
            docs: 文档文本列表，每个元素是一篇文档的字符串。
        """
        # 保存原始文档
        self.docs = list(docs)
        # 记录文档总数
        self.num_docs = len(self.docs)
        # 清空倒排索引与长度表
        self.postings = {}
        self.doc_lens = []

        # 遍历每篇文档，统计词频并建立倒排
        for doc_id, text in enumerate(self.docs):
            # 对本篇文档分词
            toks = self._tokenize_doc(text)
            # 记录该文档的词条总数（长度）
            self.doc_lens.append(len(toks))
            # 统计本篇文档的词频
            freq = {}
            for t in toks:
                freq[t] = freq.get(t, 0) + 1
            # 把词频写入倒排索引
            for term, cnt in freq.items():
                # 若该词第一次出现，初始化一个空字典
                if term not in self.postings:
                    self.postings[term] = {}
                # 记录 (文档id -> 词频)
                self.postings[term][doc_id] = cnt

        # 计算平均文档长度
        self.avgdl = sum(self.doc_lens) / self.num_docs if self.num_docs else 0.0
        # 标记已完成拟合
        self.fitted = True

    def _tokenize_doc(self, text: str) -> list:
        """
        对文档做分词（内部使用 tokenizer）。

        参数:
            text: 文档文本。

        返回:
            词条列表。
        """
        # 延迟导入避免循环依赖；tokenizer 是纯标准库实现
        from .tokenizer import tokenize
        return tokenize(text)

    # ---------- 检索打分 ----------

    def idf(self, term: str) -> float:
        """
        计算某个词条的逆文档频率 IDF。

        IDF 越大，说明该词越稀有、区分度越高。

        参数:
            term: 词条。

        返回:
            IDF 值（平滑处理过，恒为正）。
        """
        # 包含该词的文档数
        df = len(self.postings.get(term, {}))
        # 平滑 IDF：ln(1 + (N - df + 0.5) / (df + 0.5))，保证不会为负
        return math.log(1 + (self.num_docs - df + 0.5) / (df + 0.5))

    def score(self, query_tokens: list, doc_id: int) -> float:
        """
        计算查询与某篇文档的 BM25 分数。

        参数:
            query_tokens: 查询的词条列表。
            doc_id: 目标文档 id。

        返回:
            BM25 分数（越高越相关）。
        """
        # 预取该文档的长度与平均长度，用于长度归一化
        dl = self.doc_lens[doc_id]
        # 长度归一化因子：控制长文档不至于因为词多而天然占优
        norm = 1 - B + B * (dl / self.avgdl) if self.avgdl else 1.0

        # 累计查询中每个词条对该文档的贡献
        total = 0.0
        # 去重查询词条，避免重复累加
        for term in set(query_tokens):
            # 该文档中该词的出现次数
            tf = self.postings.get(term, {}).get(doc_id, 0)
            # 文档中没出现这个词就跳过
            if tf == 0:
                continue
            # 词频饱和：tf 越大，边际收益越小
            tf_part = tf * (K1 + 1) / (tf + K1 * norm)
            # 累加：IDF * 词频项
            total += self.idf(term) * tf_part
        return total

    def search(self, query: str, top_k: int = 10) -> list:
        """
        检索与查询最相关的 top_k 篇文档。

        参数:
            query: 查询字符串。
            top_k: 返回结果条数。

        返回:
            列表，元素为 (doc_id, score)，按分数从高到低排序。
        """
        # 未拟合时无法检索，直接返回空
        if not self.fitted:
            return []
        # 对查询分词
        q_tokens = self._tokenize_doc(query)
        # 查询没有有效词条时返回空
        if not q_tokens:
            return []

        # 计算每篇文档的分数
        scored = []
        for doc_id in range(self.num_docs):
            # 只对与查询有共现词的文档打分（小优化）
            s = self.score(q_tokens, doc_id)
            if s > 0:
                scored.append((doc_id, s))
        # 按分数降序排列
        scored.sort(key=lambda x: x[1], reverse=True)
        # 截取前 top_k 条返回
        return scored[:top_k]

    # ---------- 查询扩展辅助 ----------

    def related_terms(self, term: str, n: int = 5) -> list:
        """
        返回与某个词条「共现关系最密切」的词条，用于查询扩展。

        原理：与该词出现在同一篇文档越多的词，越可能是相关词。
        这是基于语料的简单关联扩展，不需要外部知识库。

        参数:
            term: 原始词条。
            n: 返回的相关词条数量。

        返回:
            相关词条列表（不含原词本身）。
        """
        # 该词没有出现在任何文档时，无法扩展
        if term not in self.postings:
            return []
        # 取出包含该词的所有文档 id 集合
        term_docs = set(self.postings[term].keys())
        # 统计其它词与它的共现次数
        co = {}
        for doc_id in term_docs:
            # 遍历该文档中出现的所有词
            for other, _ in self.postings.items():
                # 排除自己
                if other == term:
                    continue
                # 若该词也出现在同一文档，累计共现
                if doc_id in self.postings[other]:
                    co[other] = co.get(other, 0) + 1
        # 按共现次数降序，取前 n 个
        top = sorted(co.items(), key=lambda x: x[1], reverse=True)[:n]
        # 只返回词条本身
        return [w for w, _ in top]

    # ---------- 持久化 ----------

    def to_dict(self) -> dict:
        """
        把索引序列化为可 JSON 的字典，便于存盘。

        返回:
            描述索引的字典。
        """
        # 把倒排索引、文档、长度等信息打包
        return {
            "postings": self.postings,      # 倒排索引
            "docs": self.docs,              # 原始文档
            "doc_lens": self.doc_lens,      # 文档长度
            "avgdl": self.avgdl,            # 平均长度
            "num_docs": self.num_docs,      # 文档数
        }

    @classmethod
    def from_dict(cls, data: dict) -> "BM25":
        """
        从字典恢复索引（to_dict 的逆操作）。

        参数:
            data: to_dict 产出的字典。

        返回:
            恢复后的 BM25 实例。
        """
        # 新建空实例
        bm = cls()
        # 倒排索引的文档 id 键需要转回整数（JSON 会把 int 键变成字符串，
        # 若不做转换，重载后 score() 用 int 查询将全部失配）
        postings = {}
        for term, df in data["postings"].items():
            # 把该词条下每个「文档id -> 词频」的键转回 int
            postings[term] = {int(doc_id): cnt for doc_id, cnt in df.items()}
        # 回填转换后的倒排索引
        bm.postings = postings
        # 回填其余字段（这些不受 JSON 键类型影响）
        bm.docs = data["docs"]
        bm.doc_lens = data["doc_lens"]
        bm.avgdl = data["avgdl"]
        bm.num_docs = data["num_docs"]
        # 标记为已拟合
        bm.fitted = True
        return bm

    def save(self, path: str) -> None:
        """
        把索引保存到 JSON 文件。

        参数:
            path: 输出文件路径。
        """
        # 以 UTF-8 写入序列化后的 JSON
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False)

    def load(self, path: str) -> None:
        """
        从 JSON 文件加载索引（覆盖当前内容）。

        参数:
            path: 索引文件路径。
        """
        # 读取 JSON 并恢复
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        restored = self.from_dict(data)
        # 把恢复结果拷回当前实例
        self.__dict__.update(restored.__dict__)
