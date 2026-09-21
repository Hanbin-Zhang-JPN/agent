# -*- coding: utf-8 -*-
"""
答案生成器 generator
=====================

作用：根据「问题 + 检索到的上下文」，生成最终答案。

提供两种生成模式：
  1. 离线抽样式（默认，无需任何外部服务）
     - 从最相关的块里摘取包含关键信息的句子，组织成带引用的答案；
     - 好处：不依赖大模型，也能直观看到「检索到了什么」；
     - 适合：无 API Key 的场景、调试检索质量、做自动化测试。

  2. 大模型生成式（可选，需配置 LLM）
     - 把检索到的上下文 + 问题交给大模型，生成自然、完整的回答；
     - 提示词明确要求「只依据上下文回答、引用编号、不知道就说不知道」，
       以约束模型不编造（这是 RAG 降低幻觉的关键）。

对外统一入口：generate()，自动按配置选择模式。
"""

# 系统提示词模板：约束大模型只依据上下文回答
_SYSTEM_PROMPT = (
    "你是一个严谨的问答助手。请严格遵循以下规则：\n"
    "1. 只依据下方提供的【参考材料】回答，不要编造任何材料之外的内容；\n"
    "2. 回答中引用材料时，用 [编号] 标注来源（对应材料前的编号）；\n"
    "3. 如果材料中找不到答案，请直接说明“根据现有材料无法回答”；\n"
    "4. 用中文回答，简洁、准确、分点清晰。"
)


class Generator:
    """答案生成器：离线抽取 / 在线大模型 二选一。"""

    def __init__(self, cfg: dict, llm=None, mode: str = "auto"):
        """
        参数:
            cfg:  配置字典（含 llm 子配置）。
            llm:  可选的大模型客户端。
            mode: "auto"（有 LLM 用生成式，否则抽取式）/"extract"/"llm"。
        """
        # 保存配置
        self.cfg = cfg
        # 保存 LLM 客户端
        self.llm = llm
        # 记录生成模式
        self.mode = mode

    def generate(self, question: str, context: str, used: list) -> tuple:
        """
        生成答案。

        参数:
            question: 用户问题。
            context:  组装好的上下文文本。
            used:     实际选用的候选列表（用于抽取式与引用）。

        返回:
            (answer, used_llm)
              answer:   生成的答案文本。
              used_llm: 是否使用了 LLM（True/False）。
        """
        # 决定最终模式：auto 时看是否有可用的 LLM
        mode = self.mode
        if mode == "auto":
            # 有可用 LLM 就用生成式，否则抽取式
            mode = "llm" if (self.llm and self.llm.available()) else "extract"

        # 分派到对应实现
        if mode == "llm":
            return self._generate_with_llm(question, context), True
        return self._generate_extractive(question, used), False

    # ---------- 大模型生成式 ----------

    def _generate_with_llm(self, question: str, context: str) -> str:
        """
        用大模型生成答案。

        参数:
            question: 问题。
            context:  上下文文本。

        返回:
            生成的答案文本。
        """
        # 组装用户消息：参考材料 + 问题
        user_msg = f"【参考材料】\n{context}\n\n【问题】\n{question}"
        # 调用大模型
        answer = self.llm.chat([
            {"role": "system", "content": _SYSTEM_PROMPT},   # 约束规则
            {"role": "user", "content": user_msg},           # 材料 + 问题
        ], max_tokens=int(self.cfg.get("llm", {}).get("max_tokens", 1024)))
        # 若生成失败，回退到抽取式，保证永远有答案
        if not answer:
            return self._generate_extractive(question, [])
        # 返回生成的答案
        return answer

    # ---------- 离线抽样式 ----------

    def _generate_extractive(self, question: str, used: list) -> str:
        """
        离线抽样式回答：从最相关的块中抽取关键句并组织答案。

        原理：
          - 取 top-1 相关块全文作为答案主体；
          - 若该块无法覆盖问题关键词，再补充第二相关块；
          - 末尾附上来源引用，保证可溯源。

        参数:
            question: 问题。
            used:     选用的候选列表。

        返回:
            抽样式答案文本。
        """
        # 没有检索到任何材料时的兜底提示
        if not used:
            return "根据现有材料未检索到相关信息，请尝试更换问题或补充文档。"

        # 从最相关块中抽取包含问题关键词的句子
        key_sentences = self._extract_key_sentences(question, used[0].text)
        # 若关键句为空，则退回使用该块全文
        body = key_sentences if key_sentences else used[0].text
        # 若还有第二相关块且第一块过短，追加第二块的内容
        if len(used) > 1 and len(body) < 60:
            body += "\n" + used[1].text

        # 组织引用列表（文件名 + 块号）
        refs = []
        for i, c in enumerate(used, start=1):
            # 来源文件名
            src = c.meta.get("path", "未知来源")
            refs.append(f"[{i}] {src}")
        # 答案 = 内容 + 引用
        answer = f"{body}\n\n参考来源：\n" + "\n".join(refs)
        return answer

    @staticmethod
    def _extract_key_sentences(question: str, text: str) -> str:
        """
        从一段文本中，抽出「包含问题关键词」的句子。

        参数:
            question: 问题文本。
            text:     候选块文本。

        返回:
            抽出的句子拼接；无命中则返回空串。
        """
        # 延迟导入分词器
        from .tokenizer import tokenize
        # 问题关键词集合（去掉单字，避免误匹配）
        q_terms = {t for t in tokenize(question) if len(t) > 1}
        # 没有关键词时返回空
        if not q_terms:
            return ""
        # 按句子边界切分候选文本
        import re
        sents = re.split(r"(?<=[。！？!?；;])", text)
        # 保留命中关键词的句子
        hits = []
        for s in sents:
            # 该句的分词集合
            s_terms = set(tokenize(s))
            # 与关键词有交集才保留
            if s_terms & q_terms:
                hits.append(s.strip())
        # 拼接命中的句子（最多 3 句，控制长度）
        return "".join(hits[:3])
