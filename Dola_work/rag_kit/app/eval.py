#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
eval.py — 検索精度の簡易評価
================================================================
「(質問, 期待する出典ファイル名)」のペアを用意し、
上位 k 件の検索結果に期待出典が含まれる割合（Accuracy@k）を測ります。
データセットを追加すれば、チャンクサイズや方式の改善効果を定量確認できます。

使い方:
    python app/eval.py out            # 保存済み索引で評価
    python app/eval.py out --top-k 3  # 上位3件で評価
"""

import os   # パス操作に使用
import sys  # モジュール探索パスの調整に使用
import argparse  # コマンドライン引数の解析に使用

# パッケージがある親ディレクトリをモジュール探索パスへ追加する
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag import RagPipeline  # パイプラインを読み込む

# 評価用の小規模データセット（質問 → 期待する出典）
# サンプル文書に合わせて作成しており、実際の文書に応じて書き換えてください
QA_SET = [
    ('RAGとは何ですか？', 'rag_intro.md'),
    ('RAGが必要な理由は？', 'rag_intro.md'),
    ('RAGの基本フローは？', 'rag_intro.md'),
    ('チャンク分割とは？', 'rag_architecture.md'),
    ('BM25とは何ですか？', 'rag_architecture.md'),
    ('ハイブリッド検索とは？', 'rag_architecture.md'),
    ('MMRとは何ですか？', 'rag_architecture.md'),
    ('RAGの評価はどう行う？', 'rag_advanced.md'),
    ('n-gramの利点は？', 'rag_advanced.md'),
    ('特徴ハッシュとは？', 'rag_advanced.md'),
]


def run_eval(p: RagPipeline, top_k: int) -> None:
    """質問セットを走査して Accuracy@k を表示します。"""
    hit = 0                           # 正解した数
    total = len(QA_SET)               # 全質問数
    for q, expected in QA_SET:        # 各質問について
        hits = p.ask(q, top_k=top_k)['sources']  # 上位k件の出典を取得
        got = {h['src'] for h in hits}  # 出典名の集合にする
        ok = expected in got          # 期待出典が含まれるか
        hit += ok                     # 正解なら加算
        mark = 'OK' if ok else 'NG'   # 判定マーク
        print(f'[{mark}] {q} -> 期待:{expected} 取得:{sorted(got)[:top_k]}')  # 結果表示
    acc = hit / total                 # 正解率を計算
    print(f'\nAccuracy@{top_k}: {hit}/{total} = {acc:.2%}')  # 全体の精度を表示


def main() -> None:
    """コマンドラインのエントリポイントです。"""
    parser = argparse.ArgumentParser(description='検索精度の簡易評価')  # パーサ
    parser.add_argument('index', help='索引ディレクトリ')  # 索引パス
    parser.add_argument('--top-k', type=int, default=1, help='上位何件で判定(既定1)')  # k値
    args = parser.parse_args()        # 引数を解析
    p = RagPipeline().load(args.index)  # 索引を読み込む
    run_eval(p, args.top_k)           # 評価を実行


if __name__ == '__main__':            # 直接実行された場合のみ
    main()                            # メイン処理を起動
