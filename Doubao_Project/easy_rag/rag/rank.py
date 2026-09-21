# ============================================================
# 混合检索 + 重排
#
#   - 混合检索：BM25（字面精准）与稠密向量（宽松相似）互补
#     BM25 擅长精确关键词，稠密向量能容忍表记差异 / 部分改写
#   - RRF 融合：把两种排序的位次合并，公式 1 / (k + rank)
#     只关心"排第几"，不关心各自分数尺度，天然可融合
#   - 重排：对候选块再做一次更细的打分，输出最终顺序
# ============================================================

from .tokenize import tokenize                     # 分词
from .embed import embed_tokens, normalize, dot    # 向量化


def rrf_fuse(rank_lists, k=60):
    """把多份排名列表按 RRF 融合成一份，返回 {文档号: 融合分}"""
    fused = {}                                     # 文档号 → 融合得分
    for ranks in rank_lists:                       # 遍历每一份排名
        for rank, (doc_idx, _score) in enumerate(ranks):
            # 位次越靠前，加的分越多；k 越大，排名的区分度越平缓
            fused[doc_idx] = fused.get(doc_idx, 0.0) + 1.0 / (k + rank + 1)
    return fused


def hybrid_search(index, query, top_k=5, bm25_k=20, dense_k=20, rrf_k=60):
    """混合检索主入口：两种方式各取一批候选，再 RRF 融合取 top_k"""
    index.ensure_finalized()                       # 确保统计完成
    q_tokens = tokenize(query)                     # 查询做分词
    # 查询向量：与文档用同一套嵌入与 IDF，保证可比较
    q_vec = normalize(embed_tokens(q_tokens, index.dim, index.idf))
    bm25_res = index.search_bm25(q_tokens, bm25_k) # BM25 候选
    dense_res = index.search_dense(q_vec, dense_k) # 稠密候选
    fused = rrf_fuse([bm25_res, dense_res], rrf_k) # RRF 融合
    # 按融合分降序，取前 top_k 个文档对象
    order = sorted(fused.items(), key=lambda kv: kv[1], reverse=True)[:top_k]
    return [index.docs[i] for i, _ in order]


def rerank(index, query, candidates):
    """对候选块做最终重排：融合"词面重合度"与"向量相似度"""
    q_tokens = set(tokenize(query))                # 查询词元集合
    q_vec = normalize(embed_tokens(list(q_tokens), index.dim, index.idf))
    scored = []
    for doc in candidates:                         # 逐个候选块打分
        doc_toks = set(doc["tokens"])              # 该块词元集合
        # 重合率：查询词里有多少比例出现在这块资料里（最重要信号）
        overlap = len(q_tokens & doc_toks) / max(1, len(q_tokens))
        # 向量相似：整块向量与查询向量的余弦
        sim = dot(q_vec, normalize(
            embed_tokens(doc["tokens"], index.dim, index.idf)))
        # 词面重合权重更高，因为它直接反映"资料里有没有这句话"
        score = 0.7 * overlap + 0.3 * max(0.0, sim)
        scored.append((score, doc))
    scored.sort(key=lambda kv: kv[0], reverse=True)  # 按得分降序
    return [doc for _s, doc in scored]             # 只返回文档对象
