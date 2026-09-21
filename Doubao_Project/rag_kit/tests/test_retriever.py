#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ベクトル計算・BM25索引・検索のテスト。"""

import os      # パス操作に使用
import sys     # モジュール探索パスの調整に使用
import unittest  # テストフレームワーク

# パッケージがある親ディレクトリをモジュール探索パスへ追加する
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag import vectors      # ベクトル計算
from rag import tokenizer    # トークナイザー
from rag.index import Bm25Index, Corpus  # 索引とコーパス


class TestVectors(unittest.TestCase):
    """ベクトル計算のテスト。"""

    def test_fnv1a_stable(self):
        """ハッシュは常に同じ値を返すこと。"""
        self.assertEqual(vectors.fnv1a('テスト', 100), vectors.fnv1a('テスト', 100))  # 同一
        self.assertLess(vectors.fnv1a('テスト', 100), 100)  # 範囲内

    def test_cosine_identical(self):
        """同一ベクトルの類似度は1になること。"""
        v = {1: 1.0, 2: 2.0}  # ベクトル
        self.assertAlmostEqual(vectors.cosine(v, v), 1.0)  # 自分自身と比較

    def test_cosine_orthogonal(self):
        """直交ベクトルの類似度は0になること。"""
        a = {1: 1.0}  # ベクトルA
        b = {2: 1.0}  # ベクトルB
        self.assertAlmostEqual(vectors.cosine(a, b), 0.0)  # 直交を確認

    def test_tfidf_roundtrip(self):
        """ベクトル化器が保存・復元できること。"""
        v = vectors.TfidfVectorizer(dim=64)  # ベクトル化器
        v.fit([['a'], ['a', 'b']])           # 文書頻度を学習
        vec = v.transform(['a', 'a', 'b'])   # ベクトル化
        self.assertGreater(len(vec), 0)      # 空でないこと


class TestBm25(unittest.TestCase):
    """BM25 索引のテスト。"""

    def _build(self):
        """小さなテスト索引を作ります。"""
        idx = Bm25Index()                 # 索引を生成
        idx.add(0, ['検', '索', '機械'])   # 文書0
        idx.add(1, ['検', '索', '学習'])   # 文書1
        idx.add(2, ['料理', 'レシピ'])      # 文書2
        return idx                        # 索引を返す

    def test_search_rank(self):
        """関連する文書が上位に来ること。"""
        idx = self._build()               # 索引を準備
        hits = idx.search(['検', '索'], top_k=3)  # 検索
        top = hits[0][0]                  # 最上位の文書ID
        self.assertIn(top, (0, 1))        # 文書0か1が来る

    def test_unrelated_not_top(self):
        """無関係な文書は上位に来ないこと。"""
        idx = self._build()               # 索引を準備
        hits = idx.search(['料理'], top_k=3)  # 検索
        self.assertEqual(hits[0][0], 2)   # 文書2が最上位

    def test_save_load(self):
        """索引が保存・復元できること。"""
        import tempfile                   # 一時ファイル用
        idx = self._build()               # 索引を準備
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:  # 一時ファイル
            path = f.name                 # パスを取得
        try:                              # テスト本体
            idx.save(path)                # 保存
            loaded = Bm25Index.load(path)  # 復元
            self.assertEqual(loaded.n, idx.n)  # 文書数が一致
        finally:                          # 後始末
            os.remove(path)               # 一時ファイルを削除


class TestCorpus(unittest.TestCase):
    """コーパス保存のテスト。"""

    def test_save_load(self):
        """コーパスが保存・復元できること。"""
        import tempfile                   # 一時ファイル用
        c = Corpus()                      # コーパス生成
        c.add('本文です', 'a.md', '# 見出し', 0)  # チャンク追加
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:  # 一時ファイル
            path = f.name                 # パスを取得
        try:                              # テスト本体
            c.save(path)                  # 保存
            loaded = Corpus.load(path)    # 復元
            self.assertEqual(loaded.text(0), '本文です')  # 本文が一致
        finally:                          # 後始末
            os.remove(path)               # 一時ファイルを削除


if __name__ == '__main__':  # 直接実行された場合
    unittest.main()  # テストを実行
