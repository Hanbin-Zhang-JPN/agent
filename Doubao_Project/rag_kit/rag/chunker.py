# -*- coding: utf-8 -*-
"""
chunker.py — チャンク分割（外部ライブラリ不要）
================================================================
長い文書を検索単位の「チャンク」へ分割します。
  - 段落（空行区切り）を基本単位にする
  - 目標サイズを超えたらチャンクを確定する
  - 前のチャンク末尾を overlap 分だけ引き継いで文脈の切れ目を防ぐ
  - 見出しは本文にそのまま残しつつ、メタデータとしても記録する
"""

import re  # 見出し行の判定に使用

# Markdown形式の見出し（# の連続）を検出するパターン
_HEADING_RE = re.compile(r'^\s*#{1,6}\s+')
# 日本語の【見出し】形式も検出するパターン
_BRACKET_RE = re.compile(r'^\s*【.+?】')


class Chunk:
    """検索・生成の最小単位となるチャンクを表します。"""
    def __init__(self, text: str, src: str, heading: str = ''):
        self.text = text          # チャンク本文（見出し行も含む）
        self.src = src            # 出典ファイル名
        self.heading = heading    # このチャンクに属する最新見出し
        self.index = -1           # 文書内の通し番号（後で割り当てる）

    def to_dict(self) -> dict:
        """保存用の辞書へ変換します。"""
        return {'text': self.text, 'src': self.src,
                'heading': self.heading, 'index': self.index}


def _is_heading(line: str) -> bool:
    """その行が「見出し行」かどうかを判定します。"""
    return bool(_HEADING_RE.match(line) or _BRACKET_RE.match(line))  # いずれかの形式


def split_paragraphs(text: str) -> list:
    """空行を区切りとして段落リストを作ります。"""
    # 空行（連続改行）で分割し、空白だけの段落は除去する
    return [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]


def _take_tail(paragraphs: list, max_chars: int) -> list:
    """末尾の段落を重複継承分として後ろから取り出します。"""
    out = []                      # 引き継ぐ段落のリスト
    used = 0                      # 累計文字数
    for p in reversed(paragraphs):  # 末尾から逆順に
        if used + len(p) > max_chars and out:  # 上限を超えたら
            break                 # それ以上は取らない
        out.append(p)             # この段落を引き継ぎ対象に
        used += len(p)            # 文字数を加算
    out.reverse()                 # 元の順序へ戻す
    return out                    # 引き継ぎ段落を返す


def _make_chunk(paragraphs: list, heading: str, src: str) -> Chunk:
    """段落リストを1チャンクへ整形します（見出しは本文内に既に存在）。"""
    body = '\n'.join(paragraphs)          # 段落を改行で結合
    return Chunk(body, src, heading)      # 本文と見出しメタデータを持つChunkを生成


def _hard_split(text: str, chunk_size: int, overlap: int) -> list:
    """巨大なテキストを文字単位で強制分割します（最終手段）。"""
    out = []                              # 分割結果
    step = max(chunk_size - overlap, 1)   # 窓の移動幅（重複分を引く）
    for i in range(0, len(text), step):   # 窓をずらしながら
        out.append(text[i:i + chunk_size])  # チャンクを切り出す
    return out                            # 分割結果を返す


def _split_long(text: str, chunk_size: int, overlap: int) -> list:
    """長い1段落を文単位で分割し、必要なら文字単位で強制分割します。"""
    # 文末記号の直後で文に分割する（後読みを使用）
    sentences = [s for s in re.split(r'(?<=[。．！？!?])', text) if s.strip()]
    pieces = []                           # 完成した文のまとまり
    buf = []                              # 組立中の文
    cur = 0                               # 組立中の文字数
    for s in sentences:                   # 各文について
        if cur + len(s) > chunk_size and buf:  # 目標を超え、中身がある場合
            pieces.append(''.join(buf))   # 現在のまとまりを確定
            buf = _take_tail(buf, overlap)  # 末尾を重複分として引き継ぐ
            cur = sum(len(x) for x in buf)  # 引き継いだ文字数へ更新
        buf.append(s)                     # この文を追加
        cur += len(s)                     # 文字数を加算
    if buf:                               # 残った文があれば
        pieces.append(''.join(buf))       # 最後のまとまりを確定
    final = []                            # 最終結果
    for p in pieces:                      # 各まとまりについて
        if len(p) <= chunk_size:          # 目標内なら
            final.append(p)               # そのまま追加
        else:                             # それでも長ければ
            final.extend(_hard_split(p, chunk_size, overlap))  # 文字単位で分割
    return final                          # 最終結果を返す


def chunk_document(text: str, src: str, chunk_size: int = 400,
                   overlap: int = 50) -> list:
    """
    1文書を複数のチャンクへ分割します。
      - chunk_size : 1チャンクの目標文字数
      - overlap    : 前チャンクから引き継ぐ文字数
    """
    paras = split_paragraphs(text)        # 段落へ分割
    # 1段落が大きすぎる場合は文単位で細かく分割してから処理する
    paras = [p for p in paras for p in (_split_long(p, chunk_size, overlap)
                                        if len(p) > chunk_size else [p])]
    chunks = []                           # 完成チャンクのリスト
    buf = []                              # 組立中の段落
    cur = 0                               # 組立中の文字数
    cur_heading = ''                      # 最新の見出し（メタデータ用）
    for p in paras:                       # 各段落について
        if _is_heading(p):                # 見出し行なら
            cur_heading = p               # メタデータ用に記録（本文にも残る）
        if cur + len(p) > chunk_size and buf:  # 目標を超え、中身がある場合
            chunks.append(_make_chunk(buf, cur_heading, src))  # 現在の組立を確定
            buf = _take_tail(buf, overlap)    # 末尾を重複分として引き継ぐ
            cur = sum(len(x) for x in buf)    # 引き継いだ文字数へ更新
        buf.append(p)                         # この段落を追加
        cur += len(p)                         # 文字数を加算
    if buf:                                   # 残った段落があれば
        chunks.append(_make_chunk(buf, cur_heading, src))  # 最後のチャンクを確定
    for i, c in enumerate(chunks):            # 各チャンクに
        c.index = i                           # 通し番号を割り当てる
    return chunks                             # 完成リストを返す
