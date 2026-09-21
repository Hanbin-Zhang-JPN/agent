# -*- coding: utf-8 -*-
"""
vectors.py — 白箱ベクトル化（外部ライブラリ不要）
================================================================
文書を「TF-IDF 重み付きのスパースベクトル」へ変換します。
  - 特徴量（n-gram / 単語）を FNV-1a ハッシュで固定次元へ写像
  - 単語の出現頻度(TF) と 希少度(IDF) で重み付け
  - 文書間の類似度はスパースベクトルのコサイン類似度で計算
numpy などは使わず、dict と math だけで実装しています。
"""

import math  # 対数・平方根などの計算に使用
import json  # 保存・復元に使用


def fnv1a(text: str, dim: int) -> int:
    """
    文字列を FNV-1a ハッシュで 0〜dim-1 の整数へ写像します。
    Python 組み込みの hash() はプロセス毎に値が変わるため、
    保存データと再現性を保つため独自の安定ハッシュを使います。
    """
    h = 2166136261                    # FNV-1a のオフセット基底（定数）
    for b in text.encode('utf-8'):    # UTF-8 の各バイトについて
        h ^= b                        # バイトを排他的論理和で混ぜる
        h = (h * 16777619) & 0xFFFFFFFF  # 素数を掛けて 32bit へ丸める
    return h % dim                    # 次元の範囲内へ写像


def cosine(a: dict, b: dict) -> float:
    """スパースベクトル（dict）同士のコサイン類似度を計算します。"""
    if not a or not b:                # どちらかが空なら
        return 0.0                    # 類似度は0とみなす
    dot = 0.0                         # 内積の累積
    for k, v in a.items():            # 片方の要素を走査
        if k in b:                    # 相手にも同じ次元があれば
            dot += v * b[k]           # 内積へ加算
    na = math.sqrt(sum(v * v for v in a.values()))  # ベクトルaの長さ
    nb = math.sqrt(sum(v * v for v in b.values()))  # ベクトルbの長さ
    if na == 0 or nb == 0:            # どちらかが零ベクトルなら
        return 0.0                    # 類似度は0
    return dot / (na * nb)            # コサイン類似度を返す


def normalize(vec: dict) -> dict:
    """ベクトルを単位長さ（L2正規化）にします。"""
    n = math.sqrt(sum(v * v for v in vec.values()))  # ベクトルの長さ
    if n == 0:                        # 長さが0なら
        return vec                    # そのまま返す
    return {k: v / n for k, v in vec.items()}  # 各要素を長さで割る


class TfidfVectorizer:
    """
    TF-IDF ベクトル化器。
      - fit()     : コーパス全体から文書頻度(IDF用)を集計
      - transform(): 1文書の特徴量リストを TF-IDF スパースベクトルへ変換
    """
    def __init__(self, dim: int = 4096):
        self.dim = dim                # 特徴ハッシュの次元数
        self.df = {}                  # 特徴語 → 出現文書数
        self.n_docs = 0               # 学習した文書数

    def fit(self, doc_features: list) -> 'TfidfVectorizer':
        """コーパス全体の文書頻度を集計します。"""
        seen = []                     # 文書ごとの重複除去リスト
        for feats in doc_features:    # 各文書の特徴量について
            seen.append(set(feats))   # 重複を除いて保持
        self.df = {}                  # 集計を初期化
        for s in seen:                # 各文書の特徴集合について
            for f in s:               # 各特徴語を
                self.df[f] = self.df.get(f, 0) + 1  # 出現文書数を+1
        self.n_docs = len(seen)       # 文書数を記録
        return self                   # チェーン呼び出し用に自身を返す

    def idf(self, feature: str) -> float:
        """特徴語の IDF（希少度）を計算します。"""
        df = self.df.get(feature, 0)  # 出現文書数（無ければ0）
        # 平滑化付きの対数式。分母分子に+1してゼロ除算を防ぐ
        return math.log((self.n_docs + 1) / (df + 1)) + 1.0

    def transform(self, feats: list) -> dict:
        """特徴量リストを TF-IDF スパースベクトル（dict）へ変換します。"""
        tf = {}                       # 文書内での出現回数
        for f in feats:               # 各特徴語について
            tf[f] = tf.get(f, 0) + 1  # 出現回数を加算
        vec = {}                      # 結果のベクトル
        for f, c in tf.items():       # 各語と回数について
            w = (1 + math.log(c)) * self.idf(f)  # TF×IDF の重みを計算
            idx = fnv1a(f, self.dim)  # 特徴語を次元番号へ写像
            vec[idx] = vec.get(idx, 0) + w  # 衝突時は重みを加算
        return vec                    # スパースベクトルを返す

    def save(self, path: str) -> None:
        """ベクトル化器の状態をJSONとして保存します。"""
        data = {'dim': self.dim, 'n_docs': self.n_docs, 'df': self.df}  # 保存対象
        with open(path, 'w', encoding='utf-8') as fp:  # 書き込みモードで開く
            json.dump(data, fp, ensure_ascii=False)    # JSONへ書き出す

    @classmethod
    def load(cls, path: str) -> 'TfidfVectorizer':
        """保存済みのベクトル化器を読み込みます。"""
        with open(path, 'r', encoding='utf-8') as fp:  # 読み込みモードで開く
            data = json.load(fp)      # JSONをパース
        obj = cls(data['dim'])        # 次元を指定して生成
        obj.n_docs = data['n_docs']   # 文書数を復元
        obj.df = data['df']           # 文書頻度を復元
        return obj                    # 復元したオブジェクトを返す
