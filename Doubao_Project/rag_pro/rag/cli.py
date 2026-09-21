# -*- coding: utf-8 -*-
"""
命令行入口 cli
===============

作用：把 RAG 的核心能力封装成命令行，方便直接使用与调试。

命令一览：
  python -m rag.cli build  --dir <文档目录>      构建索引
  python -m rag.cli ask    --q "问题"           单次问答
  python -m rag.cli chat                        交互式问答
  python -m rag.cli eval   --qa <评测json>      跑检索评测
  python -m rag.cli serve  --port 8765          启动 HTTP 服务
  python -m rag.cli info                        查看索引信息
"""

import argparse
import json
import os
import sys

# 把项目根目录加入模块搜索路径（保证 `python rag/cli.py` 也能运行）
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 默认配置路径
DEFAULT_CFG = "config.json"
# 默认文档目录
DEFAULT_DIR = "data/sample"


def load_config(path: str = DEFAULT_CFG) -> dict:
    """
    加载全局配置文件（JSON）。

    参数:
        path: 配置文件路径。

    返回:
        配置字典；文件不存在时返回空配置。
    """
    # 配置文件存在时读取
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    # 不存在则返回空字典（全部走默认值）
    return {}


def _get_pipeline(args):
    """
    按命令行参数创建并加载/构建 RAG 主流程。

    参数:
        args: argparse 解析出的参数。

    返回:
        RagPipeline 实例。
    """
    # 延迟导入，避免无谓开销
    from .pipeline import RagPipeline
    # 加载配置
    cfg = load_config(args.config)
    # 创建主流程实例
    pipe = RagPipeline(cfg, store_dir=args.store)
    # 尝试加载已有索引
    if pipe.load():
        # 已存在索引，直接使用
        print(f"[cli] 已加载索引（{args.store}）")
    else:
        # 索引不存在，自动从文档目录构建
        print(f"[cli] 未找到索引，从 {args.dir} 构建...")
        # 构建索引
        pipe.build(args.dir)
    # 返回主流程
    return pipe


def cmd_build(args):
    """执行 build 命令：构建索引。"""
    # 加载配置
    cfg = load_config(args.config)
    # 延迟导入入库模块
    from .pipeline import RagPipeline
    # 创建主流程并构建索引
    pipe = RagPipeline(cfg, store_dir=args.store)
    summary = pipe.build(args.dir)
    # 打印构建结果
    print(f"[build] 完成：{summary}")


def cmd_ask(args):
    """执行 ask 命令：单次问答。"""
    # 创建主流程（加载或构建索引）
    pipe = _get_pipeline(args)
    # 执行问答
    result = pipe.ask(args.q, top_n=args.top_n)
    # 打印答案
    print("\n===== 答案 =====")
    print(result["answer"])
    # 打印引用
    print("\n===== 引用 =====")
    for c in result["citations"]:
        print(" -", c)
    # 打印统计信息
    print(f"\n[ask] 耗时 {result['time_ms']}ms | 使用LLM: {result['used_llm']}")


def cmd_chat(args):
    """执行 chat 命令：交互式问答。"""
    # 创建主流程
    pipe = _get_pipeline(args)
    # 打印使用说明
    print("[chat] 输入问题开始问答，输入 exit 退出。")
    # 交互循环
    while True:
        # 读取用户输入
        q = input("\n你: ").strip()
        # 退出指令
        if q.lower() in ("exit", "quit", "q"):
            break
        # 空输入跳过
        if not q:
            continue
        # 执行问答
        result = pipe.ask(q, top_n=args.top_n)
        # 打印答案
        print("\nRAG:", result["answer"])


def cmd_eval(args):
    """执行 eval 命令：跑检索评测。"""
    # 创建主流程
    pipe = _get_pipeline(args)
    # 延迟导入评测模块
    from .eval import run_eval
    # 执行评测
    result = run_eval(pipe, args.qa, top_k=args.top_n)
    # 打印汇总指标
    print("\n===== 检索评测 =====")
    print(f"样本数  : {result['samples']}")
    print(f"Recall@{result['top_k']} : {result['recall@k']}")
    print(f"MRR@{result['top_k']}    : {result['mrr@k']}")
    print(f"Hit@{result['top_k']}   : {result['hit@k']}")


def cmd_serve(args):
    """执行 serve 命令：启动 HTTP 服务。"""
    # 创建主流程
    pipe = _get_pipeline(args)
    # 延迟导入服务模块
    from .server import serve
    # 启动服务（阻塞）
    serve(pipe, port=args.port)


def cmd_info(args):
    """执行 info 命令：查看索引信息。"""
    # 创建主流程
    pipe = _get_pipeline(args)
    # 打印索引规模
    print(f"[info] 文本块数 : {len(pipe.bm25.docs) if pipe.bm25 else 0}")
    print(f"[info] 向量条数 : {len(pipe.vs) if pipe.vs else 0}")
    print(f"[info] LLM 配置 : {'已启用' if pipe.llm and pipe.llm.available() else '未配置（离线抽取式）'}")


def main():
    """命令行入口：解析参数并分发到各子命令。"""
    # 创建顶层解析器
    parser = argparse.ArgumentParser(description="rag_pro —— 现代化白箱 RAG")
    # 公共参数：配置文件与索引目录
    parser.add_argument("--config", default=DEFAULT_CFG, help="配置文件路径")
    parser.add_argument("--store", default="store", help="索引存放目录")
    # 子命令解析器
    sub = parser.add_subparsers(dest="cmd", required=True)

    # build 子命令
    p_build = sub.add_parser("build", help="构建索引")
    p_build.add_argument("--dir", default=DEFAULT_DIR, help="文档目录")
    p_build.set_defaults(func=cmd_build)

    # ask 子命令
    p_ask = sub.add_parser("ask", help="单次问答")
    p_ask.add_argument("--q", required=True, help="问题")
    p_ask.add_argument("--top_n", type=int, default=5, help="使用块数")
    p_ask.set_defaults(func=cmd_ask)

    # chat 子命令
    p_chat = sub.add_parser("chat", help="交互式问答")
    p_chat.add_argument("--top_n", type=int, default=5, help="使用块数")
    p_chat.set_defaults(func=cmd_chat)

    # eval 子命令
    p_eval = sub.add_parser("eval", help="检索评测")
    p_eval.add_argument("--qa", required=True, help="评测数据 JSON 路径")
    p_eval.add_argument("--top_n", type=int, default=5, help="k 值")
    p_eval.set_defaults(func=cmd_eval)

    # serve 子命令
    p_serve = sub.add_parser("serve", help="启动 HTTP 服务")
    p_serve.add_argument("--port", type=int, default=8765, help="端口")
    p_serve.set_defaults(func=cmd_serve)

    # info 子命令
    p_info = sub.add_parser("info", help="查看索引信息")
    p_info.set_defaults(func=cmd_info)

    # 解析参数并执行对应函数
    args = parser.parse_args()
    args.func(args)


# 直接运行本文件时进入入口
if __name__ == "__main__":
    main()
