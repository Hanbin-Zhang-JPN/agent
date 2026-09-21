# ============================================================
# RAG 主流程：把"建库 → 检索 → 重排 → 组提示 → 生成"串成一条线
#
# 对外只暴露三个方法：
#   build(folder)   从文档文件夹建索引并保存
#   load()          从磁盘载入已有索引
#   ask(query)      回答一个问题，返回答案 + 引用来源
#
# 流程说明（每一步都对应一个可读的独立模块）：
#   ingest → chunk → index 构建；ask 时 hybrid_search → rerank → LLM
# ============================================================

import os

from .ingest import load_folder                    # 读取文档
from .chunk import chunk_text                      # 切块
from .index import Index                           # 索引
from .rank import hybrid_search, rerank            # 检索与重排
from .llm import LLM                               # 大模型客户端


class RAG:
    """端到端 RAG 系统"""

    def __init__(self, index_path="out/index.pkl", config=None):
        self.config = config or {}                 # 配置字典
        self.index_path = index_path               # 索引保存位置
        # 用配置里的参数构造索引对象
        self.index = Index(
            dim=self.config.get("EMBED_DIM", 2048),
            k1=self.config.get("K1", 1.5),
            b=self.config.get("B", 0.75),
        )
        # 用配置里的参数构造大模型客户端
        self.llm = LLM(
            base_url=self.config.get("LLM_BASE", "https://api.openai.com/v1"),
            model=self.config.get("LLM_MODEL", "gpt-4o-mini"),
            api_key=self.config.get("LLM_API_KEY", ""),
            timeout=self.config.get("LLM_TIMEOUT", 90),
        )
        self.top_k = self.config.get("TOP_K", 5)   # 默认召回条数

    # ---------------- 建库 ----------------
    def build(self, folder, chunk_size=500, overlap=100):
        """读取文件夹全部文档 → 切块 → 加入索引 → 保存到磁盘"""
        docs = load_folder(folder)                 # 读取所有支持的文件
        total = 0                                  # 统计切块总数
        for path, text in docs:                    # 逐份文档处理
            for piece in chunk_text(text, chunk_size, overlap):  # 切块
                self.index.add_documents([{        # 逐块入库
                    "id": f"{os.path.basename(path)}#{total}",
                    "text": piece,                 # 块文本
                    "meta": {"file": path},        # 记录来源文件
                }])
                total += 1
        self.index.finalize()                      # 完成统计与向量化
        self.index.save(self.index_path)           # 持久化到磁盘
        return {"docs": len(docs), "chunks": total}

    def load(self):
        """从磁盘载入已有索引"""
        self.index = Index.load(self.index_path)

    # ---------------- 问答 ----------------
    def ask(self, query, use_llm=True):
        """回答一个问题：检索 → 重排 → 生成，返回答案与来源"""
        # 1) 混合检索拿候选，再做一次最终重排
        cands = hybrid_search(self.index, query, top_k=self.top_k)
        cands = rerank(self.index, query, cands)
        # 2) 没配模型或明确只要检索时，直接返回检索结果
        if not use_llm or not self._can_call_llm():
            return {"query": query, "answer": None,
                    "contexts": self._ctx_list(cands)}
        # 3) 组装消息并调用大模型生成答案
        messages = [
            {"role": "system",                    # 系统提示：约束行为
             "content": "你是严谨的问答助手。只能依据【资料】回答，不得编造；"
                        "引用请标注来源编号如 [1]；资料不足以回答时请明确说明。"},
            {"role": "user", "content": self._build_prompt(query, cands)},
        ]
        answer = self.llm.chat(messages)           # 调用大模型
        return {"query": query, "answer": answer,
                "contexts": self._ctx_list(cands)}

    # ---------------- 内部工具 ----------------
    def _can_call_llm(self):
        """判断当前是否具备调用大模型的条件"""
        if self.llm.api_key:                       # 有密钥就能调
            return True
        # 没密钥时，仅当指向本机服务（如本地 Ollama）才允许调用
        return "localhost" in self.llm.base or "127.0.0.1" in self.llm.base

    def _ctx_list(self, cands):
        """把候选块转成方便展示的列表（含来源文件与摘要）"""
        return [{"file": d["meta"].get("file", ""),
                 "text": d["text"][:200]} for d in cands]

    def _build_prompt(self, query, cands):
        """把查询与检索到的资料拼成给模型的提示词"""
        parts = [f"问题：{query}\n\n【资料】"]      # 提示词开头
        for i, d in enumerate(cands, 1):           # 逐条编号资料
            parts.append(f"[{i}] {d['text']}")     # 带编号正文
        parts.append("\n请基于以上资料作答，并在对应句末标注来源编号 [n]。")
        return "\n".join(parts)                    # 拼成完整提示词
