# ============================================================
# 本地网页版 RAG：只用标准库 http.server，无任何前端框架
#
# 提供两个端点：
#   GET  /       → 返回问答页面（单文件 HTML + JS）
#   POST /ask    → 接收 {query}，返回 {answer, contexts}
#
# 用法：python app.py serve --port 8080
# ============================================================

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

# 页面：一个输入框 + 提问按钮，用 fetch 调 /ask 接口
# 故意不用任何外部 CDN，页面离线也能跑
_PAGE = """<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<title>easy_rag 本地问答</title>
<style>
  body { font-family: -apple-system, "PingFang SC", sans-serif;
         max-width: 720px; margin: 40px auto; padding: 0 16px; color: #222; }
  textarea { width: 100%; height: 80px; font-size: 15px;
             border: 1px solid #ccc; border-radius: 8px; padding: 10px; }
  button { margin-top: 10px; padding: 8px 22px; font-size: 15px;
           border: none; border-radius: 8px; background: #2563eb;
           color: #fff; cursor: pointer; }
  .card { background: #f7f7f8; border-radius: 10px; padding: 14px;
          margin-top: 18px; }
  .src { font-size: 13px; color: #555; margin: 4px 0;
         border-top: 1px dashed #ddd; padding-top: 6px; }
</style>
</head>
<body>
<h2>easy_rag 本地问答</h2>
<textarea id="q" placeholder="输入你的问题，例如：星云科技是哪一年成立的？"></textarea>
<br><button onclick="ask()">提问</button>
<div id="out"></div>
<script>
async function ask() {                          // 提问函数
  const q = document.getElementById("q").value.trim();
  if (!q) return;                               // 空问题直接返回
  const out = document.getElementById("out");
  out.innerHTML = "<div class='card'>检索中…</div>";   // 提示等待
  const res = await fetch("/ask", {             // 调后端接口
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({query: q})            // 传问题
  });
  const data = await res.json();                // 解析返回
  let html = "";
  if (data.answer) html += "<div class='card'><b>答案</b><br>" +
                          data.answer.replace(/\\n/g, "<br>") + "</div>";
  html += "<div class='card'><b>检索到的资料</b>";
  data.contexts.forEach(c => {                  // 展示来源
    html += "<div class='src'>" + c.file + "<br>" + c.text + "</div>";
  });
  html += "</div>";
  out.innerHTML = html;                         // 渲染结果
}
</script>
</body>
</html>
"""


def serve(rag, port=8080):
    """启动网页服务，rag 为已建好索引的 RAG 实例"""
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass                                  # 关闭默认日志，保持终端干净

        def do_GET(self):
            if urlparse(self.path).path == "/":   # 访问首页
                body = _PAGE.encode("utf-8")      # 编码页面
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)            # 返回页面
            else:                                 # 其它路径一律 404
                self.send_response(404)
                self.end_headers()

        def do_POST(self):
            if urlparse(self.path).path != "/ask":  # 只接受 /ask
                self.send_response(404)
                self.end_headers()
                return
            length = int(self.headers.get("Content-Length", 0))
            q = json.loads(self.rfile.read(length)).get("query", "")
            result = rag.ask(q)                   # 调用 RAG 主流程
            body = json.dumps(result, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)                # 返回 JSON 结果

    print(f"网页版已启动：http://127.0.0.1:{port}")
    print("按 Ctrl+C 停止服务")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
