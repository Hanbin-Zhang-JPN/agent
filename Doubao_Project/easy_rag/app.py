#!/usr/bin/env python3
# ============================================================
# 入口：命令行使用 RAG，四个子命令覆盖完整流程
#
#   python app.py build --dir data/sample      # 建索引
#   python app.py ask "你的问题"               # 单次问答
#   python app.py chat                         # 交互式对话
#   python app.py eval                         # 检索质量评测
#   python app.py serve --port 8080            # 本地网页版
#
# 所有逻辑都落在 rag/ 包内，本文件只负责解析参数与展示结果
# ============================================================

import argparse
import json
import sys

import config                                   # 全局配置
from rag.pipeline import RAG                     # RAG 主类
from rag.rank import hybrid_search               # 检索（评测用）


def cmd_build(args):
    """建库：读取文档 → 切块 → 建索引 → 保存"""
    rag = RAG(index_path=args.index, config=vars(config))
    info = rag.build(args.dir, args.chunk_size, args.overlap)
    print(f"[建库完成] 文档 {info['docs']} 个，切块 {info['chunks']} 个")
    print(f"[索引保存] {args.index}")


def _load_rag(args):
    """按参数构造 RAG 并载入已有索引"""
    rag = RAG(index_path=args.index, config=vars(config))
    try:
        rag.load()                               # 从磁盘加载索引
    except FileNotFoundError:
        print("找不到索引文件，请先运行 build 建库")
        sys.exit(1)
    return rag


def cmd_ask(args):
    """单次问答：打印答案与检索到的资料"""
    rag = _load_rag(args)
    res = rag.ask(args.query, use_llm=not args.no_llm)
    print(f"问题：{res['query']}\n")
    if res["answer"]:                            # 有大模型答案就打印
        print("答案：")
        print(res["answer"])
    else:                                        # 否则提示仅检索
        print("（未配置大模型密钥，以下仅为检索结果）")
    print("\n--- 检索到的资料 ---")
    for i, c in enumerate(res["contexts"], 1):   # 逐条展示来源
        print(f"[{i}] {c['file']}")
        print(f"    {c['text']}")


def cmd_chat(args):
    """交互式对话：输入问题回车，exit 退出"""
    rag = _load_rag(args)
    print("进入对话模式，输入 exit 退出。")
    while True:
        q = input("\n你：").strip()              # 读取输入
        if q.lower() in ("exit", "quit", "退出"):
            break
        res = rag.ask(q)                         # 调用 RAG
        if res["answer"]:                        # 有答案就打印
            print("RAG：")
            print(res["answer"])
        else:                                    # 仅检索模式
            print("（未配置大模型密钥，以下仅为检索结果）")
            for i, c in enumerate(res["contexts"], 1):
                print(f"[{i}] {c['file']}: {c['text']}")


def cmd_eval(args):
    """检索质量评测：检查期望关键词是否出现在前 top_k 个结果里"""
    rag = _load_rag(args)
    with open(args.cases, encoding="utf-8") as f:
        cases = json.load(f)                     # 读取评测用例
    total = 0                                    # 用例总数
    hit = 0                                      # 命中数
    for c in cases:                              # 逐条评测
        cands = hybrid_search(rag.index, c["q"], top_k=args.top_k)
        ok = any(c["kw"] in d["text"] for d in cands)  # 关键词是否命中
        total += 1
        hit += int(ok)                           # 命中累加
        print(f"[{'通过' if ok else '失败'}] {c['q']} → 期望含「{c['kw']}」")
    print(f"\nHit@{args.top_k} = {hit}/{total} = {hit / max(1, total):.0%}")


def cmd_serve(args):
    """启动本地网页版问答"""
    rag = _load_rag(args)
    from web.ui import serve                     # 延迟导入，避免副作用
    serve(rag, args.port)


def main():
    """解析命令行参数并分派到对应子命令"""
    p = argparse.ArgumentParser(description="easy_rag：零依赖白箱 RAG")
    p.add_argument("--index", default="out/index.pkl",
                   help="索引文件路径（默认 out/index.pkl）")
    sub = p.add_subparsers(dest="cmd", required=True)

    # build 子命令
    b = sub.add_parser("build", help="从文档文件夹建索引")
    b.add_argument("--dir", default="data/sample", help="文档文件夹")
    b.add_argument("--chunk-size", type=int, default=config.CHUNK_SIZE)
    b.add_argument("--overlap", type=int, default=config.CHUNK_OVERLAP)
    b.set_defaults(func=cmd_build)

    # ask 子命令
    a = sub.add_parser("ask", help="单次问答")
    a.add_argument("query", help="要问的问题")
    a.add_argument("--no-llm", action="store_true", help="只检索不调用大模型")
    a.set_defaults(func=cmd_ask)

    # chat 子命令
    sub.add_parser("chat", help="交互式对话").set_defaults(func=cmd_chat)

    # eval 子命令
    e = sub.add_parser("eval", help="检索质量评测")
    e.add_argument("--cases", default="data/sample/cases.json",
                   help="评测用例 JSON 文件")
    e.add_argument("--top-k", type=int, default=5, help="考察前几个结果")
    e.set_defaults(func=cmd_eval)

    # serve 子命令
    s = sub.add_parser("serve", help="本地网页版")
    s.add_argument("--port", type=int, default=8080, help="端口号")
    s.set_defaults(func=cmd_serve)

    args = p.parse_args()
    args.func(args)                              # 调用对应处理函数


if __name__ == "__main__":
    main()
