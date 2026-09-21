# -*- coding: utf-8 -*-
"""
generator.py — 回答生成（外部ライブラリ不要）
================================================================
検索で得たチャンクを「根拠付き回答」へ変換します。
  1. 抽出型（既定）: LLMを使わず、最適チャンクの要点を引用して回答
  2. LLM型（任意） : OpenAI 互換API へ HTTP で問い合わせて回答
LLM型はブラックボックス依存ではなく、標準ライブラリ urllib のみで
外部APIと通信する「明確に説明できる接続」です。未設定なら抽出型へ
自動フォールバックするため、ネットワーク不要でも動作します。
"""

import json      # JSONエンコード・デコードに使用
import urllib.request  # HTTP POST に使用（標準ライブラリ）
import urllib.error    # HTTP エラー処理に使用

from . import tokenizer  # トークナイザー（同一パッケージ内）
from .index import Corpus  # コーパス（同一パッケージ内）

# 抽出型回答のスニペット最大文字数
_SNIPPET_MAX = 220


def _cut_sentence(text: str, limit: int) -> str:
    """なるべく文の区切りで切り詰めたスニペットを作ります。"""
    text = ' '.join(text.split())     # 余分な空白を1つに圧縮
    if len(text) <= limit:            # 既に短ければ
        return text                   # そのまま返す
    cut = text[:limit]                # 上限まで切り出す
    for mark in ('。', '．', '.', '!', '？'):  # 文末記号を探す
        idx = cut.rfind(mark)         # 最後の文末記号の位置
        if idx > limit * 0.5:         # 途中過ぎない位置なら
            return cut[:idx + 1]      # 文の区切りまでで返す
    return cut + '…'                  # 見つからなければ省略記号を付ける


def build_contexts(hits: list, corpus: Corpus, max_chars: int = 1500) -> list:
    """
    ヒット文書を「引用番号付きのコンテキスト」へ整形します。
    LLMへ渡す際に根拠を明確化するための形式です。
    """
    contexts = []                     # コンテキストのリスト
    used = 0                          # 使用済み文字数
    for n, (doc_id, _score) in enumerate(hits, start=1):  # 番号付きで走査
        rec = corpus.records[doc_id]  # チャンク情報を取得
        if used + len(rec['text']) > max_chars and contexts:  # 上限超過なら
            break                     # これ以上は足さない
        head = f'[{n}] 出典: {rec["src"]}'  # 引用ヘッダを作る
        if rec['heading']:            # 見出しがあれば
            head += f' / 見出し: {rec["heading"]}'  # ヘッダへ追記
        contexts.append(f'{head}\n{rec["text"]}')  # ヘッダ+本文を追加
        used += len(rec['text'])      # 文字数を加算
    return contexts                   # 完成リストを返す


def _pick_snippet(query: str, text: str) -> str:
    """質問語との重なりが大きい区間を優先して要点文を抜き出します。"""
    q_words = set(tokenizer.bm25_tokens(query))  # 質問の語集合
    sentences = [s for s in text.replace('\n', '。').split('。') if s.strip()]  # 文分割
    if not sentences:                 # 文が無ければ
        return _cut_sentence(text, _SNIPPET_MAX)  # 先頭を切り詰めて返す
    # 各文の質問語ヒット数を数えて最良の文を選ぶ
    best = max(sentences, key=lambda s: len(q_words & set(tokenizer.bm25_tokens(s))))
    # 周辺文も少し含めて自然な回答にする
    idx = sentences.index(best)       # 最良文の位置
    around = sentences[max(0, idx - 1): idx + 2]  # 前後1文ずつ
    return _cut_sentence('。'.join(around), _SNIPPET_MAX)  # 切り詰めて返す


