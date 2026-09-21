# -*- coding: utf-8 -*-
"""
文档读取器 reader
=================

作用：把不同格式的本地文档读取为纯文本，供后续切块与索引使用。

支持格式（全部用 Python 标准库实现，无外部依赖）：
  - .txt / .md / .markdown ：直接按 UTF-8 读取；
  - .docx                  ：docx 本质是 zip 压缩包，用 zipfile + xml 解析正文；
  - .pdf                   ：内置一个极简 PDF 文本抽取器（处理最常见的
                              FlateDecode 文本流），复杂版式可能抽取不全，
                              但足以覆盖大多数文本型 PDF。

说明：
  PDF 解析本身是个很深的领域，本项目只做「够用」的透明实现。
  如果遇到解析不出来的 PDF，建议先用工具转成 txt/md 再入库，
  这是刻意的取舍，见 README「已知限制」一节。
"""

import os
import re
import zlib
import zipfile
import xml.etree.ElementTree as ET

# 支持的扩展名（统一转小写后比对）
SUPPORTED_EXTS = {".txt", ".md", ".markdown", ".docx", ".pdf"}


def _read_utf8(path: str) -> str:
    """
    以 UTF-8 读取文本文件；若失败则尝试 GBK（兼容中文老文件）。

    参数:
        path: 文件路径。

    返回:
        文件文本。
    """
    # 优先 UTF-8 读取
    try:
        # 显式指定 UTF-8 编码读取全部内容
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        # UTF-8 失败说明可能是 GBK 等编码，兜底再试一次
        with open(path, "r", encoding="gbk", errors="ignore") as f:
            return f.read()


def _read_docx(path: str) -> str:
    """
    从 .docx 中抽取正文纯文本。

    原理：docx 是一个 zip 包，正文在 word/document.xml 中，
    用 xml 标准库遍历所有 <w:t> 文本节点并拼接即可。

    参数:
        path: docx 文件路径。

    返回:
        抽取出的正文文本。
    """
    # 打开 zip 包，读取正文 XML 内容
    with zipfile.ZipFile(path) as zf:
        # document.xml 是 docx 正文的标准位置
        xml_bytes = zf.read("word/document.xml")
    # 解析 XML 为元素树
    root = ET.fromstring(xml_bytes)
    # 命名空间：w 是 Word 正文的固定命名空间前缀
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    # 收集所有段落文本
    lines = []
    # 遍历所有段落 <w:p>
    for para in root.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p"):
        # 把段内所有 <w:t> 的文本拼成一行
        text = "".join(t.text or "" for t in para.iter(
            "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t"))
        # 非空行才保留
        if text.strip():
            lines.append(text.strip())
    # 用换行连接各段
    return "\n".join(lines)


def _read_pdf(path: str) -> str:
    """
    极简 PDF 文本抽取器（零依赖）。

    原理：
      PDF 内部由若干对象组成，文本通常放在「流（stream）」里，
      且常见使用 FlateDecode（即 zlib 压缩）存储。
      本函数：
        1. 扫描出所有 stream ... endstream 之间的原始字节；
        2. 用 zlib 解压（失败则跳过该流）；
        3. 在解压后的内容里，用正则抽取文本显示操作符
           ( ... ) Tj 与 [ ... ] TJ 中的括号字符串。

    局限：不处理字体映射、复杂排版、扫描件（无文本层），
          但对纯文本型 PDF 已足够实用。

    参数:
        path: PDF 文件路径。

    返回:
        抽取出的文本（尽力而为）。
    """
    # 读取 PDF 二进制内容
    with open(path, "rb") as f:
        data = f.read()

    # 收集所有抽到的文本片段
    texts = []

    # 正则：匹配一个 stream ... endstream 块
    stream_re = re.compile(rb"stream\r?\n(.*?)\r?\nendstream", re.DOTALL)
    # 正则：匹配括号字符串显示操作，如 (abc) Tj 或 [ (a) (b) ] TJ
    text_op_re = re.compile(rb"\(((?:[^()\\]|\\.)*)\)")

    # 逐个处理 PDF 中的流对象
    for m in stream_re.finditer(data):
        # 取出流原始字节
        raw = m.group(1)
        # 尝试 zlib 解压；失败说明不是 Flate 流，跳过
        try:
            content = zlib.decompress(raw)
        except zlib.error:
            continue
        # 在解压内容中提取所有括号字符串
        for tm in text_op_re.finditer(content):
            # 取出字符串原始字节
            s = tm.group(1)
            # 反转义常见转义（如 \( 表示字面左括号）
            s = s.replace(rb"\(", b"(").replace(rb"\)", b")")
            s = s.replace(rb"\\", b"\\")
            # 尝试按 UTF-8 解码，失败则用 latin-1 兜底
            try:
                texts.append(s.decode("utf-8", errors="ignore"))
            except Exception:
                texts.append(s.decode("latin-1", errors="ignore"))

    # 把所有片段用空格连接（PDF 中每段显示是分开的）
    return " ".join(texts)


def read_document(path: str) -> str:
    """
    读取单个文档，返回其纯文本。

    参数:
        path: 文档路径。

    返回:
        文档的纯文本内容。

    抛出:
        ValueError: 当扩展名不受支持时抛出。
    """
    # 取扩展名并转小写
    ext = os.path.splitext(path)[1].lower()
    # 不支持的格式直接报错，明确边界
    if ext not in SUPPORTED_EXTS:
        raise ValueError(f"不支持的文档格式: {ext}（支持 {sorted(SUPPORTED_EXTS)}）")

    # 按扩展名分发到对应读取函数
    if ext in (".txt", ".md", ".markdown"):
        # 纯文本类：按 UTF-8/GBK 读取
        return _read_utf8(path)
    if ext == ".docx":
        # Word 文档：从 zip 中解析 XML
        return _read_docx(path)
    if ext == ".pdf":
        # PDF：走极简文本抽取器
        return _read_pdf(path)
    # 理论不可达，防御性兜底
    return ""
