# -*- coding: utf-8 -*-
"""
pipeline.py — RAG パイプライン統合（外部ライブラリ不要）
================================================================
「文書登録 → チャンク分割 → 索引構築 → ハイブリッド検索 →
再ランキング → 回答生成」までを1つのクラスに束ねます。
利用者は RagPipeline を build() して ask() するだけで
一連のRAG動作を実行できます。
"""

import os        # 保存先ディレクトリの作成に使用
import json      # メタ情報の保存に使用

from . import tokenizer  # トークナイザー
from . import loader     # ドキュメント読み込み
from . import chunker    # チャンク分割
from . import vectors    # ベクトル計算
from . import generator  # 回答生成
from .index import Bm25Index, Corpus   # 索引とコーパス
from .retriever import HybridRetriever # ハイブリッド検索
from .reranker import Reranker         # 再ランキング


class RagPipeline:
    """
    RAG の一連の処理を束ねるメインクラス。
    パラメータは全てこのクラスで一括管理します。
    """
    def __init__(self, chunk_size: int = 400, overlap: int = 50,
                 dim: int = 4096, k1: float = 1.5, b: float = 0.75):
        self.chunk_size = chunk_size  # 1チャンクの目標文字数
        self.overlap = overlap        # チャンク間の重複文字数
        self.dim = dim                # ベクトルの次元数
        self.k1 = k1                  # BM25 の飽和度パラメータ
        self.b = b                    # BM25 の長さ正規化パラメータ
        self.bm25 = Bm25Index(k1, b)  # BM25 索引を生成
        self.vectorizer = vectors.TfidfVectorizer(dim)  # ベクトル化器
        self.corpus = Corpus()        # チャンクストア
        self.doc_vectors = []         # 正規化済み文書ベクトル
        self.doc_tokens = []          # 文書ごとの語彙トークン
        self._built = False           # 索引構築済みフラグ

    # ------------------------------------------------------------------
    # 索引の構築
    # ------------------------------------------------------------------
    def _add_chunk(self, c: chunker.Chunk) -> None:
        """1チャンクを索引とコーパスへ登録します。"""
        doc_id = len(self.corpus)     # 新チャンクのID（通し番号）
        self.corpus.add(c.text, c.src, c.heading, c.index)  # 本文を保存
        tokens = tokenizer.bm25_tokens(c.text)  # 語彙トークンを作る
        feats = tokenizer.vector_features(c.text)  # n-gram特徴量を作る
        self.bm25.add(doc_id, tokens)   # BM25 索引へ登録
        self.doc_tokens.append(tokens)  # トークンを保存（再ランク用）
        vec = self.vectorizer.transform(feats)  # TF-IDFベクトル化
        self.doc_vectors.append(vectors.normalize(vec))  # 正規化して保存

    def build_texts(self, docs: list, out_dir: str = None) -> int:
        """
        テキストリスト [(出典名, 本文), ...] から索引を構築します。
        out_dir 指定時は結果を保存します。チャンク総数を返します。
        """
        self.bm25 = Bm25Index(self.k1, self.b)  # 索引を初期化
        self.vectorizer = vectors.TfidfVectorizer(self.dim)  # ベクトル化器を初期化
        self.corpus = Corpus()        # コーパスを初期化
        self.doc_vectors = []         # ベクトルを初期化
        self.doc_tokens = []          # トークンを初期化
        chunks = []                   # 全チャンクの一時リスト
        for src, text in docs:        # 各文書について
            chunks.extend(chunker.chunk_document(text, src, self.chunk_size, self.overlap))  # 分割
        # ベクトル化に必要な文書頻度を先に集計する
        all_feats = [tokenizer.vector_features(c.text) for c in chunks]  # 全特徴量
        self.vectorizer.fit(all_feats)  # IDF 用の頻度を学習
        for c in chunks:              # 各チャンクを登録
            self._add_chunk(c)        # 索引とコーパスへ追加
        self._built = True            # 構築完了フラグ
        if out_dir:                   # 保存先があれば
            self.save(out_dir)        # 結果を保存
        return len(self.corpus)       # チャンク総数を返す

    def build_dir(self, data_dir: str, out_dir: str = None) -> int:
        """ディレクトリ内の文書から索引を構築します。"""
        docs = loader.load_directory(data_dir)  # 文書を読み込む
        return self.build_texts(docs, out_dir)  # 索引を構築

    # ------------------------------------------------------------------
    # 保存と復元
    # ------------------------------------------------------------------
    def save(self, out_dir: str) -> None:
        """索引とコーパスを out_dir へ保存します。"""
        os.makedirs(out_dir, exist_ok=True)  # 保存先を作成
        self.bm25.save(os.path.join(out_dir, 'bm25.json'))  # BM25保存
        self.corpus.save(os.path.join(out_dir, 'corpus.json'))  # コーパス保存
        self.vectorizer.save(os.path.join(out_dir, 'vectorizer.json'))  # ベクトル化器保存
        meta = {'chunk_size': self.chunk_size, 'overlap': self.overlap,  # 設定
                'dim': self.dim, 'k1': self.k1, 'b': self.b,  # 設定
                'n_chunks': len(self.corpus)}  # チャンク数
        with open(os.path.join(out_dir, 'meta.json'), 'w', encoding='utf-8') as fp:  # 開く
            json.dump(meta, fp, ensure_ascii=False)  # メタ情報を保存

    def load(self, out_dir: str) -> 'RagPipeline':
        """保存済みの索引を読み込んで復元します。"""
        self.bm25 = Bm25Index.load(os.path.join(out_dir, 'bm25.json'))  # BM25復元
        self.corpus = Corpus.load(os.path.join(out_dir, 'corpus.json'))  # コーパス復元
        self.vectorizer = vectors.TfidfVectorizer.load(os.path.join(out_dir, 'vectorizer.json'))  # 復元
        # ベクトルとトークンは本文から再計算する（軽量・確定的）
        self.doc_vectors = []         # ベクトルを初期化
        self.doc_tokens = []          # トークンを初期化
        for rec in self.corpus.records:  # 各チャンクについて
            feats = tokenizer.vector_features(rec['text'])  # 特徴量
            vec = self.vectorizer.transform(feats)  # TF-IDFベクトル化
            self.doc_vectors.append(vectors.normalize(vec))  # 正規化して保存
            self.doc_tokens.append(tokenizer.bm25_tokens(rec['text']))  # トークン保存
        self._built = True            # 構築済みフラグを立てる
        return self                   # 自身を返す

    # ------------------------------------------------------------------
    # 質問応答
    # ------------------------------------------------------------------
    def ask(self, question: str, top_k: int = 5, mmr_lambda: float = 0.0,
            use_llm: bool = False) -> dict:
        """
        質問に対して回答を生成します。
          - top_k      : 検索で使う上位件数
          - mmr_lambda : 0より大きいと多様化
          - use_llm    : True でLLM型回答（環境変数必要）
        戻り値は {'question', 'answer', 'sources', 'mode'} です。
        """
        if not self._built:           # 索引が未構築なら
            raise RuntimeError('索引が未構築です。先に build_dir() を実行してください。')  # 通知
        retriever = HybridRetriever(self.bm25, self.vectorizer,  # 検索器を生成
                                    self.doc_vectors, self.doc_tokens)  # データを渡す
        hits = retriever.search(question, top_k=top_k * 3, mmr_lambda=mmr_lambda)  # 多めに取得
        reranker = Reranker(self.doc_tokens, self.corpus.records)  # 再ランカを生成
        hits = reranker.rerank(hits, question, top_k)  # 再ランキング
        contexts = generator.build_contexts(hits, self.corpus)  # コンテキスト整形
        if use_llm:                   # LLM型の場合
            gen = generator.LlmGenerator.from_env()  # 環境変数から生成器を作る
            answer = gen.generate(question, contexts)  # LLMで回答
            mode = 'llm'              # モード名を記録
            sources = [{'doc_id': i, 'src': self.corpus.records[i]['src'],  # 出典
                        'heading': self.corpus.records[i]['heading'],  # 見出し
                        'score': s} for i, s in hits]  # スコア
        else:                         # 抽出型の場合
            result = generator.extract_answer(question, hits, self.corpus)  # 抽出回答
            answer, sources, mode = result['answer'], result['sources'], result['mode']  # 分解
        return {'question': question, 'answer': answer,  # 質問と回答
                'sources': sources, 'mode': mode}  # 出典とモード

    def stats(self) -> dict:
        """索引の統計情報を返します。"""
        return {'n_chunks': len(self.corpus), 'n_terms': len(self.bm25.postings),  # 数
                'n_docs_src': len({r['src'] for r in self.corpus.records})}  # 出典数
