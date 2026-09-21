#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""チャンク分割のテスト。"""

import os      # パス操作に使用
import sys     # モジュール探索パスの調整に使用
import unittest  # テストフレームワーク

# パッケージがある親ディレクトリをモジュール探索パスへ追加する
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag import chunker  # テスト対象のチャンカ


class TestChunker(unittest.TestCase):
    """チャンク分割のテスト。"""

    def test_split_paragraphs(self):
        """空行で段落が分かれること。"""
        paras = chunker.split_paragraphs('段落1\n\n段落2')  # 2段落
        self.assertEqual(paras, ['段落1', '段落2'])  # 分割を確認

    def test_small_doc_one_chunk(self):
        """短い文書は1チャンクになること。"""
        chunks = chunker.chunk_document('短い文章です。', 'a.md')  # 短い文書
        self.assertEqual(len(chunks), 1)  # 1チャンク

    def test_long_doc_multiple(self):
        """長い文書は複数チャンクに分割されること。"""
        # 500文字の長い文書を作る
        text = ('これはテスト用の長文です。' * 50)  # 約550文字
        chunks = chunker.chunk_document(text, 'a.md', chunk_size=200)  # 200文字基準
        self.assertGreater(len(chunks), 1)  # 複数に分割

    def test_heading_tracked(self):
        """見出しがメタデータとして記録されること。"""
        text = '# 導入\n\nここに本文があります。'  # 見出し付き
        chunks = chunker.chunk_document(text, 'a.md')  # 分割
        self.assertEqual(chunks[0].heading, '# 導入')  # 見出しを確認

    def test_overlap_carried(self):
        """オーバーラップが次のチャンクへ引き継がれること。"""
        # 十分な長さの文書を用意
        text = '\n\n'.join(f'段落{i}の内容です。' * 8 for i in range(8))  # 8段落
        chunks = chunker.chunk_document(text, 'a.md', chunk_size=80, overlap=20)  # 分割
        self.assertGreaterEqual(len(chunks), 2)  # 複数チャンク
        # 2番目のチャンクに前チャンクの末尾が含まれる
        self.assertIn(chunks[0].text.split('\n')[-1], chunks[1].text)  # 重複を確認


if __name__ == '__main__':  # 直接実行された場合
    unittest.main()  # テストを実行
