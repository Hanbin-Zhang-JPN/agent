#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""パイプライン統合のテスト。"""

import os      # パス操作に使用
import sys     # モジュール探索パスの調整に使用
import unittest  # テストフレームワーク

# パッケージがある親ディレクトリをモジュール探索パスへ追加する
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag import RagPipeline  # テスト対象のパイプライン

# テスト用の小さな文書セット
SAMPLE_DOCS = [
    ('a.md', 'RAGは検索と生成を組み合わせた手法です。\n\n'
             '大量の文書をインデックス化して検索し、回答を生成します。'),
    ('b.md', 'BM25はキーワードベースの検索モデルです。\n\n'
             '質問の語が文書にどれだけ含まれるかでスコアを計算します。'),
    ('c.md', 'ベクトル検索は文書を数値ベクトルに変換して類似度を測ります。\n\n'
             '表記ゆれや類義表現に強いという特徴があります。'),
]


class TestPipeline(unittest.TestCase):
    """パイプライン全体のテスト。"""

    def setUp(self):
        """各テスト共通の準備を行います。"""
        self.p = RagPipeline(chunk_size=60, overlap=10)  # 小さいパイプライン
        self.p.build_texts(SAMPLE_DOCS)  # テスト文書で構築

    def test_build_counts(self):
        """索引が正しく構築されること。"""
        st = self.p.stats()             # 統計を取得
        self.assertEqual(st['n_chunks'], 3)  # 3チャンク
        self.assertEqual(st['n_docs_src'], 3)  # 3出典

    def test_ask_returns_answer(self):
        """質問に対して回答が返ること。"""
        res = self.p.ask('BM25とは何ですか？')  # 質問
        self.assertIn('answer', res)    # 回答フィールド
        self.assertEqual(res['mode'], 'extractive')  # 抽出型
        self.assertGreater(len(res['answer']), 0)  # 空でない

    def test_ask_finds_relevant(self):
        """関連する出典が上位に来ること。"""
        res = self.p.ask('ベクトル検索の特徴は？')  # 質問
        self.assertEqual(res['sources'][0]['src'], 'c.md')  # 文書cが最上位

    def test_save_load(self):
        """保存・復元後も質問に答えられること。"""
        import tempfile                 # 一時ディレクトリ用
        with tempfile.TemporaryDirectory() as d:  # 一時ディレクトリ
            self.p.save(d)              # 保存
            p2 = RagPipeline().load(d)  # 復元
            res = p2.ask('RAGとは何ですか？')  # 質問
            self.assertIn('answer', res)  # 回答が返る

    def test_not_built_error(self):
        """未構築で質問すると例外になること。"""
        p = RagPipeline()               # 未構築のパイプライン
        with self.assertRaises(RuntimeError):  # 例外を期待
            p.ask('テスト')             # 質問を実行


if __name__ == '__main__':  # 直接実行された場合
    unittest.main()  # テストを実行
