# -*- coding: utf-8 -*-
"""
文档入库管线 ingest
====================

作用：把一批本地文档变成可检索的索引（BM25 索引 + 向量库）。

入库流程：
  1. 发现文件：递归扫描目录，按扩展名过滤；
  2. 读取文本：调用 reader.read_document；
  3. 切块：调用 chunker.chunk_document；
  4. 分词建索引：全部块喂给 BM25.fit；
  5. 向量化：块文本交给 embedder；
  6. 入库向量库：向量与元信息写入 VectorStore；
  7. 持久化：BM25 索引、向量库、文档清单分别存盘。

支持并行：读取/切块阶段用线程池并行，文档多时明显提速。
"""

import json
import os
from concurrent.futures import ThreadPoolExecutor

from . import reader          # 文档读取
from .chunker import chunk_document   # 切块
from .bm25 import BM25        # BM25 索引
from .vectorstore import VectorStore  # 向量库
from .embedder import make_embedder   # 向量化器工厂


def _discover_files(directory: str) -> list:
    """
    递归扫描目录，返回所有受支持格式的文件路径（已排序，保证稳定）。

    参数:
        directory: 要扫描的目录。

    返回:
        文件路径列表。
    """
    # 收集到的文件
    found = []
    # 用 os.walk 递归遍历目录
    for root, _, files in os.walk(directory):
        # 遍历当前目录下的每个文件
        for name in files:
            # 取扩展名
            ext = os.path.splitext(name)[1].lower()
            # 只保留受支持的格式
            if ext in reader.SUPPORTED_EXTS:
                # 拼接完整路径并记录
                found.append(os.path.join(root, name))
    # 排序保证多次构建结果一致
    return sorted(found)


def _load_one(path: str) -> tuple:
    """
    读取单个文件并切成块（供线程池并行调用）。

    参数:
        path: 文件路径。

    返回:
        (path, [块文本...])；失败时返回 (path, [])。
    """
    try:
        # 读取文档全文
        text = reader.read_document(path)
        # 切块（参数在下方配置中可调）
        chunks = chunk_document(text, chunk_size=400, overlap=60)
        # 返回路径与块列表
        return path, chunks
    except Exception as e:
        # 单文件失败不中断整体入库，打印警告后跳过
        print(f"[ingest] 跳过文件 {path}：{e}")
        return path, []


def build_index(directory: str, cfg: dict, store_dir: str = "store"):
    """
    构建（或重建）整个索引，并保存到 store 目录。

    参数:
        directory: 文档目录。
        cfg:       全局配置字典。
        store_dir: 索引输出目录。

    返回:
        dict 汇总信息（文档数、块数、向量化器名称等）。
    """
    # ---------- 1. 发现文件 ----------
    files = _discover_files(directory)
    print(f"[ingest] 发现 {len(files)} 个文档")

    # ---------- 2-3. 并行读取并切块 ----------
    all_chunks = []   # 所有块文本（顺序与 doc_id 对应）
    metas = []        # 每个块对应的元信息
    # 用线程池并行处理（最多 8 个线程）
    with ThreadPoolExecutor(max_workers=8) as pool:
        # 提交所有文件任务并收集结果
        results = list(pool.map(_load_one, files))
    # 按顺序整理：块文本 + 元信息
    for path, chunks in results:
        # 跳过没有内容的文件
        if not chunks:
            continue
        # 逐个块记录元信息（来源路径 + 块号）
        for idx, c in enumerate(chunks):
            metas.append({"path": path, "chunk_idx": idx, "doc_id": len(all_chunks)})
            all_chunks.append(c)
    print(f"[ingest] 共生成 {len(all_chunks)} 个文本块")

    # 没有内容时给出明确提示
    if not all_chunks:
        print("[ingest] 警告：没有生成任何块，请检查文档格式与内容。")

    # ---------- 4. 建立 BM25 索引 ----------
    bm25 = BM25()          # 新建 BM25 实例
    bm25.fit(all_chunks)   # 用全部块拟合

    # ---------- 5. 向量化 ----------
    # 创建向量化器（auto：有 API 用语义向量，否则用内置哈希向量）
    embedder = make_embedder(cfg, corpus_docs=all_chunks)
    # 对全部块生成向量
    vectors = embedder.embed(all_chunks)

    # ---------- 6. 写入向量库 ----------
    vs = VectorStore()     # 新建向量库
    # 依次加入每个向量与元信息
    for v, m in zip(vectors, metas):
        vs.add(v, m)
    # 若向量化失败（向量为空），给出提示
    if len(vs) == 0:
        print("[ingest] 警告：向量库为空（向量化可能失败）。")

    # ---------- 7. 持久化 ----------
    # 确保输出目录存在
    os.makedirs(store_dir, exist_ok=True)
    # 保存 BM25 索引
    bm25.save(os.path.join(store_dir, "bm25.json"))
    # 保存向量库
    vs.save(os.path.join(store_dir, "vectors.json"))
    # 保存文档清单与元信息
    with open(os.path.join(store_dir, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump({"files": files, "num_docs": len(all_chunks),
                   "embedder": embedder.name}, f, ensure_ascii=False)

    # 返回构建汇总
    return {
        "files": len(files),          # 文件数
        "chunks": len(all_chunks),    # 块数
        "embedder": embedder.name,    # 使用的向量化器
    }
