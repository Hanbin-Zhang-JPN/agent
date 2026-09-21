# -*- coding: utf-8 -*-
"""
RAG 主流程 pipeline
====================

作用：把「入库 → 检索 → 重排 → 组装 → 生成」串成一条完整流水线，
     对外只暴露一个简单的 ask() 接口。

一条完整 RAG 问答链路（本类实现）：
  1. 查询处理（可选改写 + 语料扩展）；
  2. 混合检索（BM25 + 向量 + RRF 融合）；
  3. 重排（多信号打分 + 可选 MMR 去重）；
  4. 上下文组装（去重 + token 预算 + 引用编号）；
  5. 答案生成（离线抽取 或 大模型生成）。

支持两种工作方式：
  - 先 build() 构建索引，再 ask() 问答（推荐）；
  - 或 load() 直接加载已构建的索引（跳过入库）。
"""

import json
import os
import time

from .bm25 import BM25              # BM25 索引
from .vectorstore import VectorStore  # 向量库
from .retriever import Retriever     # 混合检索器
from .reranker import Reranker       # 重排器
from .context import assemble_context  # 上下文组装
from .generator import Generator     # 答案生成器
from .llm import LLMClient           # 大模型客户端
from .query import process_query     # 查询处理
from . import ingest                 # 入库管线


