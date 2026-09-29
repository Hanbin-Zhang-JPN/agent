#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""只用 Python 标准库，运行一个能训练的小型 Transformer 语言模型。

运行：python3 learn_llm_from_scratch.py
查看术语：python3 learn_llm_from_scratch.py --glossary
改变解码：python3 learn_llm_from_scratch.py --top-k 5 --temperature 0.7
核对反向传播：python3 learn_llm_from_scratch.py --check-grad --steps 0
需要 Python 3.10 或更高版本；无需安装第三方库。

不熟悉术语时，先看下方 GLOSSARY，或运行 --glossary。脚本从头计算字节级 BPE、嵌入、位置编码、
多头因果自注意力、前馈网络、层归一化、交叉熵、反向传播、Adam 和逐 token 生成。
训练目标与 GPT 一类 decoder-only LLM 相同。模型只有一层，维度和语料也小；
代码没有实现 dropout、批处理或加速用的矩阵计算。

建议阅读顺序：
  1. 先运行脚本，看终端输出的 ①～⑥。
  2. 再读 main()，了解数据怎样流过各个函数。
  3. 接着读 ByteBPE 和 forward()，最后才读 loss_and_backward()。

整体路线：文字 → token ID → token/位置向量 → 注意力 → 前馈网络
        → 每个候选 token 的原始分数(logits) → softmax 概率 → 下一个 token。
训练时把预测概率和已知答案比较，再让梯度沿相反方向更新参数；
生成时没有已知答案，只能把新选出的 token 接回输入，继续预测。

给 Python 初学者的记号提示：
  list[int] 表示“由整数构成的列表”，只是类型提示，不会改变运行方式。
  self 表示当前对象；例如 self.emb 就是这个模型自己的嵌入参数。
  a[start:end] 取列表从 start 到 end-1 的元素，不包含 end。
  enumerate(xs) 会同时给出下标和元素；zip(a, b) 会把两个列表配对。
  [表达式 for x in 列表] 是列表推导式，可理解为“逐个算出并收集结果”。

数学记号：t=输入 token 数，d=向量宽度，V=词表大小，h=注意力头数。
虽然代码用普通列表和循环，文中的 [t, d] 仍表示“t 行，每行 d 个数”。
向量要作为整体看。单独拿出某一维，通常解释不出固定的词义。
"""

from __future__ import annotations

import argparse
import math
import random
from collections import Counter


# 这份速查表可以单独打印：python3 learn_llm_from_scratch.py --glossary
# 同一个词在代码里第一次出现时，附近通常还有针对那一步的解释。
GLOSSARY = """术语速查

文字和数据
  语料：拿来训练的文本。本脚本的语料就是下方 CORPUS 中的句子。
  UTF-8：把文字表示成字节的规则。一个常见汉字通常占 3 个字节。
  token：模型一次处理的文本片段。它可能是一个字节、汉字的一部分或几个字。
  ID / 词表：每种 token 有一个整数 ID；词表记录 ID 对应哪些字节。
  BPE：不断把语料中最常挨在一起的两个片段合成新 token 的分词方法。
  EOS：表示一句文本结束的特殊 token，本身不对应普通文字。

模型怎样计算
  参数：训练时会改变的数字，例如嵌入表、矩阵和偏置。
  向量 / 维度：排成一列的数字；[0.2, -0.1] 是一个 2 维向量。
  矩阵：由多行向量组成的数字表。模型用矩阵把输入向量换成新的向量。
  嵌入：按 token ID 从参数表里取出的向量；位置也有自己的向量。
  位置编码：让模型区分文字顺序的信息；这里把位置向量加到 token 向量上。
  上下文：预测当前答案时模型看得到的前文；context 限制最多看多少 token。
  Transformer：用注意力汇总不同位置的信息，再逐位置经过前馈网络的模型结构。
  decoder-only：只根据已出现的 token 预测后面的 token；这里采用 GPT 类模型的结构。
  Q / K / V：Query 与各 Key 比较得到权重；Value 是按权重取回的向量。
  注意力：当前位置给可见的旧位置分配权重，取回它们的 Value 并加权求和。
  多头：把 Q/K/V 分成几段，各段独立计算注意力，最后合起来。
  因果遮罩：让位置 i 看不到 i 之后的 token，训练时便不会偷看答案。
  层归一化：对一个 token 的向量做缩放，控制各维数值的分布。
  残差连接：把某一层的输入加到该层输出上，保留一条直接传递信息的路径。
  前馈网络：对每个位置分别做线性变换和非线性变换；这里用 GELU 激活。
  GELU：一种非线性函数；输入翻倍时，输出不一定跟着翻倍。
  logits：模型为词表中每个候选 token 给出的原始分数，还不是概率。
  softmax：把一组分数变成总和为 1 的概率；此处分别用于注意力和输出。

训练和生成
  交叉熵 / 损失：正确 token 的概率为 p 时，单次损失是 -log(p)；p 越大，损失越小。
  梯度：参数增大一点时损失如何变化；梯度为负表示此时增大参数会降低损失。
  链式法则：把各层之间的影响逐段相乘，求早期参数对最终损失的影响。
  反向传播：按计算的反方向使用链式法则，把梯度传回每一层。
  Adam：根据当前和过去的梯度更新参数的一种算法；这里还会裁剪过大的梯度。
  batch：一次参数更新使用多少段训练样本；这里每次只用 1 段。
  dropout：训练时随机把部分中间值置零的做法；此脚本没有实现。
  困惑度：交叉熵损失取指数后的数，常用于衡量下一 token 预测。
  数值微分：给一个参数加减微小量，用损失变化近似求出梯度。
  自回归：生成一个 token，把它接在已有序列后面，再预测下一个。
  top-k：生成时只考虑分数最高的 k 个候选；k=1 就是每次选最高分。
  temperature：生成时用它缩放 logits；低于 1 时分布更集中。
  KV cache：生成时保存已算过的 Key 和 Value，减少重复计算；此脚本没有使用。
