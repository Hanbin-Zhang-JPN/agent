# -*- coding: utf-8 -*-
"""
loader.py — ドキュメント読み込み（外部ライブラリ不要）
================================================================
テキスト系ファイル（.txt / .md / .csv）を読み込んで
「(出典ファイル名, 本文)」のリストへ変換します。
PDFは任意のオプション機能として、pypdfが入っている時だけ対応します。
"""

import os      # ファイル一覧の取得に使用
import csv     # CSVパースに使用（標準ライブラリ）
import io      # 文字コード変換に使用

# 対応するテキスト系拡張子（小文字で管理）
_TEXT_EXTS = {'.txt', '.md', '.markdown', '.rst', '.csv'}
# 文字コードの候補（日本語文書を順に試す）
_ENCODINGS = ('utf-8', 'utf-8-sig', 'shift_jis', 'cp932', 'euc_jp')


def _read_text(path: str) -> str:
    """ファイルを複数の文字コードで試しながら読み込みます。"""
    raw = open(path, 'rb').read()      # まずバイナリで全体を読む
    for enc in _ENCODINGS:             # 候補コードを順に試す
        try:                           # デコード成功なら
            return raw.decode(enc)     # その文字コードで確定
        except (UnicodeDecodeError, ValueError):  # 失敗したら次を試す
            continue                   # 次の候補へ進む
    return raw.decode('utf-8', errors='replace')  # 全て失敗時は代替文字で読む


def _read_pdf(path: str) -> str:
    """PDFを読み込みます（任意依存: pypdf が無ければエラー）。"""
    try:                                  # オプション依存を遅延import
        import pypdf                      # PDF解析ライブラリ（任意）
    except ImportError:                   # 未インストールなら
        raise RuntimeError(               # 明確にエラーを通知する
            'PDF読込には "pip install pypdf" が必要です')  # 対処法を案内
    text = []                             # ページ本文のリスト
    reader = pypdf.PdfReader(path)        # PDFを開く
    for page in reader.pages:             # 各ページについて
        text.append(page.extract_text() or '')  # テキストを抽出して追加
    return '\n'.join(text)                # 全ページを結合して返す


def load_file(path: str):
    """1ファイルを読み込み「(src, text)」を返します。"""
    ext = os.path.splitext(path)[1].lower()   # 拡張子を取り出す
    if ext == '.pdf':                         # PDFなら
        text = _read_pdf(path)                # 専用処理で読む
    elif ext in _TEXT_EXTS:                   # テキスト系なら
        text = _read_text(path)               # 文字コード判定して読む
    else:                                     # 未対応の拡張子は
        return None                           # 読み飛ばす
    return (os.path.basename(path), text)     # (ファイル名, 本文) を返す


def load_directory(dir_path: str) -> list:
    """
    ディレクトリ内の対応ファイルを全て読み込みます。
    戻り値は [(src, text), ...] のリストです。
    """
    results = []                          # 結果のリスト
    for name in sorted(os.listdir(dir_path)):  # ファイル名順に処理
        if name.startswith('.'):          # 隠しファイルは無視
            continue                      # スキップ
        path = os.path.join(dir_path, name)   # フルパスを作る
        if not os.path.isfile(path):      # ディレクトリなら
            continue                      # スキップ
        item = load_file(path)            # ファイルを読み込む
        if item:                          # 対応形式なら
            results.append(item)          # リストへ追加
    return results                        # 全ファイルの結果を返す


def load_csv_records(path: str) -> list:
    """
    CSVを「文書レコード」として読み込みます。
    各レコードは「列名: 値」を改行で連結した1つの文書テキストになります。
    この関数は主に付加情報付きの文書を取り込む用途を想定しています。
    """
    rows = []                             # レコードのリスト
    with open(path, encoding='utf-8-sig', newline='') as fp:  # BOMを除去して開く
        reader = csv.DictReader(fp)       # 先頭行を列名として読む
        for row in reader:                # 各データ行について
            parts = []                    # 列テキストの断片
            for key, val in row.items():  # 全列を順に処理
                parts.append(f'{key}: {val}')  # 「列名: 値」形式に整形
            rows.append('\n'.join(parts))      # 1文書へ結合して追加
    return rows                           # 完成した文書リストを返す
