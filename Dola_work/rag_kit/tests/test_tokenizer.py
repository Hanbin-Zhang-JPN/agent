#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""トークナイザーのテスト。"""

import os      # パス操作に使用
import sys     # モジュール探索パスの調整に使用
import unittest  # テストフレームワーク

# パッケージがある親ディレクトリをモジュール探索パスへ追加する
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag import tokenizer  # テスト対象のトークナイザー


class TestBm25Tokens(unittest.TestCase):
    """BM25用トークン生成のテスト。"""

    def test_cjk_one_char(self):
        """日本語は1文字ずつトークンになること。"""
        toks = tokenizer.bm25_tokens('検索')  # 2文字
        self.assertEqual(toks, ['検', '索'])  # 1文字ずつ分解

    def test_word_kept(self):
        """英単語はまとまった1トークンになること。"""
        toks = tokenizer.bm25_tokens('Hello World')  # 2単語
        self.assertEqual(toks, ['hello', 'world'])  # 小文字化も確認

    def test_mixed(self):
        """日本語と英字が混ざっても正しく分かれること。"""
        toks = tokenizer.bm25_tokens('RAGとは')  # 英字と漢字
        self.assertIn('rag', toks)  # 英単語が含まれる
        self.assertIn('と', toks)   # かなも含まれる

    def test_punctuation_removed(self):
        """記号はトークンにならないこと。"""
        toks = tokenizer.bm25_tokens('a!b, c。')  # 記号入り
        self.assertEqual(toks, ['a', 'b', 'c'])  # 語のみ残る


class TestVectorFeatures(unittest.TestCase):
    """ベクトル用n-gram特徴量のテスト。"""

    def test_bigram_default(self):
        """既定の bi-gram で分解されること。"""
        feats = tokenizer.vector_features('検索')  # 2文字
        self.assertEqual(feats, ['検索'])  # 1つのbi-gramになる

    def test_trigram_option(self):
        """n=3 を指定するとtri-gramになること。"""
        feats = tokenizer.vector_features('検索エンジン', n=3)  # 5文字
        self.assertIn('検索エ', feats)  # 先頭のtri-gram
        self.assertIn('エンジ', feats)  # 途中のtri-gram

    def test_word_unchanged(self):
        """英単語はそのまま特徴量になること。"""
        feats = tokenizer.vector_features('embedding')  # 英単語
        self.assertIn('embedding', feats)  # 単語単位で保持


if __name__ == '__main__':  # 直接実行された場合
    unittest.main()  # テストを実行
