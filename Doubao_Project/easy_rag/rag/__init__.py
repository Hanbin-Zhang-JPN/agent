# ============================================================
# rag 包入口：对外暴露 RAG 主类，方便 import 使用
# 用法：from rag.pipeline import RAG
# ============================================================

__version__ = "1.0.0"          # 版本号

# 重新导出主类，让使用方可以 from rag import RAG
from .pipeline import RAG

__all__ = ["RAG", "__version__"]
