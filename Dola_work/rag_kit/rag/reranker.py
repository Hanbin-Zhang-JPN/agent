# -*- coding: utf-8 -*-
"""
reranker.py — 軽量再ランキング（外部ライブラリ不要）
================================================================
検索で得た上位候補を、より細かな観点で並べ替えます。
  - クエリ語の被覆率  : 質問の語がどれだけ含まれるか（高いほど良い）
  - 長さの罰則        : 極端に短い・長いチャンクを割り引く
  - 見出しボーナス    : 見出しを持つチャンクは自己完結的で高評価
重い外部モデルは使わず、全ての係数をコード内で明示しています。
"""

import math  # 対数による長さ罰則の計算に使用

from . import tokenizer  # トークナイザー（同一パッケージ内）


class Reranker:
    """検索結果を説明可能なルールで再ランキングします。"""
    # 各観点の重み（チューニングしやすいよう定数で分離）
    W_COVERAGE = 0.6          # 被覆率の重み
    W_LENGTH = 0.3            # 長さ罰則の重み
    B_HEADING = 0.05          # 見出しボーナス
    OPT_LEN = 300             # 長さ罰則の基準となる文字数

    def __init__(self, doc_tokens: list, records: list):
        self.doc_tokens = doc_tokens  # 文書ごとの語彙トークン
        self.records = records        # 文書ID → チャンク情報

    def _coverage(self, q_tokens: set, doc_id: int) -> float:
        """クエリ語のうち何割がこの文書に含まれるかを返します。"""
        if not q_tokens:              # クエリ語が無ければ
            return 0.0                # 被覆率0
        doc_set = set(self.doc_tokens[doc_id])  # 文書の語を集合化
        hit = len(q_tokens & doc_set) # 共通する語の数
        return hit / len(q_tokens)    # 割合を返す

    def _length_penalty(self, doc_id: int) -> float:
        """チャンク長が基準から外れるほど大きくなる罰則を返します。"""
        text = self.records[doc_id]['text']  # チャンク本文を取得
        n = len(text)                 # 文字数
        ratio = n / self.OPT_LEN      # 基準長との比
        if ratio == 0:                # 空なら
            return 1.0                # 最大の罰則
        # 対数尺度で基準から離れるほど罰則を大きくする（0〜1に丸める）
        pen = abs(math.log2(ratio)) / 5.0  # 5倍で割って0〜1程度に正規化
        return min(pen, 1.0)          # 最大1.0に制限

    def rerank(self, hits: list, query_text: str, top_k: int = None) -> list:
        """
        検索ヒット [(文書ID, ベーススコア), ...] を並べ替えます。
        top_k 指定時は上位のみ返します。
        """
        q_tokens = set(tokenizer.bm25_tokens(query_text))  # クエリ語集合
        scored = []                   # 再計算後の結果
        for doc_id, base in hits:     # 各ヒットについて
            cov = self._coverage(q_tokens, doc_id)  # 被覆率
            lp = self._length_penalty(doc_id)       # 長さ罰則
            heading = bool(self.records[doc_id]['heading'])  # 見出し有無
            hb = self.B_HEADING if heading else 0.0  # 見出しボーナス
            final = base + self.W_COVERAGE * cov - self.W_LENGTH * lp + hb  # 合成
            scored.append((doc_id, final))          # 結果へ追加
        scored.sort(key=lambda x: -x[1])            # スコア降順で並べる
        if top_k:                                   # 件数指定があれば
            scored = scored[:top_k]                 # 上位で切り出す
        return scored                               # 再ランク結果を返す