def extract_answer(question: str, hits: list, corpus: Corpus) -> dict:
    """
    LLM不要の抽出型回答を生成します。
    戻り値: {'answer': 回答文, 'sources': [出典一覧], 'mode': 'extractive'}
    """
    sources = []                      # 出典一覧
    if not hits:                      # 該当文書が無ければ
        return {'answer': '該当する情報が見つかりませんでした。',  # 回答文
                'sources': sources, 'mode': 'extractive'}  # 空の出典
    top_id = hits[0][0]               # 最上位チャンク
    top = corpus.records[top_id]      # その情報を取得
    snippet = _pick_snippet(question, top['text'])  # 要点文を抜き出す
    # 回答文：根拠の提示と引用で構成する
    answer = (f'【抽出回答】\n{question}\n'
              f'根拠: {snippet}\n'
              f'（出典: {top["src"]}）')  # 回答文を組み立て
    for doc_id, score in hits[:3]:    # 上位3件の出典を記録
        rec = corpus.records[doc_id]  # チャンク情報を取得
        sources.append({'doc_id': doc_id, 'src': rec['src'],  # 出典ファイル
                        'heading': rec['heading'], 'score': round(score, 4),  # スコア
                        'snippet': _cut_sentence(rec['text'], 160)})  # 抜粋
    return {'answer': answer, 'sources': sources, 'mode': 'extractive'}  # 結果


# LLM型のシステムプロンプト（日本語で根拠を限定する）
_LLM_SYSTEM = (
    'あなたは検索結果に基づいて回答するRAGアシスタントです。\n'
    '参照情報のみを根拠にし、必ず引用番号 [1][2] を付けて答えてください。\n'
    '参照情報に無いことは「参照情報からは不明」と明記してください。'
)


class LlmGenerator:
    """
    OpenAI 互換 API を使う生成器（任意・外部通信）。
      - base_url : API のベースURL（例: https://api.openai.com/v1）
      - api_key  : API キー
      - model    : モデル名
    通信は標準ライブラリ urllib のみで行い、依存パッケージは追加しません。
    """
    def __init__(self, base_url: str, api_key: str, model: str, timeout: int = 60):
        self.base_url = base_url.rstrip('/')  # 末尾のスラッシュを除去
        self.api_key = api_key        # 認証キー
        self.model = model            # モデル名
        self.timeout = timeout        # 通信タイムアウト（秒）

    @classmethod
    def from_env(cls) -> 'LlmGenerator':
        """環境変数から生成器を作ります（無ければ分かりやすく例外）。"""
        import os                     # 環境変数の取得用
        try:                          # 環境変数を読み取る
            url = os.environ['RAG_LLM_URL']  # ベースURL
            key = os.environ['RAG_LLM_KEY']  # APIキー
        except KeyError as e:         # 未設定の変数があれば
            raise RuntimeError(       # 設定方法を明示したエラーを投げる
                f'LLM利用には環境変数 {e} が必要です。'
                'RAG_LLM_URL / RAG_LLM_KEY を設定してください。') from e
        return cls(url, key, os.environ.get('RAG_LLM_MODEL', 'gpt-4o-mini'))  # 生成器

    def _build_payload(self, question: str, contexts: list) -> dict:
        """APIへ送るリクエスト本文を作ります。"""
        user = '【質問】\n' + question + '\n\n【参照情報】\n' + '\n\n'.join(contexts)  # 本文
        return {                      # リクエスト内容
            'model': self.model,      # モデル指定
            'messages': [             # メッセージ列
                {'role': 'system', 'content': _LLM_SYSTEM},  # システム指示
                {'role': 'user', 'content': user},           # ユーザー質問
            ],
            'temperature': 0.3,       # 決定論的な回答を優先
        }

    def generate(self, question: str, contexts: list) -> str:
        """LLM を呼び出して回答文字列を取得します。"""
        payload = self._build_payload(question, contexts)  # 本文を作る
        body = json.dumps(payload).encode('utf-8')         # JSONへ変換
        req = urllib.request.Request(  # リクエストを作成
            f'{self.base_url}/chat/completions',  # エンドポイントURL
            data=body,                # 送信ボディ
            headers={'Content-Type': 'application/json',  # コンテンツ種別
                     'Authorization': f'Bearer {self.api_key}'},  # 認証ヘッダ
            method='POST')            # POST メソッド
        try:                          # 通信を実行
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:  # 送信
                data = json.loads(resp.read().decode('utf-8'))  # 応答をJSON化
        except urllib.error.HTTPError as e:  # HTTPエラー時は
            raise RuntimeError(f'LLM API エラー: {e.code} {e.reason}') from e  # 通知
        return data['choices'][0]['message']['content']  # 回答文を返す
