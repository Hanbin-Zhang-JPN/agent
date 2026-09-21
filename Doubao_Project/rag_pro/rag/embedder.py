# -*- coding: utf-8 -*-
"""
向量化器 embedder
=================

作用：把一段文本变成「向量」，供向量检索（vectorstore）使用。

本项目提供两种向量化方式，同一接口、可随时切换：

  1. HashEmbedder（内置，离线可用，零依赖）
     - 原理：基于语料构建词表，用 TF-IDF 权重把文本表示成稀疏向量；
     - 它本质上是一个「带权词袋模型」，无需任何外部服务即可运行；
     - 配合 BM25 的词法检索，离线模式下已具备可用的检索能力。

  2. ApiEmbedder（可选，语义向量）
     - 原理：调用 OpenAI 兼容的 /v1/embeddings 接口（如硅基流动、豆包、
       OpenAI 等），得到真正理解语义的稠密向量；
     - 这是全项目唯一的外部黑盒调用，使用目的与方法在下方注释中写清；
     - 带磁盘缓存，重复文本不重复计费、不重复请求。

  自动选择策略：默认「hash」；若配置了合法 API，则自动使用语义向量。
"""

import hashlib
import json
import os
from collections import Counter

from . import net            # 复用网络请求工具
from .tokenizer import tokenize   # 复用分词器


class BaseEmbedder:
    """向量化器的公共接口（定义子类必须实现的方法）。"""

    name = "base"   # 向量化器名称，用于日志标识

    def embed(self, texts: list) -> list:
        """把一批文本转成向量列表。子类必须实现。"""
        raise NotImplementedError


class HashEmbedder(BaseEmbedder):
    """
    内置哈希向量化器：基于语料的 TF-IDF 稀疏向量。

    流程：
      1. fit(语料)：统计每个词条的「文档频率」，选出词表（默认前 N 高频词）；
      2. embed(文本)：对文本分词，按「词频 × IDF」加权，产出稀疏向量。
    """

    name = "hash"   # 标识名称

    def __init__(self, vocab_size: int = 4096):
        # 词表大小（保留的高频词数量）
        self.vocab_size = vocab_size
        # 词表：词条 -> 词表下标
        self.vocab = {}
        # IDF 权重：词条 -> idf 值
        self.idf = {}
        # 总文档数（用于 IDF）
        self.total_docs = 0
        # 是否已拟合
        self.fitted = False

    def fit(self, docs: list) -> None:
        """
        用一批文档（文本列表）构建词表与 IDF。

        参数:
            docs: 文档文本列表。
        """
        # 记录文档总数
        self.total_docs = len(docs)
        # 文档频率：词条 -> 出现在多少篇文档中
        df = Counter()
        # 遍历每篇文档
        for text in docs:
            # 对本篇文档分词并去重（DF 只计出现与否）
            terms = set(tokenize(text))
            # 累加文档频率
            for t in terms:
                df[t] += 1

        # 按文档频率降序，取前 vocab_size 个词作为词表
        top = [t for t, _ in df.most_common(self.vocab_size)]
        # 为词表分配下标
        self.vocab = {t: i for i, t in enumerate(top)}
        # 计算每个词的 IDF：ln((N+1)/(df+1)) + 1，保证正数
        for t, d in df.items():
            if t in self.vocab:
                self.idf[t] = 1 + os_ln_ratio(d, self.total_docs)
        # 标记已拟合
        self.fitted = True

    def embed(self, texts: list) -> list:
        """
        把一批文本转成稀疏向量（字典 {词表下标: 权重}）。

        参数:
            texts: 文本列表。

        返回:
            向量列表，每个向量是 {下标: TF-IDF 权重}。
        """
        # 未拟合时返回空（调用方会感知到并回退）
        if not self.fitted:
            return []
        # 逐条转换
        out = []
        for text in texts:
            # 统计词频
            tf = Counter(tokenize(text))
            # 构造稀疏向量
            vec = {}
            for t, c in tf.items():
                # 只保留词表中出现的词
                if t in self.vocab:
                    # 权重 = 词频 × IDF
                    vec[self.vocab[t]] = c * self.idf[t]
            # 记录该向量
            out.append(vec)
        return out


def os_ln_ratio(df: int, total: int) -> float:
    """
    计算平滑 IDF：ln((N+1)/(df+1))。

    参数:
        df: 包含该词的文档数。
        total: 总文档数。

    返回:
        IDF 值。
    """
    import math
    return math.log((total + 1) / (df + 1))


