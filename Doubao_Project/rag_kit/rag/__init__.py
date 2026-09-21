# -*- coding: utf-8 -*-
"""
rag — 白箱 RAG パッケージ
================================================================
外部ブラックボックス依存なしの軽量 RAG 実装。
主要なエントリポイントは RagPipeline です。

使い方の例:
    from rag import RagPipeline      # パイプラインを読み込む
    p = RagPipeline()                # インスタンスを作る
    p.build_dir('data')              # 文書から索引を構築
    print(p.ask('RAGとは何ですか？'))  # 質問に回答
"""

from .pipeline import RagPipeline  # メインのパイプラインを公開

__all__ = ['RagPipeline']  # 公開シンボルを明示
__version__ = '1.0.0'      # バージョン番号
