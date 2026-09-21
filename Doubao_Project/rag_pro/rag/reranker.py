# -*- coding: utf-8 -*-
"""
重排器 reranker
================

作用：在「粗召回」得到的候选列表之上，做一轮精细排序，得到更准的 top-N。

为什么需要重排：
  - 混合检索的 RRF 只用了名次，比较「粗糙」；
  - 重排综合多种信号（关键词命中、向量相似、位置先验、精确词覆盖），
    让真正相关的块排到最前面，能显著提升最终答案质量。

评分公式（透明可调）：
    final = w_lex * bm25归一 + w_vec * vec归一
          + w_pos * 位置先验 + w_exact * 精确命中率

多轮对话多样性（可选）：MMR（最大边际相关）
    - 在保证「相关」的同时，惩罚与已选结果过于相似的候选，
      避免 top-N 全是同一段的重复内容。
"""


class Reranker:
    """轻量重排器：综合多信号打分 + 可选 MMR 去重。"""

    def __init__(self, w_lex: float = 0.35, w_vec: float = 0.35,
                 w_pos: float = 0.10, w_exact: float = 0.20,
                 use_mmr: bool = True, mmr_lambda: float = 0.7):
        """
        参数:
            w_lex:     BM25 信号权重。
            w_vec:     向量信号权重。
            w_pos:     位置先验权重（靠前的块略加分）。
            w_exact:   精确词命中权重。
            use_mmr:   是否启用 MMR 多样性。
            mmr_lambda: MMR 的相关性权重（越大越重相关，越小越重多样）。
        """
        # 保存各信号权重
        self.w_lex = w_lex
        self.w_vec = w_vec
        self.w_pos = w_pos
        self.w_exact = w_exact
        # 保存 MMR 配置
        self.use_mmr = use_mmr
        self.mmr_lambda = mmr_lambda

    def rerank(self, query: str, candidates: list, top_n: int = 5) -> list:
        """
        对候选列表重排，返回前 top_n 条。

        参数:
            query:      查询文本。
            candidates: Retriever 产出的候选列表。
            top_n:      最终保留的条数。

        返回:
            重排后的候选列表（已按分数降序）。
        """
        # 候选为空时直接返回
        if not candidates:
            return []

        # 计算全局归一化基准：BM25 与向量分数的最大值
        max_lex = max((c.bm25 for c in candidates), default=0.0)
        max_vec = max((c.vec for c in candidates), default=0.0)

        # 为每个候选计算综合分
        for c in candidates:
            # BM25 归一化到 [0,1]
            lex_n = c.bm25 / max_lex if max_lex > 0 else 0.0
            # 向量归一化到 [0,1]（向量分可能是负数，先整体平移取 max(0,·)）
            vec_n = max(0.0, c.vec / max_vec) if max_vec > 0 else 0.0
            # 位置先验：块越靠前（doc_id 小）越加分，用递减函数
            pos_n = 1.0 / (1.0 + c.doc_id * 0.01)
            # 精确命中率：查询词条中，有多少直接出现在该块里
            exact_n = self._exact_hit_ratio(query, c.text)
            # 加权求和得到最终分
            c.score = (self.w_lex * lex_n + self.w_vec * vec_n
                       + self.w_pos * pos_n + self.w_exact * exact_n)

        # 按综合分降序排列
        candidates.sort(key=lambda c: c.score, reverse=True)

        # 若启用 MMR，在已排序基础上做多样性筛选
        if self.use_mmr:
            return self._mmr_select(candidates, top_n)
        # 不启用 MMR：直接截取前 top_n
        return candidates[:top_n]

    @staticmethod
    def _exact_hit_ratio(query: str, text: str) -> float:
        """
        计算查询词条在文本中的直接命中率。

        参数:
            query: 查询文本。
            text:  候选块文本。

        返回:
            命中比例 [0,1]，越高说明字面匹配越多。
        """
        # 延迟导入分词器
        from .tokenizer import tokenize
        # 查询与文本分别分词
        q_terms = set(tokenize(query))
        t_terms = set(tokenize(text))
        # 查询没有有效词条时返回 0
        if not q_terms:
            return 0.0
        # 命中率 = 交集大小 / 查询词条数
        return len(q_terms & t_terms) / len(q_terms)

    @staticmethod
    def _text_sim(a: str, b: str) -> float:
        """
        计算两段文本的字面相似度（Jaccard），供 MMR 判重使用。

        参数:
            a, b: 两段文本。

        返回:
            Jaccard 相似度 [0,1]。
        """
        # 延迟导入分词器
        from .tokenizer import tokenize
        # 两个词集合
        sa, sb = set(tokenize(a)), set(tokenize(b))
        # 并集为空时相似度为 0
        if not sa and not sb:
            return 0.0
        # Jaccard = 交集 / 并集
        return len(sa & sb) / len(sa | sb)

    def _mmr_select(self, candidates: list, top_n: int) -> list:
        """
        用最大边际相关（MMR）贪心选择 top_n 条。

        公式（每步选使下式最大的候选）：
            score' = lambda * 相关分 - (1-lambda) * max(与已选文本的相似度)

        参数:
            candidates: 已按相关分排序的候选列表。
            top_n:      要选出的条数。

        返回:
            选出的候选列表。
        """
        # 已选中的结果
        selected = []
        # 已选文本列表（用于计算相似度）
        chosen_texts = []
        # 剩余候选（拷贝一份避免污染原列表）
        pool = list(candidates)
        # 贪心选择：循环直到选够或候选耗尽
        while len(selected) < top_n and pool:
            best = None      # 本轮最优候选
            best_score = -1  # 本轮最优分数
            for c in pool:
                # 相关项：当前综合分
                rel = c.score
                # 多样性项：与已选结果的最大相似度
                sim = max((self._text_sim(c.text, t) for t in chosen_texts),
                          default=0.0)
                # MMR 综合：相关 - 相似度惩罚
                mmr = self.mmr_lambda * rel - (1 - self.mmr_lambda) * sim
                # 记录本轮最优
                if mmr > best_score:
                    best_score = mmr
                    best = c
            # 把最优候选移入已选
            selected.append(best)
            chosen_texts.append(best.text)
            pool.remove(best)
        # 返回选出的结果
        return selected
