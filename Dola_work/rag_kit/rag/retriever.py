# -*- coding: utf-8 -*-
"""
retriever.py — ハイブリッド検索（外部ライブラリ不要）
================================================================
2つの検索結果を組み合わせて精度を高めます。
  1. BM25（語彙の完全一致）          : 確実なキーワードヒットを拾う
  2. n-gramベクトルのコサイン類似度  : 表記ゆれや類義表現を拾う
  3. RRF（Reciprocal Rank Fusion）  : 2つの順位を統合して最終順位を作る
  4. 任意で MMR により回答の多様性を確保する
"""

from . import tokenizer  # トークナイザー（同一パッケージ内）
from . import vectors    # ベクトル計算（同一パッケージ内）
from .index import Bm25Index  # BM25 索引


def rrf(ranked_lists: list, k: int = 60) -> list:
    """
    RRF で複数の順位リストを1つへ統合します。
    順位が上位であるほど 1/(k+順位) の加点が大きくなるため、
    複数方式で上位に入った文書が自然と高評価になります。
    """
    scores = {}                       # 文書ID → 融合スコア
    for lst in ranked_lists:          # 各方式の順位リストについて
        for rank, (doc_id, _) in enumerate(lst):  # 順位付きで走査
            scores[doc_id] = scores.get(doc_id, 0) + 1.0 / (k + rank + 1)  # 加算
    return sorted(scores.items(), key=lambda x: -x[1])  # スコア降順で返す


class HybridRetriever:
    """BM25 とベクトル類似度を RRF で融合する検索器です。"""
    def __init__(self, bm25: Bm25Index, vectorizer,
                 doc_vectors: list, doc_tokens: list):
        self.bm25 = bm25              # BM25 索引
        self.vectorizer = vectorizer  # TF-IDF ベクトル化器
        self.doc_vectors = doc_vectors  # 正規化済み文書ベクトル
        self.doc_tokens = doc_tokens  # 文書ごとの語彙トークン（再ランク用）

    def _cosine_scores(self, q_vec: dict) -> list:
        """全文書とのコサイン類似度を計算し、降順リストで返します。"""
        scores = []                   # 結果のリスト
        for doc_id, dv in enumerate(self.doc_vectors):  # 全文書を走査
            scores.append((doc_id, vectors.cosine(q_vec, dv)))  # 類似度を計算
        scores.sort(key=lambda x: -x[1])  # 降順で並べる
        return scores                 # 全文書の類似度リストを返す

    def _mmr_select(self, ranked: list, top_k: int, lam: float) -> list:
        """
        MMR（Maximal Marginal Relevance）で多様性を確保します。
        関連性(rel)が高く、かつ既選文書と似ていない文書を順に選びます。
        """
        chosen = []                   # 選択済み文書ID
        cand = list(ranked)           # 候補リスト（融合スコア付き）
        while cand and len(chosen) < top_k:  # 選ぶ数に達するまで
            best_i = None             # 最良候補の添字
            best_s = -1e18            # 最良スコア
            for i, (doc_id, rel) in enumerate(cand):  # 各候補を評価
                if chosen:            # 既に選んだ文書があれば
                    # 既選文書との最大類似度 = 冗長度（小さいほど良い）
                    div = max(vectors.cosine(self.doc_vectors[doc_id],
                                             self.doc_vectors[c]) for c in chosen)
                else:                 # 最初の1件は冗長度0
                    div = 0.0
                s = lam * rel - (1 - lam) * div  # 関連性−冗長性で評価
                if s > best_s:        # より良いスコアなら
                    best_s = s        # 記録を更新
                    best_i = i        # 添字を記録
            chosen.append(cand[best_i][0])  # 最良候補を選択
            cand.pop(best_i)          # 候補から除外
        score_map = dict(ranked)      # スコア対応表を作る
        return [(d, score_map[d]) for d in chosen]  # 選んだ文書をスコア付きで返す

    def search(self, query_text: str, top_k: int = 5,
               rrf_k: int = 60, mmr_lambda: float = 0.0) -> list:
        """
        クエリ文に対する上位文書を [(文書ID, 融合スコア), ...] で返します。
          - top_k      : 返す件数
          - rrf_k      : RRF の平滑化定数（既定60が一般的）
          - mmr_lambda : 0より大きいと MMR で多様化（0.7前後が目安）
        """
        q_tokens = tokenizer.bm25_tokens(query_text)  # 語彙トークン
        q_feats = tokenizer.vector_features(query_text)  # n-gram特徴量
        q_vec = self.vectorizer.transform(q_feats)    # クエリベクトル
        # 各方式の順位リストを用意
        bm25_list = self.bm25.search(q_tokens, top_k=max(top_k * 5, 20))  # BM25上位
        vec_list = self._cosine_scores(q_vec)         # ベクトル類似度全順位
        fused = rrf([bm25_list, vec_list], k=rrf_k)   # 2つの順位を融合
        if mmr_lambda > 0:                            # 多様化が指定されていれば
            fused = self._mmr_select(fused, top_k, mmr_lambda)  # MMR適用
        return fused[:top_k]                          # 上位を返す
