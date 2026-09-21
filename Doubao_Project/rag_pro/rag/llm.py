# -*- coding: utf-8 -*-
"""
大模型客户端 llm
=================

作用：调用「大语言模型」生成最终答案，使用 OpenAI 兼容的 /v1/chat/completions 协议。

关于外部依赖的说明（项目刻意保持透明）：
  - 大模型本身无法从零实现，必须调用外部服务；
  - 本项目只依赖「标准、公开」的 OpenAI 兼容协议，任何主流服务商
    （豆包、硅基流动、DeepSeek、OpenAI 等）都能接入；
  - 唯一的请求逻辑在 net.post_json 里，HTTP 头、请求体、响应解析全部可见；
  - 若用户不配置 LLM，系统会自动降级为「离线抽样式生成」（见 generator.py），
    全流程依旧可用。

调用方法：
  - 请求 POST {base_url}/v1/chat/completions
  - 请求体 {model, messages, temperature, max_tokens}
  - 请求头 Authorization: Bearer {api_key}
  - 响应体 choices[0].message.content 即生成的文本。
"""

from . import net      # 复用网络请求工具


class LLMClient:
    """OpenAI 兼容的大模型客户端（非流式，足够 RAG 问答使用）。"""

    def __init__(self, base_url: str, api_key: str, model: str,
                 temperature: float = 0.3):
        """
        参数:
            base_url:   API 基础地址（会自动补 /v1/chat/completions）。
            api_key:    API 密钥。
            model:      模型名（如 doubao-pro-32k、deepseek-chat 等）。
            temperature: 采样温度（越小越稳定，RAG 问答建议偏小）。
        """
        # 去掉尾部斜杠，便于拼接路径
        self.base_url = base_url.rstrip("/")
        # 保存密钥与模型名
        self.api_key = api_key
        self.model = model
        # 保存温度
        self.temperature = temperature

    def chat(self, messages: list, max_tokens: int = 1024,
             temperature: float = None) -> str:
        """
        发送一轮对话，返回模型生成的文本。

        参数:
            messages:   消息列表，形如
                       [{"role": "system", "content": "..."},
                        {"role": "user", "content": "..."}]
            max_tokens: 生成的最大 token 数。
            temperature: 临时温度（不传则用默认值）。

        返回:
            生成的文本；调用失败时返回空字符串（上层会回退）。
        """
        # 拼接对话接口地址
        url = self.base_url + "/v1/chat/completions"
        # 构造请求头（Bearer 认证 + JSON）
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        # 构造请求体
        payload = {
            "model": self.model,                        # 模型名
            "messages": messages,                       # 对话消息
            "max_tokens": max_tokens,                   # 最大长度
            "temperature": temperature or self.temperature,  # 采样温度
            "stream": False,                            # 非流式
        }
        # 发送请求并取回 JSON 响应
        resp = net.post_json(url, headers, payload)
        # 从响应中提取生成的文本（OpenAI 标准结构）
        return resp["choices"][0]["message"]["content"].strip()

    def available(self) -> bool:
        """
        判断 LLM 是否配置完整、可能可用。

        返回:
            True 表示三个必要字段都不为空。
        """
        # 三个字段都要非空
        return bool(self.base_url and self.api_key and self.model)