class ApiEmbedder(BaseEmbedder):
    """
    语义向量器：调用 OpenAI 兼容的 /v1/embeddings 接口。

    使用目的（为什么需要它）：
      - TF-IDF 与 BM25 只能匹配「字面词」，无法理解「同义词、上下文、语义」；
      - 接入语义向量后，检索能理解「如何缓解幻觉」与「怎么减少编造」
        这类字面不同但语义相同的表达，大幅提升召回质量。

    调用方法（对外部接口的说明）：
      - 请求 POST {base_url}/embeddings
      - 请求体 {"model": model, "input": [文本列表]}
      - 请求头 Authorization: Bearer {api_key}
      - 响应体 data[i].embedding 即第 i 条文本的向量。
      该协议是 OpenAI 的标准协议，几乎所有主流模型服务商都兼容。
    """

    name = "api"   # 标识名称

    def __init__(self, base_url: str, api_key: str, model: str,
                 cache_path: str = ""):
        # API 基础地址（末尾会自动补 /v1/embeddings）
        self.base_url = base_url.rstrip("/")
        # API 密钥
        self.api_key = api_key
        # 模型名（如 text-embedding-v4、text-embedding-3-small 等）
        self.model = model
        # 磁盘缓存路径（存 sha256(文本) -> 向量），可复用省成本
        self.cache_path = cache_path
        # 内存缓存
        self.cache = {}
        # 若给了缓存路径且文件存在，先加载旧缓存
        if cache_path and os.path.exists(cache_path):
            try:
                with open(cache_path, "r", encoding="utf-8") as f:
                    self.cache = json.load(f)
            except Exception:
                # 缓存损坏时忽略，重新构建
                self.cache = {}

    def _embed_one_batch(self, texts: list) -> list:
        """
        调用一次嵌入接口，返回这批文本的向量列表。

        参数:
            texts: 文本列表（单批，长度 ≤ 批量上限）。

        返回:
            向量列表。
        """
        # 拼接嵌入接口的完整地址
        url = self.base_url + "/v1/embeddings"
        # 构造请求头（Bearer 认证 + JSON 类型）
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        # 构造请求体
        payload = {"model": self.model, "input": texts}
        # 发送请求并取回 JSON 响应
        resp = net.post_json(url, headers, payload)
        # 从响应中提取每条向量
        # 注意：响应顺序与请求顺序一致
        out = [item["embedding"] for item in resp["data"]]
        return out

    def embed(self, texts: list) -> list:
        """
        把一批文本转成稠密向量（带缓存与分批）。

        参数:
            texts: 文本列表。

        返回:
            稠密向量列表（每条为 [float, ...]）。

        抛出:
            RuntimeError: API 调用失败时抛出，由上层决定是否回退 hash。
        """
        # 结果收集器
        result = []
        # 待请求的未命中文本与它们在结果中的位置
        pending_idx = []
        pending_texts = []
        # 逐个查缓存
        for i, t in enumerate(texts):
            # 计算文本指纹（sha256）作为缓存键
            key = hashlib.sha256(t.encode("utf-8")).hexdigest()
            if key in self.cache:
                # 命中缓存：直接复用
                result.append(self.cache[key])
            else:
                # 未命中：记入待请求队列
                pending_idx.append(i)
                pending_texts.append(t)
                # 先占位，稍后填充
                result.append(None)

        # 分批请求未命中的文本（控制单次请求体大小）
        batch_size = 32   # 单批最多 32 条
        for s in range(0, len(pending_texts), batch_size):
            # 取出一批
            batch = pending_texts[s:s + batch_size]
            # 调用接口
            vecs = self._embed_one_batch(batch)
            # 把结果写回对应位置，并写入缓存
            for j, v in enumerate(vecs):
                idx = pending_idx[s + j]
                result[idx] = v
                # 同步写入内存缓存
                key = hashlib.sha256(pending_texts[s + j].encode("utf-8")).hexdigest()
                self.cache[key] = v

        # 若配置了缓存路径，把新缓存落盘
        if self.cache_path:
            try:
                # 确保目录存在
                os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
                # 写回磁盘
                with open(self.cache_path, "w", encoding="utf-8") as f:
                    json.dump(self.cache, f, ensure_ascii=False)
            except Exception:
                # 缓存写盘失败不影响主流程
                pass

        # 返回结果（此时不应再有 None）
        return result


def make_embedder(cfg: dict, corpus_docs: list = None) -> BaseEmbedder:
    """
    向量化器工厂：根据配置自动选择 hash 或 api。

    参数:
        cfg: 配置字典，含 embed 子配置。
        corpus_docs: 语料文档列表（仅 hash 模式需要，用于构建词表）。

    返回:
        一个 BaseEmbedder 实例。
    """
    # 读取 embed 子配置
    ecfg = cfg.get("embed", {})
    # 读取向量化模式
    mode = ecfg.get("mode", "auto")
    # auto 模式：看是否配置了合法的 API
    if mode == "auto":
        # 有 base_url + api_key + model 三个字段才算配置完整
        if ecfg.get("base_url") and ecfg.get("api_key") and ecfg.get("model"):
            mode = "api"
        else:
            mode = "hash"

    # 按最终模式创建对应实例
    if mode == "api":
        # 语义向量：需要 URL / 密钥 / 模型 / 缓存路径
        emb = ApiEmbedder(
            base_url=ecfg.get("base_url", ""),
            api_key=ecfg.get("api_key", ""),
            model=ecfg.get("model", ""),
            cache_path=ecfg.get("cache_path", "store/embed_cache.json"),
        )
    else:
        # 内置哈希向量：需要语料来构建词表
        emb = HashEmbedder(vocab_size=ecfg.get("vocab_size", 4096))
        # 用语料拟合词表与 IDF
        if corpus_docs:
            emb.fit(corpus_docs)

    # 返回最终选定的向量化器
    return emb
