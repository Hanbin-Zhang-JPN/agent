#!/usr/bin/env python3
"""Local HTTP UI + JSON API. Start with python3 server.py."""
import argparse
import base64
import binascii
import importlib.util
import json
import os
import secrets
import sys
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from raglab.core import Store, Remote, ask, extract_file, split_text
from raglab.evaluate import evaluate

ROOT = Path(__file__).resolve().parent
TOKEN = secrets.token_urlsafe(32)
MAX_BODY = 12_000_000


def load_demo(store):
    return [store.add(p.name, p.read_text(encoding="utf-8"), size=260, overlap=40, demo=True)
            for p in sorted((ROOT / "examples").glob("*.md"))]


def integer(body, key, default):
    value = body.get(key, default)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{key} 须为整数。")
    return value


def string(body, key, default=""):
    value = body.get(key, default)
    if not isinstance(value, str):
        raise ValueError(f"{key} 须为字符串。")
    return value


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        # No bodies, queries, credentials or document contents in access logs.
        if args and isinstance(args[0], str):
            sys.stderr.write(f"HTTP {self.command} {urlsplit(self.path).path}\n")

    def send(self, status, data, content_type="application/json; charset=utf-8"):
        payload = json.dumps(data, ensure_ascii=False).encode() if content_type.startswith("application/json") else data
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
        self.end_headers()
        self.wfile.write(payload)

    def allowed(self):
        port = self.server.server_port
        allowed_hosts = {f"localhost:{port}", f"127.0.0.1:{port}"}
        if self.headers.get("Host") not in allowed_hosts:
            self.send(403, {"error": "仅允许从 localhost 或 127.0.0.1 访问。"})
            return False
        if self.command == "POST":
            origin = self.headers.get("Origin")
            if origin and origin not in {f"http://{h}" for h in allowed_hosts}:
                self.send(403, {"error": "不允许跨站请求。"})
                return False
            if not secrets.compare_digest(self.headers.get("X-RAG-Token", ""), TOKEN):
                self.send(403, {"error": "请求令牌无效，请刷新页面。"})
                return False
        return True

    def do_GET(self):
        if not self.allowed():
            return
        path = urlsplit(self.path).path
        try:
            if path == "/api/config":
                rows = self.server.store.chunks()
                valid_vectors = sum(bool(r["embedding"]) and r["embedding_key"] == self.server.remote.embedding_key for r in rows)
                self.send(200, {"token": TOKEN, "has_key": bool(self.server.remote.api_key),
                                "model": self.server.remote.model, "embedding_model": self.server.remote.embedding_model,
                                "pdf_supported": importlib.util.find_spec("pypdf") is not None,
                                "chunks": len(rows), "semantic_chunks": valid_vectors,
                                "eval_cases": json.loads((ROOT / "examples/evaluation.json").read_text(encoding="utf-8"))})
            elif path == "/api/documents":
                self.send(200, {"documents": self.server.store.documents()})
            elif path.startswith("/api/documents/"):
                self.send(200, self.server.store.document(path.removeprefix("/api/documents/")))
            else:
                files = {"/": ("index.html", "text/html; charset=utf-8"),
                         "/app.js": ("app.js", "text/javascript; charset=utf-8"),
                         "/style.css": ("style.css", "text/css; charset=utf-8")}
                if path not in files:
                    self.send(404, {"error": "页面不存在。"})
                    return
                name, mime = files[path]
                self.send(200, (ROOT / "web" / name).read_bytes(), mime)
        except ValueError as exc:
            self.send(404, {"error": str(exc)})
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception:
            traceback.print_exc()
            self.send(500, {"error": "服务器异常，请查看终端日志。"})

    def do_POST(self):
        if not self.allowed():
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= MAX_BODY:
                self.send(413, {"error": "请求过大或为空；单文件最多 8 MB。"})
                return
            if self.headers.get("Content-Type", "").split(";")[0] != "application/json":
                raise ValueError("请发送 application/json。")
            body = json.loads(self.rfile.read(length))
            if not isinstance(body, dict):
                raise ValueError("请求须为 JSON 对象。")
            path = urlsplit(self.path).path
            store, remote = self.server.store, self.server.remote
            if path == "/api/documents":
                name = string(body, "name", "笔记.md")
                if "file_base64" in body:
                    try:
                        data = base64.b64decode(string(body, "file_base64"), validate=True)
                    except (ValueError, binascii.Error) as exc:
                        raise ValueError("文件编码无效。") from exc
                    if len(data) > 8_000_000:
                        raise ValueError("单文件最多 8 MB。")
                    text = extract_file(name, data)
                else:
                    text = string(body, "text")
                result = store.add(name, text, integer(body, "chunk_size", 500), integer(body, "overlap", 80))
            elif path == "/api/examples":
                result = {"documents": load_demo(store)}
            elif path == "/api/ask":
                doc_ids = body.get("doc_ids")
                if doc_ids is not None and (not isinstance(doc_ids, list) or len(doc_ids) > 3000 or
                                            any(not isinstance(x, str) for x in doc_ids)):
                    raise ValueError("doc_ids 须为文档 ID 数组。")
                generate = body.get("generate", False)
                if not isinstance(generate, bool):
                    raise ValueError("generate 须为布尔值。")
                result = ask(store, remote, string(body, "question"), generate=generate,
                             mode=string(body, "mode", "hybrid"), top_k=integer(body, "top_k", 4),
                             vector_kind=string(body, "vector_kind", "tfidf"), doc_ids=doc_ids,
                             budget=integer(body, "budget", 6000))
            elif path == "/api/split-preview":
                text = string(body, "text")
                if len(text) > 20000:
                    raise ValueError("分块预览最多 20,000 字符。")
                result = {"chunks": split_text(text, integer(body, "chunk_size", 500), integer(body, "overlap", 80))}
            elif path == "/api/embeddings":
                result = store.embed(remote)
            elif path == "/api/evaluate":
                cases = body.get("cases", json.loads((ROOT / "examples/evaluation.json").read_text(encoding="utf-8")))
                result = evaluate(store, cases, integer(body, "top_k", 4))
            elif path.startswith("/api/documents/"):
                parts = path.split("/")
                if len(parts) != 5:
                    raise ValueError("接口地址错误。")
                doc_id, action = parts[3:]
                if action == "delete":
                    store.delete(doc_id)
                    result = {"deleted": True}
                elif action == "reindex":
                    result = store.reindex(doc_id, integer(body, "chunk_size", 500), integer(body, "overlap", 80))
                else:
                    raise ValueError("操作不支持。")
            else:
                self.send(404, {"error": "接口不存在。"})
                return
            self.send(200, result)
        except (ValueError, UnicodeDecodeError) as exc:
            self.send(400, {"error": str(exc)})
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception:
            traceback.print_exc()
            self.send(500, {"error": "服务器异常，请查看终端日志。"})


def main():
    parser = argparse.ArgumentParser(description="RAG Lab · 个人/团队知识库")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--db", default=str(ROOT / "data/knowledge.db"))
    parser.add_argument("--demo", action="store_true", help="加载可重复导入的虚构示例资料")
    args = parser.parse_args()
    store = Store(args.db)
    if args.demo:
        load_demo(store)
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    server.store, server.remote = store, Remote()
    print(f"RAG Lab 已启动：http://127.0.0.1:{server.server_port}", flush=True)
    print(f"数据库：{store.path}\n按 Ctrl+C 停止。", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
