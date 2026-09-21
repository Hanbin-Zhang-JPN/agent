# -*- coding: utf-8 -*-
"""
网络请求工具 net
=================

作用：提供最小化的 HTTP JSON 请求封装，供「语义向量 API」与「大模型 API」复用。

为什么有这个文件：
  - 本项目全程只用标准库，因此用 urllib 手写 POST JSON 请求；
  - 把网络层单独抽出来，embedder 与 llm 都能复用，避免重复代码；
  - 逻辑完全透明：构造请求 → 发送 → 读响应 → 解析 JSON。

注意：这是全项目唯一涉及「对外网络」的地方。
只有当用户配置了 API（OpenAI 兼容接口）时才会被调用，
不配置 API 时整个系统可完全离线运行（见 embedder.HashEmbedder）。
"""

import json
import urllib.request
import urllib.error


def post_json(url: str, headers: dict, payload: dict, timeout: int = 60):
    """
    向指定 URL 发送一个 JSON POST 请求，并返回解析后的 JSON 响应。

    参数:
        url:     目标接口地址。
        headers: 请求头（如 Authorization、Content-Type）。
        payload: 请求体（会自动序列化为 JSON）。
        timeout: 超时秒数，防止网络卡死。

    返回:
        服务器返回的 JSON（dict / list 等）。

    抛出:
        RuntimeError: 请求失败、超时或返回非 JSON 时抛出。
    """
    # 把请求体序列化为 JSON 字节
    body = json.dumps(payload).encode("utf-8")
    # 构造请求对象，并带上请求头
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        # 发送请求并读取响应
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            # 读取响应字节并按 UTF-8 解码
            raw = resp.read().decode("utf-8")
        # 解析 JSON；失败说明接口返回异常
        return json.loads(raw)
    except urllib.error.HTTPError as e:
        # 服务端返回了非 2xx 状态码，把错误信息透传出来
        detail = e.read().decode("utf-8", errors="ignore")[:500]
        raise RuntimeError(f"HTTP {e.code} 错误: {detail}") from e
    except urllib.error.URLError as e:
        # 网络不可达、域名解析失败等
        raise RuntimeError(f"网络错误: {e.reason}") from e
    except json.JSONDecodeError as e:
        # 返回内容不是合法 JSON
        raise RuntimeError(f"响应不是合法 JSON: {e}") from e
