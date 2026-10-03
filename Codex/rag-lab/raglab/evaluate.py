"""Deterministic retrieval evaluation, deliberately separate from generation."""
import time
from .core import retrieve


def evaluate(store, cases, top_k=4):
    if not isinstance(cases, list) or not 1 <= len(cases) <= 50:
        raise ValueError("评测集须为 1–50 个问题组成的 JSON 数组。")
    for c in cases:
        if not isinstance(c, dict) or not isinstance(c.get("question"), str) or not c["question"].strip():
            raise ValueError("每道题须包含非空 question。")
        if len(c["question"]) > 2000:
            raise ValueError("评测问题最多 2000 字符。")
        if "expected_source" not in c or c.get("expected_source") == "":
            raise ValueError("每道题须明确设置 expected_source：文档名或 null（无答案题）。")
        if c.get("expected_source") is not None and not isinstance(c["expected_source"], str):
            raise ValueError("expected_source 须为文档名字符串或 null（无答案题）。")
        if not isinstance(c.get("expected_quote", ""), str):
            raise ValueError("expected_quote 须为字符串。")
    # One immutable corpus snapshot makes modes comparable even if a concurrent
    # HTTP request imports/deletes a document during a long evaluation.
    corpus = store.chunks()
    class Snapshot:
        def chunks(self, doc_ids=None):
            return corpus
    snapshot = Snapshot()
    reports = []
    for mode in ("bm25", "vector", "hybrid"):
        rows, hits, rr, negatives, rejected = [], 0, 0., 0, 0
        started = time.perf_counter()
        for c in cases:
            result = retrieve(snapshot, c["question"], mode=mode, top_k=top_k)
            expected = c.get("expected_source")
            quote = c.get("expected_quote", "")
            rank = next((i for i, r in enumerate(result["results"], 1)
                         if r["name"] == expected and quote in r["text"]), None) if expected else None
            if expected:
                hits += int(rank is not None)
                rr += 1 / rank if rank else 0
            else:
                negatives += 1
                rejected += int(not result["results"])
            rows.append({"question": c["question"], "expected_source": expected, "rank": rank,
                         "pass": rank is not None if expected else not result["results"],
                         "retrieved": [r["name"] + f" · #{r['ordinal']}" for r in result["results"]]})
        positives = len(cases) - negatives
        reports.append({"mode": mode, "hit_at_k": round(hits / positives, 4) if positives else None,
                        "mrr_at_k": round(rr / positives, 4) if positives else None,
                        "no_candidate_rate": round(rejected / negatives, 4) if negatives else None,
                        "positive_cases": positives, "negative_cases": negatives, "rows": rows,
                        "latency_ms": round((time.perf_counter() - started) * 1000, 2)})
    return {"reports": reports, "top_k": top_k, "cases": len(cases), "corpus_chunks": len(corpus),
            "note": "评测仅比较本地检索：命中要求文件名和证据短语同时匹配。不衡量生成质量；无候选率不等于可靠拒答率。"}
