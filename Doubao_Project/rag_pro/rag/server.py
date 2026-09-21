# -*- coding: utf-8 -*-
"""
HTTP API 服务 server
=====================

作用：用 Python 标准库的 http.server 起一个本地 API 服务，
     让外部程序（网页、脚本）可以通过 HTTP 调用 RAG 问答。

为什么用标准库而不是 FastAPI 等框架：
  - 保持「零黑盒依赖」的项目原则；
  - http.server + ThreadingHTTPServer 足够支撑本地/内网场景，
    每个请求由独立线程处理，能并发响应；
  - 代码量小、完全透明，想改成 FastAPI 也很容易（接口结构不变）。

提供接口：
  - GET  /health             健康检查
  - POST /query              问答  {"question": "..."}
  - POST /ingest             增量入库 {"path": "文档目录"}
  - GET  /info               索引信息
"""

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# 默认端口
DEFAULT_PORT = 8765


def make_handler(pipeline):
    """
    工厂函数：为指定的 pipeline 生成一个 HTTP 请求处理器类。

    参数:
        pipeline: 已初始化（build/load 过）的 RagPipeline。

    返回:
        handler 类（可直接传给 ThreadingHTTPServer）。
    """
    # 保存 pipeline 引用（闭包内使用）
    p = pipeline

    # 定义请求处理器类
    class Handler(BaseHTTPRequestHandler):
        # 关闭日志输出，保持终端干净
        def log_message(self, *args):
            pass

        # 响应工具：写 JSON 返回
        def _json(self, code: int, data: dict) -> None:
            # 序列化为 JSON 字节
            body = json.dumps(data, ensure_ascii=False).encode("utf-8")
            # 设置状态码
            self.send_response(code)
            # 设置内容类型
            self.send_header("Content-Type", "application/json; charset=utf-8")
            # 设置内容长度
            self.send_header("Content-Length", str(len(body)))
            # 结束响应头
            self.end_headers()
            # 写入响应体
            self.wfile.write(body)

        # GET 请求处理
        def do_GET(self):
            # 健康检查接口
            if self.path == "/health":
                # 返回存活状态
                self._json(200, {"status": "ok"})
                return
            # 索引信息接口
            if self.path == "/info":
                # 返回索引规模信息
                self._json(200, {
                    "docs": len(p.bm25.docs) if p.bm25 else 0,   # 块数
                    "llm": bool(p.llm and p.llm.available()),     # 是否配置 LLM
                })
                return
            # 其它路径返回 404
            self._json(404, {"error": "not found"})

        # POST 请求处理
        def do_POST(self):
            # 读取请求体长度
            length = int(self.headers.get("Content-Length", 0))
            # 读取请求体
            raw = self.rfile.read(length)
            # 解析 JSON 请求体；失败返回 400
            try:
                payload = json.loads(raw.decode("utf-8"))
            except Exception:
                self._json(400, {"error": "invalid json"})
                return

            # 问答接口
            if self.path == "/query":
                # 取问题
                q = payload.get("question", "")
                # 问题为空返回 400
                if not q:
                    self._json(400, {"error": "question required"})
                    return
                # 执行 RAG 问答
                result = p.ask(q)
                # 返回结果
                self._json(200, result)
                return

            # 入库接口
            if self.path == "/ingest":
                # 取文档目录
                path = payload.get("path", "")
                # 目录不存在返回 400
                if not path or not os.path.exists(path):
                    self._json(400, {"error": "path not exists"})
                    return
                # 重建索引
                summary = p.build(path)
                # 返回构建汇总
                self._json(200, summary)
                return

            # 其它路径返回 404
            self._json(404, {"error": "not found"})

    # 返回处理器类
    return Handler


def serve(pipeline, port: int = DEFAULT_PORT, host: str = "127.0.0.1") -> None:
    """
    启动 HTTP 服务（阻塞运行）。

    参数:
        pipeline: RagPipeline 实例。
        port:     监听端口。
        host:     监听地址（默认仅本机）。
    """
    # 生成请求处理器
    handler = make_handler(pipeline)
    # 创建线程化 HTTP 服务器
    server = ThreadingHTTPServer((host, port), handler)
    # 打印启动信息
    print(f"[server] 服务已启动: http://{host}:{port}")
    print(f"[server] 接口: GET /health, POST /query, POST /ingest")
    # 开始对外服务（阻塞）
    server.serve_forever()
