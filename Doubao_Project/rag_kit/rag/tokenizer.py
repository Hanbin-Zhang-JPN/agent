# -*- coding: utf-8 -*-
"""
tokenizer.py — 白箱トークナイザー（外部ライブラリ不要）
================================================================
日本語・中国語などのCJK文字と英数字を、2種類の粒度で分解します。
  - BM25用トークン    : 語彙の「完全一致」検索に使う単位
  - n-gram特徴量      : ベクトル類似度（あいまい検索）に使う単位
依存ライブラリは一切使わず、正規表現のみで実装しています。
"""

import re  # 文字種の判定と切り出しに使用

# ------------------------------------------------------------------
# 文字種パターン（コンパイル済みで高速化）
# ------------------------------------------------------------------
# CJK（漢字・ひらがな・カタカナ・ハングル）を1文字ずつトークン化するための範囲
_CJK = re.compile(r'[\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af]')
# 英数字の連続（単語）を1トークン化するためのパターン
_WORD = re.compile(r'[a-zA-Z0-9]+')


def normalize(text: str) -> str:
    """入力文字列を小文字化し、前後の空白を除きます。"""
    return text.strip().lower()  # 大文字小文字の揺れを吸収して検索精度を安定させる


def bm25_tokens(text: str) -> list:
    """
    BM25用の語彙トークン列を作ります。
    CJK文字は1文字=1トークン、英数字は単語単位=1トークンです。
    """
    text = normalize(text)     # まず正規化する
    tokens = []                # 結果のトークン列
    word = []                  # 英数字をためる一時バッファ
    for ch in text:            # 1文字ずつ順に判定
        if _CJK.match(ch):     # CJK文字なら
            if word:           # 英数字の途中だった場合
                tokens.append(''.join(word))  # ためた英単語を先に出力
                word = []      # バッファを空にする
            tokens.append(ch)  # CJKは1文字をそのままトークン化
        elif _WORD.match(ch):  # 英数字なら
            word.append(ch)    # バッファへ貯めておく
        else:                  # 記号・空白など区切り文字なら
            if word:           # 英単語が溜まっていれば
                tokens.append(''.join(word))  # 単語として出力
                word = []      # バッファを空にする
    if word:                   # 末尾に残った英単語を
        tokens.append(''.join(word))  # 出力する
    return tokens              # 完成したトークン列を返す


def _ngrams(text: str, n: int) -> list:
    """文字列をn-gram（連続n文字）のリストに分解します。"""
    if len(text) < n:              # 短すぎてn文字未満なら
        return [text]              # そのまま1つの特徴として返す
    return [text[i:i + n] for i in range(len(text) - n + 1)]  # 窓をずらして切り出す


def vector_features(text: str, n: int = 2) -> list:
    """
    ベクトル化用の特徴量リストを作ります。
    CJKの連続部分はn-gram、英数字は単語単位にします。
    n=2 のbi-gramが日本語で実用的な精度を出しやすい既定値です。
    """
    text = normalize(text)     # まず正規化する
    feats = []                 # 結果の特徴量リスト
    cjk = []                   # CJKの連続をためるバッファ
    word = []                  # 英数字をためるバッファ
    for ch in text:            # 1文字ずつ走査
        if _CJK.match(ch):     # CJK文字なら
            if word:           # 英単語の途中だった場合
                feats.append(''.join(word))  # 英単語を先に出力
                word = []      # バッファを空にする
            cjk.append(ch)     # CJKは列に追加
        elif _WORD.match(ch):  # 英数字なら
            if cjk:            # CJK列が溜まっていたら
                feats.extend(_ngrams(''.join(cjk), n))  # n-gram化して出力
                cjk = []       # バッファを空にする
            word.append(ch)    # 英数字はバッファへ
        else:                  # 区切り文字なら
            if cjk:            # CJK列が溜まっていたら
                feats.extend(_ngrams(''.join(cjk), n))  # n-gram化して出力
                cjk = []       # バッファを空にする
            if word:           # 英単語が溜まっていたら
                feats.append(''.join(word))  # 単語として出力
                word = []      # バッファを空にする
    if cjk:                    # 末尾に残ったCJK列を
        feats.extend(_ngrams(''.join(cjk), n))  # n-gram化して出力
    if word:                   # 末尾に残った英単語を
        feats.append(''.join(word))  # 出力する
    return feats               # 完成した特徴量列を返す
