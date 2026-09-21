# ============================================================
# 文本向量化：哈希 n-gram 嵌入（轻量"语义"向量，零依赖）
#
# 原理（hashing trick，与 fastText 同源的思路）：
#   - 每个词元算一个稳定整数哈希（用 zlib.crc32，跨进程一致）
#   - 用哈希值取模定位到向量的一维，把权重累加进去
#   - 用哈希的另一位比特决定正负号，让不同词元尽量正交、减少碰撞抵消
#   - 最后做 L2 归一化，使"余弦相似度"退化为"点积"，计算更简单更快
#
# 优点：无外部依赖、无需下载模型、结果确定可复现
# 局限：这是"字面/表记相似"而非真正的语义，正式场景可换真模型，见 README
# ============================================================

import math
import zlib


def hash_token(token):
    """把词元映射成稳定整数（跨进程、跨机器结果一致）"""
    return zlib.crc32(token.encode("utf-8"))       # crc32 天然稳定且快


def embed_tokens(tokens, dim=2048, idf=None, tf_weight=True):
    """把词元列表累加成固定维度向量（未归一化）"""
    vec = [0.0] * dim                              # 初始化全零向量
    tf = {}                                        # 统计每个词元的词频
    for t in tokens:
        tf[t] = tf.get(t, 0) + 1                   # 计数累加
    for t, c in tf.items():                        # 遍历去重后的词元
        h = hash_token(t)                          # 词元的稳定哈希
        idx = h % dim                              # 取模定位到某一维
        sign = 1.0 if (h >> 1) & 1 else -1.0       # 用第2位比特决定正负号
        w = 1.0 + math.log(c) if tf_weight else 1.0  # 词频权重 1+log(tf)
        if idf is not None:
            w *= idf.get(t, 0.0)                   # 乘 IDF：突出稀有词
        vec[idx] += sign * w                       # 累加到对应维度
    return vec


def normalize(vec):
    """L2 归一化：让向量长度为 1，之后余弦相似度 = 点积"""
    n = math.sqrt(sum(x * x for x in vec))         # 求向量长度
    if n == 0:                                     # 全零向量无法归一化
        return vec
    return [x / n for x in vec]                    # 每个分量除以长度


def dot(a, b):
    """两个已归一化向量的点积，即它们的余弦相似度"""
    return sum(x * y for x, y in zip(a, b))