"""


# 语料库：每个字符串是一条训练文本。* 8 表示把整个列表重复八次，
# 训练时会反复抽到这些句子。重复八遍只增加抽样机会，不增加句型。
CORPUS = [
    "春天来了，花开了。",
    "春天来了，鸟叫了。",
    "夏天来了，天气热了。",
    "秋天来了，叶子黄了。",
    "冬天来了，雪花落了。",
    "春天的花是红色的。",
    "秋天的叶子是黄色的。",
    "冬天的雪是白色的。",
    "小猫喜欢晒太阳。",
    "小狗喜欢在院子里跑。",
    "小猫看见了小狗。",
    "小狗看见了小猫。",
] * 8


class ByteBPE:
    """字节级 BPE：把高频相邻片段逐步合并成 token。

    最初的 256 个 token 各代表一种字节，ID 为 0..255。
    tokenizer 是“把文字变成 token ID”的程序。主流 tokenizer 往往还会先按
    预设规则切分文字，或对空格做特殊处理。
    此处保留 BPE 的核心算法；每条训练文本独立统计，不跨文本边界合并。
    合并越多，常见文本通常会用更少 token 表示，词表和输出层也会变大。
    BPE 负责把文字映射成 ID；模型训练才会改变这些 ID 对应的向量。
    """

    def __init__(self, merges: list[tuple[int, int]]):
        # merges 按训练先后保存合并规则，如 (65, 66) 表示把字节 A、B 合成新 token。
        self.merges = merges
        # bytes([i]) 生成一个只含字节 i 的 bytes 对象。开始时 0～255 各有一个 token。
        self.pieces = [bytes([i]) for i in range(256)]
        for left, right in merges:
            # 新 token 的字节内容 = 左 token 的字节 + 右 token 的字节。
            self.pieces.append(self.pieces[left] + self.pieces[right])
        self.eos_id = len(self.pieces)  # EOS 表示文本结束，占一个独立 ID。

    @classmethod
    def train(cls, texts: list[str], num_merges: int) -> "ByteBPE":
        """从训练文本学合并规则；cls(...) 相当于创建一个 ByteBPE 对象。"""
        # UTF-8 将汉字拆成字节。例如“春”通常是三个字节，之后 BPE 才可能把它们合回去。
        sequences = [list(s.encode("utf-8")) for s in texts]
        merges: list[tuple[int, int]] = []
        for _ in range(num_merges):
            # zip(seq, seq[1:]) 生成每对相邻 token；Counter 统计它们出现的次数。
            counts = Counter(pair for seq in sequences for pair in zip(seq, seq[1:]))
            if not counts:
                break
            # 频数相同取字典序最小的 pair，保证每次运行得到同一词表。
            pair = min(counts, key=lambda p: (-counts[p], p))
            # 最初的 ID 是 0～255，第一个合并产生 256，第二个产生 257，依此类推。
            new_id = 256 + len(merges)
            merges.append(pair)
            # 学到新规则后，必须更新所有训练文本，再统计下一轮相邻对。
            sequences = [cls._replace(seq, pair, new_id) for seq in sequences]
        return cls(merges)

    @staticmethod
    def _replace(seq: list[int], pair: tuple[int, int], new_id: int) -> list[int]:
        """从左到右扫描；遇到指定相邻对，就用新 ID 代替两个旧 ID。"""
        out = []
        i = 0
        while i < len(seq):
            if i + 1 < len(seq) and (seq[i], seq[i + 1]) == pair:
                out.append(new_id)
                # 刚合并了两个位置，所以下次从 i+2 继续。
                i += 2
            else:
                out.append(seq[i])
                i += 1
        return out

    def encode(self, text: str) -> list[int]:
        """把任意字符串变成 token ID；未在训练语料出现的文字仍能由字节表示。"""
        seq = list(text.encode("utf-8"))
        # 训练时新 pair 的 ID 按顺序产生；编码时须按相同顺序合并。
        for i, pair in enumerate(self.merges):
            seq = self._replace(seq, pair, 256 + i)
        return seq

    def decode(self, ids: list[int]) -> str:
        """把 token 对应的字节依次拼起来，再按 UTF-8 转回字符串。"""
        raw = b"".join(self.pieces[i] for i in ids if i != self.eos_id)
        # 一个 token 可能只含汉字的部分字节。生成结果若拼不成合法 UTF-8，
        # decode 会显示替换符 �；原来的 token ID 不受影响。
        return raw.decode("utf-8", errors="replace")


def dot(a: list[float], b: list[float]) -> float:
    """向量点积：对应位置相乘再求和，如 [1,2]·[3,4]=11。"""
    return sum(x * y for x, y in zip(a, b))


def cosine(a: list[float], b: list[float]) -> float:
    """点积除以两个向量的长度；1 接近同方向，0 接近垂直。

    这个函数只用于查看向量。模型预测时使用注意力和输出层中的点积。
    分母的 1e-12 是很小的保护值，避免零向量造成除零错误。
    """
    return dot(a, b) / (math.sqrt(dot(a, a) * dot(b, b)) + 1e-12)


def softmax(values: list[float]) -> list[float]:
    """把分数变成概率。概率非负，全部加起来等于 1。"""
    # 减最大值不改变概率，却可防止 exp 溢出。
    peak = max(values)
    exps = [math.exp(v - peak) for v in values]
    total = sum(exps)
    # 例如 [2, 1] 会变成约 [0.73, 0.27]；高分得到较高概率。
    return [v / total for v in exps]


def gelu(x: float) -> float:
    """GELU 是一种激活函数：让输入和输出不再保持简单的线性关系。"""
    return 0.5 * x * (1.0 + math.erf(x / math.sqrt(2.0)))


def gelu_grad(x: float) -> float:
    """GELU 对输入 x 的导数，供反向传播使用。"""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0))) + x * math.exp(-x * x / 2.0) / math.sqrt(2.0 * math.pi)


class Parameter:
    """一组训练时会改变的数字，以及它们的梯度和 Adam 要保存的历史值。"""

    def __init__(self, values: list[float]):
        # data 是当前参数值；grad 是损失对参数的导数，训练时据此更新 data。
        self.data = values
        self.grad = [0.0] * len(values)
        # m、v 分别保存 Adam 的梯度移动平均和平方梯度移动平均。
        self.m = [0.0] * len(values)
        self.v = [0.0] * len(values)


def linear(x: list[float], w: Parameter, out_dim: int, bias: Parameter | None = None) -> list[float]:
    """线性层 y=xW+b；W 按 [输入维, 输出维] 展平成一个列表。

    例如输入维=2、输出维=3 时，W 实际有 6 个数。第 i 行第 j 列
    放在列表的 i*3+j 处。bias（偏置）是加到输出上的可训练数字；
    没有 bias 时，从全零输出开始累加。
    """
    result = bias.data.copy() if bias else [0.0] * out_dim
    for i, xi in enumerate(x):
        row = i * out_dim
        for j in range(out_dim):
            # 输出的第 j 维收到输入第 i 维的贡献 xi*W[i,j]。
            result[j] += xi * w.data[row + j]
    return result


def linear_backward(x: list[float], w: Parameter, dy: list[float], bias: Parameter | None = None) -> list[float]:
    """线性层的反向传播：已知输出梯度 dy，求输入梯度 dx，并累加参数梯度。

    “梯度”可以理解为：某个数略微改变时，最终损失会怎样改变。
    这里反复使用的“链式法则”是：如果损失受 y 影响，而 y 又受 x 影响，
    就把这两段影响相乘，求出损失对 x 的影响。
    同一个参数可能被多个 token 使用，所以这里用 += 累加，而不是覆盖。
    """
    out_dim = len(dy)
    dx = [0.0] * len(x)
    if bias:
        for j, delta in enumerate(dy):
            bias.grad[j] += delta
    for i, xi in enumerate(x):
        row = i * out_dim
        for j, delta in enumerate(dy):
            # y[j] 包含 x[i]*W[i,j]，因此 dL/dW[i,j]=x[i]*dL/dy[j]。
            w.grad[row + j] += xi * delta
            # 同理，dL/dx[i] 需要把所有输出维 j 的贡献加起来。
            dx[i] += w.data[row + j] * delta
    return dx


def layer_norm(x: list[float], gamma: Parameter, beta: Parameter):
    """对一个 token 的向量求均值和方差，再缩放到较稳定的数值范围。"""
    mean = sum(x) / len(x)
    var = sum((v - mean) ** 2 for v in x) / len(x)
    # 方差可能接近 0；1e-5 防止除零。inv_std 是“标准差的倒数”。
    inv_std = 1.0 / math.sqrt(var + 1e-5)
    normalized = [(v - mean) * inv_std for v in x]
    # gamma、beta 初值分别为 1 和 0，但训练中会变化。
    # 第二个返回值是反向传播要用的中间结果，称为 cache（缓存）。
    return [normalized[i] * gamma.data[i] + beta.data[i] for i in range(len(x))], (normalized, inv_std)


def layer_norm_backward(dy: list[float], cache, gamma: Parameter, beta: Parameter) -> list[float]:
    """把归一化层的输出梯度传回输入，同时累计 gamma、beta 的梯度。"""
    normalized, inv_std = cache
    n = len(dy)
    dn = [0.0] * n
    for i in range(n):
        # 输出是 normalized[i]*gamma[i]+beta[i]。
        gamma.grad[i] += dy[i] * normalized[i]
        beta.grad[i] += dy[i]
        dn[i] = dy[i] * gamma.data[i]
    # 均值和方差都依赖每个输入分量，不能只乘 1/std。
    mean_dn = sum(dn) / n
    mean_dn_n = dot(dn, normalized) / n
    return [(dn[i] - mean_dn - normalized[i] * mean_dn_n) * inv_std for i in range(n)]


class TinyTransformer:
    """单层、两头、pre-LN 的自回归 Transformer，完整训练全部参数。

    pre-LN 指先做层归一化（LayerNorm），再送入注意力或前馈网络。
    主要数据形状：输入 ids=[t]；隐藏状态=[t,d]；输出 logits=[t,V]。
    位置采用可学习的绝对位置向量；有些模型改用 RoPE（旋转位置编码），
    将位置信息放进注意力中的 Q/K。两种做法都让模型区分 token 顺序。
    """

    def __init__(self, vocab: int, context: int, width: int = 16, heads: int = 2, ff_width: int = 32, seed: int = 7):
        if width % heads:
            raise ValueError("width 必须能被 heads 整除")
        self.vocab, self.context, self.width = vocab, context, width
        self.heads, self.head_dim, self.ff_width = heads, width // heads, ff_width
        # 独立随机数生成器 + 固定种子：每次运行得到同样的初始模型。
        rng = random.Random(seed)
        self.params: list[Parameter] = []

        def param(size: int, std: float = 0.0, fill: float | None = None) -> Parameter:
            # fill 给定时全部填相同数字；否则从均值 0、标准差 std 的正态分布抽样。
            vals = [fill if fill is not None else rng.gauss(0.0, std) for _ in range(size)]
            p = Parameter(vals)
            self.params.append(p)
            return p

        d = width
        # 嵌入矩阵有 V 行、d 列；token ID 就是要查的行号。
        self.emb = param(vocab * d, 0.12)
        self.pos = param(context * d, 0.08)  # 可学习的绝对位置向量。
        # ln1/ln2/ln3 是三处层归一化，每处都有 gamma(g) 和 beta(b)。
        self.ln1_g, self.ln1_b = param(d, fill=1.0), param(d, fill=0.0)
        # “投影”就是乘以一个可训练矩阵。三个矩阵分别算出 Query、Key、Value。
        self.wq = param(d * d, 1 / math.sqrt(d))
        self.wk = param(d * d, 1 / math.sqrt(d))
        self.wv = param(d * d, 1 / math.sqrt(d))
        self.wo = param(d * d, 1 / math.sqrt(d))
        self.ln2_g, self.ln2_b = param(d, fill=1.0), param(d, fill=0.0)
        self.w1, self.b1 = param(d * ff_width, 1 / math.sqrt(d)), param(ff_width, fill=0.0)
        self.w2, self.b2 = param(ff_width * d, 1 / math.sqrt(ff_width)), param(d, fill=0.0)
        self.ln3_g, self.ln3_b = param(d, fill=1.0), param(d, fill=0.0)
        # LM head 把 d 维隐藏向量变成 V 个分数；一个分数对应一个候选 token。
        self.lm, self.lm_b = param(d * vocab, 0.02), param(vocab, fill=0.0)
        self.step_number = 0

    def forward(self, ids: list[int]):
        """前向计算。返回词表分数 logits，以及反向传播需要的 cache。"""
        if not 1 <= len(ids) <= self.context:
            raise ValueError("输入长度必须在 1 到 context 之间")
        d, t = self.width, len(ids)
        # x0 的形状是 [t,d]。位置 0 即使和位置 1 用同一 token，位置向量也不同。
        # token*d+c 是展平矩阵中第 token 行、第 c 列的下标。
        x0 = [[self.emb.data[token * d + c] + self.pos.data[i * d + c] for c in range(d)]
              for i, token in enumerate(ids)]
        a, ln1 = [], []
        for x in x0:
            normalized, saved = layer_norm(x, self.ln1_g, self.ln1_b)
            a.append(normalized)
            ln1.append(saved)
        # q、k、v 各有 t 个 d 维向量。Query 用来与历史位置的 Key 比较；
        # 算出的权重再对历史位置的 Value 求加权和。
        q = [linear(x, self.wq, d) for x in a]
        k = [linear(x, self.wk, d) for x in a]
        v = [linear(x, self.wv, d) for x in a]
        z = [[0.0] * d for _ in ids]
        weights = []
        for head in range(self.heads):
            # 每个头使用向量中不重叠的一段；比如 d=16、2 头时各用 8 维。
            start, end = head * self.head_dim, (head + 1) * self.head_dim
            head_weights = []
            for i in range(t):
                # j 只到 i，这就是因果遮罩：位置 i 不会读取未来位置。
                # 用 √头维度 缩放，避免维度较大时点积过大、softmax 过于尖锐。
                scores = [dot(q[i][start:end], k[j][start:end]) / math.sqrt(self.head_dim)
                          for j in range(i + 1)]
                # 此处 softmax 是沿“可看的历史位置 j”进行，得到注意力权重。
                # 最后预测 token 时还有另一次 softmax，那次是沿词表 ID 进行。
                probs = softmax(scores)
                # head_weights[i][j] 是位置 i 对位置 j 的注意力权重。
                head_weights.append(probs)
                for j, probability in enumerate(probs):
                    for c in range(start, end):
                        # 用概率给旧位置的 Value 加权，得到当前位置的新信息。
                        z[i][c] += probability * v[j][c]
            weights.append(head_weights)
        o = [linear(zi, self.wo, d) for zi in z]
        # 残差连接让原始信息有直接路径传到下一层，也帮助梯度传回早期层。
        x1 = [[x0[i][c] + o[i][c] for c in range(d)] for i in range(t)]
        b, ln2 = [], []
        for x in x1:
            normalized, saved = layer_norm(x, self.ln2_g, self.ln2_b)
            b.append(normalized)
            ln2.append(saved)
        # 前馈网络对每个位置单独计算：d → ff_width → d。这里不混合位置。
        hidden = [linear(x, self.w1, self.ff_width, self.b1) for x in b]
        activated = [[gelu(value) for value in row] for row in hidden]
        f = [linear(row, self.w2, d, self.b2) for row in activated]
        x2 = [[x1[i][c] + f[i][c] for c in range(d)] for i in range(t)]
        c, ln3 = [], []
        for x in x2:
            normalized, saved = layer_norm(x, self.ln3_g, self.ln3_b)
            c.append(normalized)
            ln3.append(saved)
        logits = [linear(row, self.lm, self.vocab, self.lm_b) for row in c]
        # logits 是原始分数。训练或生成时再用 softmax 转成概率。
        # 每个位置都会输出一整行 V 个分数；第 i 行预测的是 ids[i] 后的 token。
        # cache 留住前向过程的中间值，反向传播会按相反顺序使用。
        cache = (ids, x0, a, ln1, q, k, v, z, weights, x1, b, ln2, hidden,
                 activated, x2, c, ln3)
        return logits, cache

    def loss_and_backward(self, ids: list[int], targets: list[int]) -> float:
        """算平均交叉熵，并求损失对全部可学习参数的梯度。

        如果 ids=[A,B,C]，targets=[B,C,D]，位置 0 用 A 预测 B，
        位置 1 用 A、B 预测 C，位置 2 用 A、B、C 预测 D。
        反向传播从 logits 开始，沿前向计算的反方向逐层走回嵌入。
        """
        if len(ids) != len(targets):
            raise ValueError("ids 和 targets 长度必须相同")
        # 每次训练步都重新计算梯度；保留上一轮梯度会错误地混在一起。
        for p in self.params:
            p.grad = [0.0] * len(p.data)
        logits, cache = self.forward(ids)
        (ids, x0, a, ln1, q, k, v, z, weights, x1, b, ln2, hidden,
         activated, x2, c, ln3) = cache
        t, d = len(ids), self.width
        dx2 = []
        loss = 0.0
        for i, row in enumerate(logits):
            # row 有 V 个分数，softmax 后才是“下一个 token 是各 ID”的概率。
            probabilities = softmax(row)
            # 正确答案概率越小，-log(概率) 越大；/t 得到各位置平均损失。
            loss -= math.log(max(probabilities[targets[i]], 1e-300)) / t
            # 对每个候选 ID，梯度 = 预测概率 - 正确答案的 one-hot 值。
            # 只有 targets[i] 对应的那一项要减 1。
            probabilities[targets[i]] -= 1.0
            dlogits = [p / t for p in probabilities]  # softmax + 交叉熵的导数。
            # 依次传回语言模型头、最终层归一化，得到 dL/dx2。
            dc = linear_backward(c[i], self.lm, dlogits, self.lm_b)
            dx2.append(layer_norm_backward(dc, ln3[i], self.ln3_g, self.ln3_b))

        dx1 = []
        for i in range(t):
            # 前向是 x2 = x1 + W2(GELU(W1(LN(x1))))。
            # 所以梯度一条路直通残差 x1，另一条路倒着穿过 W2、GELU、W1、LN。
            dg = linear_backward(activated[i], self.w2, dx2[i], self.b2)
            dh = [dg[j] * gelu_grad(hidden[i][j]) for j in range(self.ff_width)]
            db = linear_backward(b[i], self.w1, dh, self.b1)
            from_ff = layer_norm_backward(db, ln2[i], self.ln2_g, self.ln2_b)
            # 两条路径的梯度相加：这就是残差连接的反向传播。
            dx1.append([dx2[i][j] + from_ff[j] for j in range(d)])

        # 从注意力的输出反传：先经 Wo，再经加权求和、softmax 和 QKᵀ。
        dz = [linear_backward(z[i], self.wo, dx1[i]) for i in range(t)]
        # 三组梯度形状都是 [t,d]，分别对应 Query、Key、Value。
        dq = [[0.0] * d for _ in range(t)]
        dk = [[0.0] * d for _ in range(t)]
        dv = [[0.0] * d for _ in range(t)]
        for head in range(self.heads):
            start, end = head * self.head_dim, (head + 1) * self.head_dim
            scale = 1.0 / math.sqrt(self.head_dim)
            for i in range(t):
                probs = weights[head][i]
                dp = []
                for j in range(i + 1):
                    # z[i] = Σ_j probs[j] * v[j]，故权重的梯度是 dz[i]·v[j]。
                    dp.append(dot(dz[i][start:end], v[j][start:end]))
                    for cidx in range(start, end):
                        # 同一 Value 可被后面多个位置使用，故用 += 累加。
                        dv[j][cidx] += probs[j] * dz[i][cidx]
                # softmax 的各输出互相影响，不能把每项当独立函数求导。
                # 对分数 s_j 的导数 = p_j*(dp_j - Σ_k p_k*dp_k)。
                weighted_mean = dot(dp, probs)
                for j in range(i + 1):
                    ds = probs[j] * (dp[j] - weighted_mean) * scale
                    for cidx in range(start, end):
                        # score(i,j) = q[i]·k[j]/√头维度，再传回 q 和 k。
                        dq[i][cidx] += ds * k[j][cidx]
                        dk[j][cidx] += ds * q[i][cidx]

        for i, token in enumerate(ids):
            # q、k、v 都由 a[i] 投影而来，三条梯度路径需要相加。
            daq = linear_backward(a[i], self.wq, dq[i])
            dak = linear_backward(a[i], self.wk, dk[i])
            dav = linear_backward(a[i], self.wv, dv[i])
            da = [daq[j] + dak[j] + dav[j] for j in range(d)]
            from_attention = layer_norm_backward(da, ln1[i], self.ln1_g, self.ln1_b)
            for j in range(d):
                gradient = dx1[i][j] + from_attention[j]  # 注意力残差也传梯度。
                # x0 = token 嵌入 + 位置嵌入，因此两者都收到相同的梯度。
                # 相同 token 在序列里出现多次时，嵌入梯度会继续累加。
                self.emb.grad[token * d + j] += gradient
                self.pos.grad[i * d + j] += gradient
        return loss

    def adam_step(self, lr: float = 0.003, clip: float = 1.0):
        """根据刚算出的梯度更新所有参数。

        lr 是学习率，决定每次移动多大；clip 限制整体梯度过大。
        梯度裁剪是把过大的梯度整体缩小，避免一次更新走得太远。
        这里的学习率固定；大型训练任务通常会在训练过程中调整学习率。
        """
        self.step_number += 1
        # 把所有参数梯度看成一条很长的向量，计算其欧氏长度。
        norm = math.sqrt(sum(g * g for p in self.params for g in p.grad))
        # 范数不超过 clip 时 factor=1；超过时等比例缩小所有梯度。
        factor = min(1.0, clip / (norm + 1e-12))
        beta1, beta2 = 0.9, 0.999
        for p in self.params:
            for i, raw_gradient in enumerate(p.grad):
                g = raw_gradient * factor
                # m 平滑梯度方向；v 平滑梯度的平方，帮助调整各参数的步长。
                p.m[i] = beta1 * p.m[i] + (1 - beta1) * g
                p.v[i] = beta2 * p.v[i] + (1 - beta2) * g * g
                # 刚开始的移动平均偏向 0，除以对应系数做偏差修正。
                m_hat = p.m[i] / (1 - beta1 ** self.step_number)
                v_hat = p.v[i] / (1 - beta2 ** self.step_number)
                # 沿负梯度方向移动，让损失倾向下降。
                p.data[i] -= lr * m_hat / (math.sqrt(v_hat) + 1e-8)
        return norm

    def generate(self, prefix: list[int], count: int, eos: int, rng: random.Random,
                 temperature: float = 0.8, top_k: int = 1) -> list[int]:
        """从提示词开始，最多再产生 count 个 token。

        top_k=1 每次取分数最高的 token，叫贪心解码；更大的 top_k 会在候选中抽样。
        temperature 是采样温度：把每个分数除以它，再算概率。低于 1 时
        高分 token 更占优势，高于 1 时各 token 的概率更接近。
        """
        if not prefix or temperature <= 0 or top_k < 1:
            raise ValueError("prefix 不能为空，temperature 和 top_k 必须大于 0")
        result = prefix.copy()
        for _ in range(count):
            # 每次只读取最后 context 个 token。KV cache 会保存前几步算好的
            # Key 和 Value，避免每生成一个 token 就重新算整段前文；这里直接重算。
            logits, _ = self.forward(result[-self.context:])
            # forward 为输入的每个位置都算分数；生成只用最后一个位置。
            row = logits[-1]
            # sorted(..., reverse=True) 从高分排到低分，再用 [:top_k] 截取前 k 个。
            choices = sorted(range(self.vocab), key=lambda i: row[i], reverse=True)[:top_k]
            probabilities = softmax([row[i] / temperature for i in choices])
            picked = rng.choices(choices, weights=probabilities, k=1)[0]
            # EOS 表示“这段文本结束”，不属于要展示的正文。
            if picked == eos:
                break
            result.append(picked)
        return result


def gradient_check(model: TinyTransformer, ids: list[int], targets: list[int]):
    """用数值微分检查手写导数，避免代码看似能训练但梯度实际有错。

    数值微分：对一个参数分别加、减很小的 eps，看损失改变多少，
    用两次损失之差估算导数，再与反向传播的结果比较。
    数值微分每查一个参数都要额外运行两次前向，不能用于完整模型训练。
    """
    model.loss_and_backward(ids, targets)
    # 每类关键运算抽查一个参数；这是抽样检查，不等于穷举所有参数。
    checks = [("词嵌入", model.emb, ids[0] * model.width),
              ("位置嵌入", model.pos, 0), ("第一处层归一化", model.ln1_g, 0),
              ("查询矩阵", model.wq, 0), ("键矩阵", model.wk, 0),
              ("值矩阵", model.wv, 0), ("注意力输出", model.wo, 0),
              ("前馈网络第一层", model.w1, 0), ("前馈网络第二层", model.w2, 0),
              ("最终层归一化", model.ln3_g, 0), ("语言模型头", model.lm, 0)]
    for label, p, index in checks:
        analytical = p.grad[index]
        original = p.data[index]
        eps = 1e-4
        p.data[index] = original + eps
        plus = _loss_only(model, ids, targets)
        p.data[index] = original - eps
        minus = _loss_only(model, ids, targets)
        # 检查后把参数恢复，后续训练才能从原来的模型继续。
        p.data[index] = original
        numerical = (plus - minus) / (2 * eps)
        error = abs(analytical - numerical) / max(1e-6, abs(analytical) + abs(numerical))
        print(f"  {label}: 解析={analytical:+.6e}, 数值={numerical:+.6e}, 相对误差={error:.2e}")
        if error > 1e-3:
            raise AssertionError(f"{label} 的反向传播核对失败")


def _loss_only(model: TinyTransformer, ids: list[int], targets: list[int]) -> float:
    """只算损失、不算梯度，供训练前后对比和数值微分使用。"""
    logits, _ = model.forward(ids)
    return sum(-math.log(max(softmax(row)[target], 1e-300)) for row, target in zip(logits, targets)) / len(ids)


def show_next_token_predictions(model: TinyTransformer, tokenizer: ByteBPE, prompt: str, limit: int = 3):
    """打印给定前缀后概率最高的几个 token，连接 logits 与可见文字。

    这里显示的是“紧接着的一个 token”，不是完整句子的概率。
    某个 token 若只含汉字的一部分 UTF-8 字节，就显示 bytes 的写法。
    """
    ids = tokenizer.encode(prompt)
    if not ids:
        raise ValueError("用于查看预测的 prompt 不能为空")
    logits, _ = model.forward(ids[-model.context:])
    probabilities = softmax(logits[-1])
    best_ids = sorted(range(model.vocab), key=lambda i: probabilities[i], reverse=True)[:limit]
    print(f"在“{prompt}”后，概率最高的 {limit} 个下一个 token：")
    for token_id in best_ids:
        if token_id == tokenizer.eos_id:
            label = "<EOS>"
        else:
            piece = tokenizer.pieces[token_id]
            try:
                label = piece.decode("utf-8")
            except UnicodeDecodeError:
                # 单个 token 可以不是完整汉字；如 b'\\xe7' 是某汉字的起始字节。
                label = repr(piece)
        print(f"  ID {token_id:>3} | {label!r} | 概率 {probabilities[token_id]:.3f}")


def text_loss(model: TinyTransformer, token_ids: list[int]) -> float:
    """计算一段文本逐 token 的平均预测损失，长文本也能处理。

    每次最多让模型看到 context 个已有 token，然后预测紧接着的一个 token。
    第一个 token 前没有给定上下文，因此不计入本函数的平均值。
    这比一次性传入超过 context 的列表更贴近模型的实际上下文限制。
    """
    if len(token_ids) < 2:
        raise ValueError("评估至少需要两个 token")
    total = 0.0
    for position in range(len(token_ids) - 1):
        start = max(0, position - model.context + 1)
        visible = token_ids[start:position + 1]
        logits, _ = model.forward(visible)
        answer = token_ids[position + 1]
        probability = softmax(logits[-1])[answer]
        total -= math.log(max(probability, 1e-300))
    return total / (len(token_ids) - 1)


def main():
    """把上面的零件串起来；建议初读源码时先从这里开始。"""
    # argparse 是标准库的命令行参数解析器。运行 --help 可查看所有可调选项。
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--glossary", action="store_true", help="只打印术语速查表，不训练模型")
    parser.add_argument("--steps", type=int, default=400, help="训练步数；0 表示只看未训练模型")
    parser.add_argument("--merges", type=int, default=40, help="BPE 合并次数")
    parser.add_argument("--context", type=int, default=16, help="最大上下文 token 数")
    parser.add_argument("--prompt", default="小猫", help="生成文本的前缀")
    parser.add_argument("--top-k", type=int, default=1, help="每步只从概率最高的 k 个 token 中选；1 为贪心解码")
    parser.add_argument("--temperature", type=float, default=0.8, help="采样温度；top-k=1 时不起作用")
    parser.add_argument("--check-grad", action="store_true", help="用数值微分核对反向传播")
    args = parser.parse_args()
    if args.glossary:
        print(GLOSSARY)
        return
    if args.steps < 0 or args.merges < 0 or args.context < 2 or args.top_k < 1 or args.temperature <= 0:
        parser.error("steps、merges 不能为负，context 至少为 2，top-k 和 temperature 必须大于 0")

    # 第一步：仅凭训练语料学习 BPE 合并规则，再试着编码/解码一个句子。
    tokenizer = ByteBPE.train(CORPUS, args.merges)
    print("术语看不懂时，可以单独运行：python3 learn_llm_from_scratch.py --glossary")
    example = "春天来了，花开了。"
    encoded = tokenizer.encode(example)
    print("\n① 分词：文本 → UTF-8 字节 → BPE token ID")
    print("原文:", example)
    print("token ID:", encoded)
    print("每个 token 对应的字节:", [tokenizer.pieces[i] for i in encoded])
    print("还原:", tokenizer.decode(encoded), "| 词表大小:", tokenizer.eos_id + 1)
    print("BPE 会合并常见的相邻片段，所以一个 token 可能是部分汉字，也可能是几个字。")

    # 词表是普通 token 加一个 EOS；模型输出层必须能为每个 ID 给出分数。
    model = TinyTransformer(tokenizer.eos_id + 1, args.context)
    parameter_count = sum(len(parameter.data) for parameter in model.params)
    print(f"模型可训练参数总数: {parameter_count:,}")
    # 合并次数很大时，整句可能变成一个 token；此时从另一句选第二个比较对象。
    token_a = encoded[0]
    token_b = encoded[1] if len(encoded) > 1 else tokenizer.encode("小猫")[0]
    # emb.data 是展平的矩阵；下面两个切片各取出一整行，即一个 token 向量。
    va = model.emb.data[token_a * model.width:(token_a + 1) * model.width]
    vb = model.emb.data[token_b * model.width:(token_b + 1) * model.width]
    print("\n② 向量：查找可训练的嵌入矩阵行，再加位置向量")
    print(f"token {token_a} 的前 6 维: {[round(x, 3) for x in va[:6]]}")
    print(f"两个初始 token 向量的余弦相似度: {cosine(va, vb):.4f}")
    print("余弦相似度比较两个向量的方向：接近 1 表示方向相近，接近 0 表示近乎垂直。")
    print("注意：这些向量刚随机初始化，相似度尚无语义；训练后才可能学到有用关系。")

    # 把多条文本拼成一个 token 流，并在每条文本后插入 EOS。
    # 这相当于语言模型训练中常见的“打包”样本方式。
    stream = []
    for text in CORPUS:
        # extend 将列表里的多个元素逐个加入；append 会把整张列表当作一个元素。
        stream.extend(tokenizer.encode(text) + [tokenizer.eos_id])
    if len(stream) <= args.context:
        parser.error("语料太短或 context 太长")
    # 固定随机种子后，训练窗口的抽样顺序每次运行都一样，方便对照输出。
    rng = random.Random(42)
    # 用一小段固定样本做前后损失比较。切片 [:5] 取开头 5 个 token。
    sample_ids = stream[:min(5, args.context)]
    # 目标向右平移一个位置，所以每个输入 token 都有“下一个 token”作为答案。
    sample_targets = stream[1:len(sample_ids) + 1]
    logits, cache = model.forward(sample_ids)
    # cache 的第 8 项保存所有注意力头的权重；[0][-1] 是头 0 最后位置的权重。
    weights = cache[8]
    print("\n③ 多头因果自注意力：分头汇总前文，不读取未来位置")
    print("Q、K、V 是同一输入分别乘以三个矩阵后得到的向量。")
    print("Q 与历史 K 比较得到分数；softmax 把分数变成权重，再按权重混合历史 V。")
    print("代码中的公式是 softmax(QKᵀ / √头维度 + 因果遮罩)V；各头结果拼接后再乘 Wo。")
    print("头 0 最后位置对当前位置及之前位置的权重:", [round(x, 3) for x in weights[0][-1]])
    print("未来位置根本不进入 softmax，因此训练时不会偷看目标 token。")
    # 实验：给原序列末尾加一个“未来 token”，再对比原来各位置的 logits。
    # 如果因果遮罩正确，原来位置的结果必须完全不变。
    if len(sample_ids) < model.context:
        extended_logits, _ = model.forward(sample_ids + [tokenizer.eos_id])
        largest_change = max(abs(old - new)
                             for old_row, new_row in zip(logits, extended_logits)
                             for old, new in zip(old_row, new_row))
        print(f"因果性自检：加入未来 token 后，已有位置的最大分数变化 = {largest_change:.1e}")
    print("注意力权重表示 Value 的混合比例；单看权重，不能断定某个词对最终答案有多重要。")
    print("注意力 softmax 在历史位置之间分配权重；输出 softmax 则在整个词表之间分配概率。")
    print("残差连接把原向量加回来；层归一化调整数值范围；GELU 为前馈网络加入非线性。")
    print("输出层给词表中的每个 token 一个 logit（原始分数），softmax 再把分数转成概率。")
    print(f"随机均匀猜测时的理论交叉熵约为 ln(词表大小) = {math.log(model.vocab):.3f}")
    print(f"未训练时的平均下一 token 损失: {_loss_only(model, sample_ids, sample_targets):.3f}")

    # 这个句子不在 CORPUS 中。BPE 仍能编码它，但模型未必知道其规律。
    # 评估文字后加 EOS，连“什么时候结束”也作为一个预测目标。
    unseen_text = "今天下雨了。"
    unseen_ids = tokenizer.encode(unseen_text) + [tokenizer.eos_id]
    unseen_before = text_loss(model, unseen_ids)

    if args.check_grad:
        # 可选的正确性检查，不参与下面的参数更新。
        print("\n④ 用中心差分核对部分参数的反向传播：")
        gradient_check(model, sample_ids, sample_targets)

    if args.steps:
        print("\n⑤ 训练：用已有 token 预测下一个 token，再按预测误差更新参数")
        print("交叉熵衡量模型给正确 token 的概率；概率越低，损失越高。")
        for step in range(1, args.steps + 1):
            # 随机截取一个长度为 context 的连续窗口。这是 batch size=1 的训练。
            start = rng.randrange(len(stream) - args.context)
            ids = stream[start:start + args.context]
            targets = stream[start + 1:start + args.context + 1]
            # 先求损失和梯度，再让 Adam 用梯度调整所有参数。
            loss = model.loss_and_backward(ids, targets)
            grad_norm = model.adam_step()
            if step == 1 or step % max(1, args.steps // 4) == 0 or step == args.steps:
                print(f"第 {step:>4} 步 | 平均交叉熵 {loss:.3f} | 裁剪前梯度范数 {grad_norm:.3f}")
        print(f"固定样本训练后的平均损失: {_loss_only(model, sample_ids, sample_targets):.3f}")
        print("交叉熵使用自然对数；它的指数 exp(损失) 叫困惑度，但不同文本的数值不能直接说明理解能力。")
        print(f"未参与训练的“{unseen_text}”损失: {unseen_before:.3f} → {text_loss(model, unseen_ids):.3f}")
        print("训练文本变容易，不等于新主题也变容易；一条未见句子只是示例，不是可靠的泛化评测。")
        after_a = model.emb.data[token_a * model.width:(token_a + 1) * model.width]
        after_b = model.emb.data[token_b * model.width:(token_b + 1) * model.width]
        print(f"同一对 token 训练后的嵌入余弦相似度: {cosine(after_a, after_b):.4f}")
        print("嵌入是 token 的静态起点；注意力之后的隐藏向量随上下文变化，单一余弦值不能证明语义关系。")
        # 两段前文只差“小猫”和“小狗”。比较同一结尾 token 的最终隐藏向量。
        # cache[15] 是最终 LayerNorm 后的 [t,d] 向量；[-1] 取最后位置。
        cat_context = tokenizer.encode("小猫看见了")
        dog_context = tokenizer.encode("小狗看见了")
        if len(cat_context) == len(dog_context) and cat_context[-1] == dog_context[-1]:
            cat_window = cat_context[-model.context:]
            dog_window = dog_context[-model.context:]
            cat_state = model.forward(cat_window)[1][15][-1]
            dog_state = model.forward(dog_window)[1][15][-1]
            distance = math.sqrt(sum((left - right) ** 2 for left, right in zip(cat_state, dog_state)))
            print(f"相同结尾 token 在“小猫看见了”与“小狗看见了”中的上下文向量距离: {distance:.3f}")
            print("距离由前文和可见上下文决定；若 context 太短，模型可能已看不到两句的不同开头。")

    # 直接检查一处真正的“下一个 token”分布；完整生成则在下面的循环中反复做这件事。
    print("\n下一 token 的具体预测：")
    show_next_token_predictions(model, tokenizer, "小狗看见了")

    # 生成时只输入提示词，不提供正确答案；模型必须一步步预测后续 token。
    prefix = tokenizer.encode(args.prompt)
    if not prefix:
        parser.error("prompt 不能为空")
    output = model.generate(prefix, 40, tokenizer.eos_id, rng, args.temperature, args.top_k)
    print("\n⑥ 自回归生成：一次选一个 token，接到已有文本后，再预测下一个")
    print("提示词:", args.prompt)
    print("解码:", "贪心" if args.top_k == 1 else f"top-k={args.top_k}, temperature={args.temperature}")
    print("生成:", tokenizer.decode(output))
    print("\n边界：样本很少，生成内容可能不通顺；这反映数据与算力限制，不改变模型的计算方式。")
    print("采样时若出现 �，通常是字节 token 尚未组合成合法 UTF-8；它不代表一个特殊预测 token。")
    print("大型 LLM 通常有更多层和参数、更大语料，并用缓存减少生成时的重复计算。")


if __name__ == "__main__":
    # 直接运行此文件才执行 main()；被另一个 Python 文件 import 时不会自动训练。
    main()
