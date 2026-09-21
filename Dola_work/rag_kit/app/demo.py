#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
demo.py — 対話デモ
================================================================
文書ディレクトリから索引を構築し、ターミナルで
質問を繰り返し投げられる対話型のデモです。
「quit」「exit」と入力すると終了します。

使い方:
    python app/demo.py [data_dir] [out_dir]
"""

import os   # パス操作に使用
import sys  # モジュール探索パスの調整に使用

# パッケージがある親ディレクトリをモジュール探索パスへ追加する
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag import RagPipeline  # パイプラインを読み込む


def show_result(res: dict) -> None:
    """回答と出典を整形して表示します。"""
    print('\n' + '=' * 50)            # 区切り線
    print(res['answer'])              # 回答を表示
    print('-' * 50)                   # 区切り線
    if res['sources']:                # 出典があれば
        print('【出典】')              # 見出しを表示
        for i, s in enumerate(res['sources'], 1):  # 出典を番号付きで
            src = s.get('src', s.get('doc_id', ''))  # 出典名を取得
            print(f'[{i}] {src} (score={s.get("score", "-")})')  # 出典表示
    print('=' * 50)                   # 終端の区切り線


def main() -> None:
    """デモのメインループです。"""
    data_dir = sys.argv[1] if len(sys.argv) > 1 else 'data'  # 文書ディレクトリ
    out_dir = sys.argv[2] if len(sys.argv) > 2 else 'out'    # 保存先
    p = RagPipeline()                 # パイプラインを生成
    n = p.build_dir(data_dir, out_dir)  # 索引を構築
    print(f'索引を構築しました: {n} チャンク（{data_dir} → {out_dir}）')  # 完了通知
    print('質問を入力してください（終了は "quit" / "exit"）')  # 案内
    while True:                       # 対話ループ
        q = input('\n質問> ').strip()  # 質問を入力
        if q.lower() in ('quit', 'exit'):  # 終了コマンドなら
            break                     # ループを抜ける
        if not q:                     # 空入力なら
            continue                  # 再度入力を促す
        try:                          # 回答処理を実行
            res = p.ask(q, top_k=5)   # 質問を投げる
            show_result(res)          # 結果を表示
        except Exception as e:        # エラー時は
            print(f'エラー: {e}')      # 内容を表示して継続


if __name__ == '__main__':            # 直接実行された場合のみ
    main()                            # メイン処理を起動
