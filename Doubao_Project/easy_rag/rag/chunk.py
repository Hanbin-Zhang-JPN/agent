# ============================================================
# 文档切块：把长文档切成适合检索和喂给大模型的小段
#
# 策略：句子级边界 + 滑动重叠
#   - 先把文本按句末标点 / 换行切成句子
#   - 句子尽量聚到目标大小，塞不下就收尾开新块
#   - 新块开头带上旧块尾部 overlap 个字符，防止语义被切碎
#   - 单个超长句子单独硬切，不拖累整体块大小
# ============================================================

import re

# 按句末标点或换行切分句子（(?<=...) 表示保留这些标点本身）
_SENT_SPLIT = re.compile(r"(?<=[。！？!?；;\n])")


def split_sentences(text):
    """把文本切成句子列表，并去掉空白句"""
    parts = _SENT_SPLIT.split(text)               # 用正则切分
    return [p.strip() for p in parts if p.strip()]  # 去首尾空白、过滤空串


def chunk_text(text, size=500, overlap=100):
    """把整段文本切成带重叠的块列表"""
    sentences = split_sentences(text)             # 先切成句子
    chunks = []                                   # 结果块列表
    cur = ""                                      # 正在累积的当前块
    for s in sentences:
        # 情况A：单句本身就超过块大小，先收尾当前块，再硬切这个长句
        if len(s) > size:
            if cur:
                chunks.append(cur)                # 收尾当前块
                cur = ""
            for i in range(0, len(s), size):      # 按固定长度硬切
                chunks.append(s[i:i + size])
            continue                              # 处理下一个句子
        # 情况B：当前块还能塞下这个句子，直接拼接
        if len(cur) + len(s) <= size:
            cur += s
        # 情况C：塞不下了，收尾旧块，并用重叠字符开新块
        else:
            if cur:
                chunks.append(cur)
            head = cur[-overlap:] if overlap > 0 else ""  # 取旧块尾部做衔接
            cur = head + s                        # 新块以重叠开头
    if cur:                                       # 收尾最后一块
        chunks.append(cur)
    # 过滤掉空块，返回最终结果
    return [c for c in chunks if c.strip()]
