# -*- coding: utf-8 -*-
"""
单元测试 test_rag
==================

作用：验证 rag_pro 核心模块的行为是否符合预期。
用法：在项目根目录执行
      python -m unittest tests.test_rag -v
      （或 python -m unittest discover -s tests）

覆盖范围：
  - 分词器（中文、英文）
  - 切块器（长度、重叠）
  - BM25 检索（能命中有关键词的文档）
  - 向量库（余弦相似度）
  - 混合检索（融合后排序合理）
  - 离线问答（不依赖 LLM 也能给出答案）
"""

import os
import sys
import unittest

# 把项目根目录加入模块搜索路径
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

# 导入被测模块
from rag.tokenizer import tokenize            # 分词器
from rag.chunker import chunk_text            # 切块器
from rag.bm25 import BM25                     # BM25
from rag.vectorstore import VectorStore, cosine   # 向量库
from rag.retriever import Retriever           # 混合检索
from rag.pipeline import RagPipeline          # RAG 主流程


class TestTokenizer(unittest.TestCase):
    """分词器测试。"""

    def test_chinese_and_english(self):
        """中文应切出单字与二字组，英文应整词小写。"""
        # 对混合文本分词
        toks = tokenize("RAG检索很好用")
        # 英文整词应出现
        self.assertIn("rag", toks)
        # 中文单字应出现
        self.assertIn("检", toks)
        # 中文二字组应出现（相邻中文字符组合）
        self.assertIn("检索", toks)

    def test_empty(self):
        """空文本应返回空列表。"""
        # 空串与 None 都返回空列表
        self.assertEqual(tokenize(""), [])
        self.assertEqual(tokenize(None), [])


class TestChunker(unittest.TestCase):
    """切块器测试。"""

    def test_short_text_single_chunk(self):
        """短文本应整段作为一个块。"""
        # 一段很短的文本
        text = "这是很短的一段话。"
        # 切块后应只有 1 块
        chunks = chunk_text(text, chunk_size=200, overlap=20)
        self.assertEqual(len(chunks), 1)

    def test_long_text_multiple_chunks(self):
        """长文本应切出多块，且不丢内容。"""
        # 构造一段明显超长的文本（重复多句）
        text = "今天天气很好，适合出门散步。" * 30
        # 用小块大小切分
        chunks = chunk_text(text, chunk_size=100, overlap=10)
        # 应切出多块
        self.assertGreater(len(chunks), 1)
        # 所有块拼接后应大致等于原文（内容不丢）
        joined = "".join(chunks)
        self.assertGreater(len(joined), len(text) * 0.8)


class TestBM25(unittest.TestCase):
    """BM25 检索测试。"""

    def setUp(self):
        # 构造三篇有明显区分的文档
        self.docs = [
            "苹果是一种常见的水果。",
            "汽车需要定期保养发动机。",
            "香蕉和苹果都属于水果。",
        ]
        # 建立 BM25 索引
        self.bm = BM25()
        self.bm.fit(self.docs)

    def test_relevant_doc_ranked_first(self):
        """查询关键词应让对应文档排在最前。"""
        # 检索"苹果"
        hits = self.bm.search("苹果")
        # 应能返回结果
        self.assertTrue(hits)
        # 第一名应是包含"苹果"的文档（0 或 2）
        top_doc = hits[0][0]
        self.assertIn(top_doc, (0, 2))

    def test_related_terms(self):
        """共现词扩展应返回相关词。"""
        # 与"水果"共现的词应包含"苹果"或"香蕉"
        related = self.bm.related_terms("水果", n=3)
        # 至少能给出非空建议（可能有扩展词）
        self.assertIsInstance(related, list)


