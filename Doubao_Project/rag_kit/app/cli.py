#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cli.py — コマンドラインインターフェース
================================================================
RAG の索引構築・質問応答・統計表示をターミナルから行います。

使い方の例:
    python app/cli.py build data out      # 索引を構築
    python app/cli.py ask out "RAGとは？"  # 質問に回答
    python app/cli.py stats out           # 統計を表示
"""

import argparse  # コマンドライン引数の解析に使用
import os        # パス操作に使用
import sys       # モジュール探索パスの調整に使用

# パッケージがある親ディレクトリをモジュール探索パスへ追加する
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag import RagPipeline  # パイプラインを読み込む


def cmd_build(args) -> None:
    """build サブコマンド：文書から索引を構築します。"""
    p = RagPipeline()                 # パイプラインを生成
    n = p.build_dir(args.data, args.out)  # 文書を読み込んで索引を構築
    print(f'構築完了: {n} チャンク → {args.out}')  # 結果を表示


def cmd_ask(args) -> None:
    """ask サブコマンド：保存済み索引を使って質問へ回答します。"""
    p = RagPipeline().load(args.index)  # 索引を読み込む
    res = p.ask(args.question, top_k=args.top_k,  # 質問を実行
                mmr_lambda=args.mmr, use_llm=args.llm)  # オプションを渡す
    print(res['answer'])              # 回答を表示
    print('\n--- 出典 ---')           # 区切り見出し
    for i, s in enumerate(res['sources'], 1):  # 出典を番号付きで
        src = s.get('src', s.get('doc_id', ''))  # 出典名を取得
        print(f'[{i}] {src} (score={s.get("score", "-")})')  # 表示
        sn = s.get('snippet', '')     # 抜粋があれば
        if sn:                        # 表示する
            print(f'    {sn[:80]}')   # 先頭80文字だけ表示


def cmd_stats(args) -> None:
    """stats サブコマンド：索引の統計を表示します。"""
    p = RagPipeline().load(args.index)  # 索引を読み込む
    st = p.stats()                    # 統計を取得
    print(f'チャンク数   : {st["n_chunks"]}')  # チャンク数
    print(f'語彙数       : {st["n_terms"]}')   # 語彙数
    print(f'出典ファイル数: {st["n_docs_src"]}')  # 出典数


def main() -> None:
    """サブコマンドを解析して各処理を実行します。"""
    parser = argparse.ArgumentParser(description='白箱 RAG コマンドライン')  # 親パーサ
    sub = parser.add_subparsers(dest='command', required=True)  # サブコマンド

    pb = sub.add_parser('build', help='文書から索引を構築')  # build定義
    pb.add_argument('data', help='文書ディレクトリ')  # 入力ディレクトリ
    pb.add_argument('out', nargs='?', default='out', help='保存先(既定: out)')  # 出力
    pb.set_defaults(func=cmd_build)   # 実行関数を登録

    pa = sub.add_parser('ask', help='質問に回答')  # ask定義
    pa.add_argument('index', help='索引ディレクトリ')  # 索引パス
    pa.add_argument('question', help='質問文')  # 質問文
    pa.add_argument('--top-k', type=int, default=5, help='検索件数(既定5)')  # 件数
    pa.add_argument('--mmr', type=float, default=0.0, help='MMR多様化係数')  # MMR
    pa.add_argument('--llm', action='store_true', help='LLM型で回答')  # LLM有効化
    pa.set_defaults(func=cmd_ask)     # 実行関数を登録

    ps = sub.add_parser('stats', help='索引の統計を表示')  # stats定義
    ps.add_argument('index', help='索引ディレクトリ')  # 索引パス
    ps.set_defaults(func=cmd_stats)   # 実行関数を登録

    args = parser.parse_args()        # 引数を解析
    args.func(args)                   # 対応する処理を実行


if __name__ == '__main__':            # 直接実行された場合のみ
    main()                            # メイン処理を起動
