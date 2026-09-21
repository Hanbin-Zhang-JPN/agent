# -*- coding: utf-8 -*-
"""
index.py — BM25索引とコーパス保存（外部ライブラリ不要）
================================================================
語彙トークン（完全一致）を使った古典的かつ実績ある検索モデル BM25 を
白箱で実装します。あわせてチャンク本文を保存する Corpus も管理します。
"""

import math  # 対数などの計算に使用
import json  # 保存・復元に使用


class Bm25Index:
    """
    BM25 検索インデックス。
      - postings : 語 → [(文書ID, その文書内の出現回数)]
      - doc_tf   : 文書ID → {語: 出現回数}（スコア計算の高速化用）
      - doc_len  : 文書ごとのトークン数
    k1 と b は BM25 の標準パラメータ（k1=1.5, b=0.75）を既定にします。
    """
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1                  # 語の飽和度（出現回数の頭打ち具合）
        self.b = b                    # 文書長の正規化の強さ
        self.postings = {}            # 転置索引（語→ポスティングリスト）
        self.doc_tf = []              # 文書ごとの語頻度辞書
        self.doc_len = []             # 文書ごとのトークン数
        self.n = 0                    # 登録された文書数
        self.avgdl = 0.0              # 平均文書長

    def add(self, doc_id: int, tokens: list) -> None:
        """1文書のトークン列を索引へ登録します。"""
        tf = {}                       # この文書内の語頻度
        for t in tokens:              # 各トークンについて
            tf[t] = tf.get(t, 0) + 1  # 出現回数を加算
        self.doc_tf.append(tf)        # 語頻度辞書を保存
        self.doc_len.append(len(tokens))  # 文書長を保存
        for t, c in tf.items():       # 各語について
            self.postings.setdefault(t, []).append((doc_id, c))  # 転置索引へ追加
        self.n += 1                   # 文書数を更新
        self.avgdl = sum(self.doc_len) / self.n  # 平均文書長を更新

    def candidates(self, query_tokens: list) -> set:
        """クエリの語を1つ以上含む文書IDの集合を返します。"""
        ids = set()                   # 候補文書の集合
        for t in query_tokens:        # 各クエリ語について
            for doc_id, _ in self.postings.get(t, []):  # ポスティングを走査
                ids.add(doc_id)       # 候補へ追加
        return ids                    # 候補集合を返す

    def score(self, doc_id: int, query_tokens: list) -> float:
        """1文書の BM25 スコアを計算します。"""
        dl = self.doc_len[doc_id]     # 文書長を取得
        tf_dict = self.doc_tf[doc_id]  # 語頻度辞書を取得
        s = 0.0                       # スコアの累積
        for t in set(query_tokens):   # 重複を除いたクエリ語について
            df = len(self.postings.get(t, []))  # その語の出現文書数
            if df == 0:               # 語が索引に無ければ
                continue              # この語は無視
            # IDF: 希少な語ほど重みを大きくする（平滑化付き）
            idf = math.log((self.n - df + 0.5) / (df + 0.5) + 1.0)
            tf = tf_dict.get(t, 0)    # 文書内の出現回数
            # BM25 の本体式：TFを飽和させ、長い文書を割り引く
            denom = tf + self.k1 * (1 - self.b + self.b * dl / self.avgdl)
            s += idf * (tf * (self.k1 + 1)) / denom  # スコアへ加算
        return s                      # 合計スコアを返す

    def search(self, query_tokens: list, top_k: int = 10) -> list:
        """クエリに対する上位文書を [(文書ID, スコア), ...] で返します。"""
        scored = []                   # スコア付きの結果
        for doc_id in self.candidates(query_tokens):  # 候補を1件ずつ
            scored.append((doc_id, self.score(doc_id, query_tokens)))  # スコア計算
        scored.sort(key=lambda x: x[1], reverse=True)  # スコア降順で並べる
        return scored[:top_k]         # 上位を返す

    def save(self, path: str) -> None:
        """索引をJSONとして保存します。"""
        data = {                      # 保存対象をまとめる
            'k1': self.k1, 'b': self.b, 'n': self.n, 'avgdl': self.avgdl,
            'doc_len': self.doc_len, 'doc_tf': self.doc_tf,
            'postings': {t: post for t, post in self.postings.items()},
        }
        with open(path, 'w', encoding='utf-8') as fp:  # 書き込みモードで開く
            json.dump(data, fp, ensure_ascii=False)    # JSONへ書き出す

    @classmethod
    def load(cls, path: str) -> 'Bm25Index':
        """保存済みの索引を読み込みます。"""
        with open(path, 'r', encoding='utf-8') as fp:  # 読み込みモードで開く
            data = json.load(fp)      # JSONをパース
        obj = cls(data['k1'], data['b'])  # パラメータを指定して生成
        obj.n = data['n']             # 文書数を復元
        obj.avgdl = data['avgdl']     # 平均文書長を復元
        obj.doc_len = data['doc_len']  # 文書長を復元
        obj.doc_tf = data['doc_tf']   # 語頻度を復元
        obj.postings = {t: [tuple(p) for p in post] for t, post in data['postings'].items()}  # 復元
        return obj                    # 復元した索引を返す


class Corpus:
    """チャンク本文と出典情報を保持するストアです。"""
    def __init__(self):
        self.records = []             # チャンク情報のリスト

    def add(self, text: str, src: str, heading: str, index: int) -> None:
        """1チャンクを追加します。"""
        self.records.append({'text': text, 'src': src,  # 本文と出典
                             'heading': heading, 'index': index})  # 見出しと通し番号

    def text(self, i: int) -> str:
        """i番目のチャンク本文を返します。"""
        return self.records[i]['text']

    def __len__(self) -> int:
        """チャンク総数を返します。"""
        return len(self.records)

    def save(self, path: str) -> None:
        """コーパスをJSONとして保存します。"""
        with open(path, 'w', encoding='utf-8') as fp:  # 書き込みモードで開く
            json.dump(self.records, fp, ensure_ascii=False)  # 全レコードを書く

    @classmethod
    def load(cls, path: str) -> 'Corpus':
        """保存済みのコーパスを読み込みます。"""
        obj = cls()                   # 空のコーパスを生成
        with open(path, 'r', encoding='utf-8') as fp:  # 読み込みモードで開く
            obj.records = json.load(fp)  # レコードを復元
        return obj                    # 復元したコーパスを返す