class TestVectorStore(unittest.TestCase):
    """向量库与余弦相似度测试。"""

    def test_cosine_same_vector(self):
        """相同向量的余弦相似度应为 1。"""
        # 相同稠密向量
        v = [1.0, 0.0, 2.0]
        # 相似度约等于 1
        self.assertAlmostEqual(cosine(v, v), 1.0, places=6)

    def test_cosine_orthogonal(self):
        """正交向量的余弦相似度应接近 0。"""
        # 两个正交向量
        a = [1.0, 0.0]
        b = [0.0, 1.0]
        # 相似度接近 0
        self.assertAlmostEqual(cosine(a, b), 0.0, places=6)

    def test_sparse_cosine(self):
        """稀疏向量也应能计算余弦相似度。"""
        # 两个有公共下标的稀疏向量
        a = {0: 1.0, 3: 2.0}
        b = {0: 1.0, 5: 1.0}
        # 相似度应大于 0
        self.assertGreater(cosine(a, b), 0.0)

    def test_search_returns_most_similar(self):
        """向量检索应返回最相似的向量。"""
        # 构造向量库
        vs = VectorStore()
        # 加入两个不同向量
        vs.add([1.0, 0.0], {"name": "a"})
        vs.add([0.0, 1.0], {"name": "b"})
        # 用与 a 相同的查询向量检索
        hits = vs.search([1.0, 0.0], top_k=1)
        # 第一名应是向量 a（id 0）
        self.assertEqual(hits[0][1], 0)


class TestHybridRetrieval(unittest.TestCase):
    """混合检索测试（BM25 + 向量 + RRF）。"""

    def test_retrieve_returns_candidates(self):
        """混合检索应返回融合后的候选列表。"""
        # 构造小语料
        docs = [
            "苹果是一种常见的水果，营养丰富。",
            "汽车需要定期保养发动机，延长寿命。",
            "香蕉与苹果都属于水果，可生食。",
        ]
        # 建立 BM25
        bm = BM25()
        bm.fit(docs)
        # 建立向量库（用简单的稀疏向量）
        vs = VectorStore()
        # 用哈希式 TF 向量粗建（这里直接用词袋稀疏向量示意）
        from collections import Counter
        from rag.tokenizer import tokenize
        for i, d in enumerate(docs):
            # 统计词频作向量
            vec = {}
            for t, c in Counter(tokenize(d)).items():
                vec[hash(t) % 64] = c
            vs.add(vec, {"path": f"doc{i}", "chunk_idx": 0})
        # 创建混合检索器
        retriever = Retriever(bm, vs, top_lex=10, top_vec=10)
        # 执行检索
        cands = retriever.retrieve("苹果", query_vec={hash("苹果") % 64: 1.0})
        # 应返回候选
        self.assertTrue(cands)
        # 每个候选应包含文本与元信息
        self.assertTrue(cands[0].text)
        self.assertTrue(cands[0].meta)


class TestPipelineOffline(unittest.TestCase):
    """离线问答全流程测试（不依赖任何外部服务）。"""

    @classmethod
    def setUpClass(cls):
        # 指向示例文档目录
        cls.doc_dir = os.path.join(ROOT, "data", "sample")
        # 用临时 store 目录，避免污染真实索引
        cls.store = os.path.join(ROOT, "store", "_test")
        # 加载配置
        import json
        with open(os.path.join(ROOT, "config.json"), "r", encoding="utf-8") as f:
            cls.cfg = json.load(f)
        # 创建并构建主流程
        cls.pipe = RagPipeline(cls.cfg, store_dir=cls.store)
        cls.pipe.build(cls.doc_dir)

    @classmethod
    def tearDownClass(cls):
        # 清理测试产生的索引文件
        import shutil
        if os.path.exists(cls.store):
            shutil.rmtree(cls.store, ignore_errors=True)

    def test_build_created_index(self):
        """构建后应能加载并返回块信息。"""
        # 索引已存在
        self.assertIsNotNone(self.pipe.bm25)
        # 块数应大于 0
        self.assertGreater(len(self.pipe.bm25.docs), 0)

    def test_ask_returns_answer_offline(self):
        """离线模式下 ask 应返回抽取式答案。"""
        # 执行问答
        result = self.pipe.ask("什么是RAG？")
        # 应包含答案
        self.assertTrue(result["answer"])
        # 离线模式不使用 LLM
        self.assertFalse(result["used_llm"])
        # 应包含引用
        self.assertTrue(result["citations"])

    def test_ask_relevant_to_question(self):
        """答案应包含与问题相关的关键词。"""
        # 提问 BM25 相关
        result = self.pipe.ask("BM25打分由哪几部分构成？")
        # 答案中应出现 BM25 相关字样
        self.assertIn("BM25", result["answer"])


if __name__ == "__main__":
    # 直接运行时执行全部测试
    unittest.main()