class RagPipeline:
    """RAG 问答主流程：构建/加载索引 + 问答。"""

    def __init__(self, cfg: dict, store_dir: str = "store"):
        """
        参数:
            cfg:      全局配置字典（含检索、生成等参数）。
            store_dir: 索引存放目录。
        """
        # 保存配置
        self.cfg = cfg
        # 保存索引目录
        self.store_dir = store_dir
        # 后续各组件初始化
        self.bm25 = None        # BM25 索引
        self.vs = None          # 向量库
        self.retriever = None   # 检索器
        self.reranker = None    # 重排器
        self.generator = None   # 生成器
        self.llm = None         # 大模型客户端
        self.embedder = None    # 向量化器

    # ---------- 索引构建 / 加载 ----------

    def build(self, doc_dir: str) -> dict:
        """
        从文档目录构建索引（会重建 store 目录中的索引文件）。

        参数:
            doc_dir: 文档目录路径。

        返回:
            构建汇总信息（来自 ingest.build_index）。
        """
        # 调用入库管线构建索引
        summary = ingest.build_index(doc_dir, self.cfg, self.store_dir)
        # 构建完成后初始化各组件
        self._load_components()
        # 返回汇总
        return summary

    def load(self) -> bool:
        """
        从 store 目录加载已构建的索引。

        返回:
            True 表示加载成功；False 表示索引不存在或损坏。
        """
        # 检查索引文件是否齐全
        if not os.path.exists(os.path.join(self.store_dir, "bm25.json")):
            return False
        # 初始化各组件
        self._load_components()
        # 返回加载成功
        return True

    def _load_components(self) -> None:
        """
        从磁盘加载索引并初始化检索/重排/生成组件（内部方法）。
        """
        # 加载 BM25 索引
        self.bm25 = BM25()
        self.bm25.load(os.path.join(self.store_dir, "bm25.json"))
        # 加载向量库
        self.vs = VectorStore()
        self.vs.load(os.path.join(self.store_dir, "vectors.json"))

        # 读取检索相关配置
        rcfg = self.cfg.get("retrieval", {})
        # 创建混合检索器
        self.retriever = Retriever(
            self.bm25,                                  # BM25 索引
            self.vs,                                    # 向量库
            top_lex=rcfg.get("top_lex", 20),            # BM25 粗召回数
            top_vec=rcfg.get("top_vec", 20),            # 向量粗召回数
            rrf_k=rcfg.get("rrf_k", 60),                # RRF 常数
        )
        # 读取重排配置
        rrcfg = self.cfg.get("rerank", {})
        # 创建重排器
        self.reranker = Reranker(
            w_lex=rrcfg.get("w_lex", 0.35),             # BM25 权重
            w_vec=rrcfg.get("w_vec", 0.35),             # 向量权重
            w_pos=rrcfg.get("w_pos", 0.10),             # 位置权重
            w_exact=rrcfg.get("w_exact", 0.20),         # 精确词权重
            use_mmr=rrcfg.get("use_mmr", True),         # 是否 MMR
            mmr_lambda=rrcfg.get("mmr_lambda", 0.7),    # MMR 参数
        )

        # 创建大模型客户端（若配置完整）
        lcfg = self.cfg.get("llm", {})
        if lcfg.get("base_url") and lcfg.get("api_key") and lcfg.get("model"):
            # 配置完整才创建客户端
            self.llm = LLMClient(
                base_url=lcfg["base_url"],   # 接口地址
                api_key=lcfg["api_key"],     # 密钥
                model=lcfg["model"],         # 模型名
                temperature=lcfg.get("temperature", 0.3),
            )
        else:
            # 未配置则置空（生成器会自动走离线抽取式）
            self.llm = None

        # 创建答案生成器
        self.generator = Generator(self.cfg, self.llm,
                                   mode=self.cfg.get("gen_mode", "auto"))

    # ---------- 问答主流程 ----------

    def ask(self, question: str, top_n: int = 5, verbose: bool = False) -> dict:
        """
        执行一次完整的 RAG 问答。

        参数:
            question: 用户问题。
            top_n:    重排后保留并送入上下文的块数。
            verbose:  是否把中间检索信息也放进结果（便于调试）。

        返回:
            字典，包含：
              question   问题原文
              answer     答案文本
              used_llm   是否使用了 LLM
              citations  引用列表（来源文件）
              chunks     使用的块（含分数，便于追溯）
              time_ms    耗时（毫秒）
        """
        # 记录开始时间，用于统计耗时
        t0 = time.time()
        # 索引未就绪时的提示
        if self.bm25 is None:
            return {"question": question,
                    "answer": "索引尚未构建，请先执行 build() 或 load()。",
                    "used_llm": False, "citations": [], "chunks": [],
                    "time_ms": 0}

        # ---------- 1. 查询处理 ----------
        # 生成最终检索用查询（改写 + 扩展）
        final_q = process_query(question, self.bm25, self.llm)

        # ---------- 2. 混合检索 ----------
        # 计算查询向量（供向量路使用）
        qvec = None
        if self.embedder is not None:
            # 用向量化器生成查询向量（失败则跳过向量路）
            try:
                qvec = self.embedder.embed([final_q])[0]
            except Exception:
                qvec = None
        # 执行混合检索
        candidates = self.retriever.retrieve(final_q, query_vec=qvec)

        # ---------- 3. 重排 ----------
        # 对候选做精细排序，取前 top_n
        ranked = self.reranker.rerank(final_q, candidates, top_n=top_n)

        # ---------- 4. 上下文组装 ----------
        # 读取上下文 token 预算
        max_tokens = self.cfg.get("context", {}).get("max_tokens", 1800)
        # 组装上下文与选用列表
        context, used = assemble_context(ranked, max_tokens=max_tokens,
                                         top_n=top_n)

        # ---------- 5. 答案生成 ----------
        # 生成答案（自动选择抽取式 / LLM 生成式）
        answer, used_llm = self.generator.generate(question, context, used)

        # 计算总耗时
        cost_ms = int((time.time() - t0) * 1000)

        # 组装引用（去重、保持顺序，便于展示）与块信息（保留每块明细）
        seen_src = set()
        citations = []
        for c in used:
            src = c.meta.get("path", "")
            # 同一来源只列一次
            if src and src not in seen_src:
                citations.append(src)
                seen_src.add(src)
        chunk_info = [
            {"text": c.text[:120] + ("…" if len(c.text) > 120 else ""),
             "score": round(c.score, 4),
             "source": c.meta.get("path", "")}
            for c in used
        ]

        # 返回完整结果
        result = {
            "question": question,      # 问题原文
            "answer": answer,          # 答案
            "used_llm": used_llm,      # 是否用 LLM
            "citations": citations,    # 引用文件
            "chunks": chunk_info,      # 使用的块摘要
            "time_ms": cost_ms,        # 耗时
        }
        # verbose 模式下追加中间检索信息
        if verbose:
            result["final_query"] = final_q                 # 检索用查询
            result["num_candidates"] = len(candidates)      # 粗召回数
        # 返回结果
        return result
