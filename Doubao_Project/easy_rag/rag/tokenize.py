# ============================================================
# 分词器：不依赖任何分词库（如 jieba），用规则自实现
#
# 设计思路：
#   - 英文/数字：按连续字符切成整词，统一转小写
#   - 中文：不做复杂分词，直接取"单字 + 相邻二字组"
#     二字组能抓住常见词组（"检索"、"向量"），召回效果接近分词
#
# 优点：零依赖、速度快、逻辑一眼看懂，且对未知新词天然免疫
# ============================================================

import re

# 匹配连续的英文/数字，作为英文词元
_EN_WORD = re.compile(r"[A-Za-z0-9]+")


def is_cjk(ch):
    """判断单个字符是否属于中日韩文字区"""
    cp = ord(ch)                                  # 取字符的 Unicode 码点
    # 常用汉字 + 扩展A + 日文假名 + 韩文音节
    return (0x4E00 <= cp <= 0x9FFF) or (0x3400 <= cp <= 0x4DBF) \
        or (0x3040 <= cp <= 0x30FF) or (0xAC00 <= cp <= 0xD7AF)


def tokenize(text):
    """把一段文本切成词元列表（英文整词 + 中文单字/二字组）"""
    tokens = []                                   # 最终词元列表
    # 1) 先取出所有英文/数字词
    for m in _EN_WORD.finditer(text):
        tokens.append(m.group().lower())          # 英文统一小写，方便匹配
    # 2) 再扫描中文：把连续中文攒进缓冲区，攒满一段就切一次
    cjk_buf = []                                  # 连续中文缓冲区
    for ch in text:
        if is_cjk(ch):
            cjk_buf.append(ch)                    # 是中文就先存进缓冲区
        else:
            if cjk_buf:                           # 遇到非中文，说明一段结束
                tokens.extend(_cjk_tokens(cjk_buf))
                cjk_buf = []                      # 清空缓冲区，等待下一段
    if cjk_buf:                                   # 收尾：处理末尾剩余中文
        tokens.extend(_cjk_tokens(cjk_buf))
    return tokens


def _cjk_tokens(seq):
    """把一串连续中文切成"单字 + 相邻二字组"的列表"""
    out = list(seq)                               # 每个单字是一个词元
    for i in range(len(seq) - 1):
        out.append(seq[i] + seq[i + 1])           # 相邻两字合成一个词元
    return out
