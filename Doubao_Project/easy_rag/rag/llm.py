# ============================================================
# 大模型客户端：仅用标准库 urllib 调用 OpenAI 兼容接口
#
# 不引入 openai SDK，接口协议完全透明、可读、可调试
# 支持任意兼容 /chat/completions 的服务：
#   OpenAI / DeepSeek / 通义千问 / 本地 vLLM、Ollama 等
# 密钥通过构造参数传入，代码里不写死任何密钥
# ============================================================

import json
import urllib.request
import urllib.error


class LLM:
    """OpenAI 兼容的聊天客户端（支持普通与流式两种模式）"""

    def __init__(self, base_url, model, api_key="", timeout=90):
        self.base = base_url.rstrip("/")           # 接口根地址，如 …/v1
        self.model = model                         # 模型名
        self.api_key = api_key                     # 密钥（本地服务可为空）
        self.timeout = timeout                     # 超时秒数

    def _post(self, payload):
        """构造并发送一次 POST 请求，返回 HTTP 响应对象"""
        url = self.base + "/chat/completions"      # 兼容 OpenAI 的路径
        headers = {"Content-Type": "application/json"}
        if self.api_key:                           # 有密钥才加鉴权头
            headers["Authorization"] = f"Bearer {self.api_key}"
        req = urllib.request.Request(
            url,                                   # 请求地址
            data=json.dumps(payload).encode("utf-8"),  # 请求体
            headers=headers, method="POST")        # 头与方法
        return urllib.request.urlopen(req, timeout=self.timeout)

    def chat(self, messages, temperature=0.3, max_tokens=1500):
        """普通对话：一次性返回完整回复文本"""
        payload = {                                # 组装标准请求体
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        try:
            with self._post(payload) as resp:      # 发起请求
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:        # 服务端报错时透传原因
            detail = e.read().decode("utf-8", "ignore")
            raise RuntimeError(f"LLM 接口报错 {e.code}: {detail}") from e
        return data["choices"][0]["message"]["content"]  # 取回复文本

    def chat_stream(self, messages, temperature=0.3, max_tokens=1500):
        """流式对话：逐段产出文本，适合边生成边展示"""
        payload = {                                # 流式只需加 stream 字段
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }
        try:
            with self._post(payload) as resp:      # 发起流式请求
                for line in resp:                  # SSE 协议按行返回
                    line = line.decode("utf-8").strip()
                    if not line.startswith("data:"):   # 忽略心跳等非数据行
                        continue
                    data = line[5:].strip()        # 去掉 "data:" 前缀
                    if data == "[DONE]":           # 官方结束标记
                        break
                    obj = json.loads(data)         # 解析增量块
                    delta = obj["choices"][0]["delta"].get("content", "")
                    if delta:                      # 有内容才产出
                        yield delta
        except urllib.error.HTTPError as e:        # 透传错误原因
            raise RuntimeError(f"LLM 接口报错 {e.code}: "
                               f"{e.read().decode('utf-8', 'ignore')}") from e
