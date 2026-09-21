# ============================================================
# 文档读取：把各种格式的文件读成纯文本，供后续切块
#
# 全部只用标准库实现，不依赖 pypdf / python-docx 等外部库：
#   txt / md : 直接按 UTF-8 读取（带编码兜底）
#   html     : 用标准库 html.parser 抽取正文文字
#   csv      : 用 csv 模块把每行拼接成一行文本
#   docx     : docx 本质是 zip 压缩的 XML，解包后抽取 <w:t> 文本
#   pdf      : 解压流对象后用正则抽取文本（仅支持简单文本型 PDF）
#
# 复杂版式 / 扫描件的 PDF 提取不完整，正式使用建议换 pypdf，见 README
# ============================================================

import csv
import html
import os
import re
import zipfile
import zlib
from html.parser import HTMLParser

# 支持的扩展名集合，用于遍历文件夹时过滤
_SUPPORTED = {".txt", ".md", ".markdown", ".html", ".htm", ".csv", ".docx", ".pdf"}


def load_text(path):
    """读取纯文本文件，自动尝试常见编码"""
    for enc in ("utf-8", "gbk", "latin-1"):       # 依次尝试三种编码
        try:
            with open(path, encoding=enc) as f:
                return f.read()
        except (UnicodeDecodeError, LookupError):  # 解码失败就换下一种
            continue
    with open(path, encoding="utf-8", errors="ignore") as f:
        return f.read()                            # 最后兜底：忽略坏字符


class _TextExtractor(HTMLParser):
    """HTML 正文抽取器：只收集标签之外的文字内容"""
    def __init__(self):
        super().__init__()
        self.parts = []                            # 收集到的文字片段

    def handle_data(self, data):                   # 标签之间的文本回调
        self.parts.append(data)


def load_html(path):
    """解析 HTML 并返回去掉标签后的正文文本"""
    parser = _TextExtractor()
    parser.feed(load_text(path))                   # 喂给解析器
    # 过滤空白片段后用换行拼接，方便检索时按句切分
    return "\n".join(p for p in parser.parts if p.strip())


def load_csv(path):
    """把 CSV 每一行拼成一行文本，方便整行检索"""
    lines = []
    with open(path, encoding="utf-8", errors="ignore", newline="") as f:
        for row in csv.reader(f):                  # 逐行读取
            lines.append(" | ".join(cell.strip() for cell in row))
    return "\n".join(lines)


def load_docx(path):
    """读取 Word 文档：解包 zip 结构，抽取段落文本"""
    with zipfile.ZipFile(path) as z:
        xml = z.read("word/document.xml").decode("utf-8", "ignore")
    xml = re.sub(r"</w:p>", "\n", xml)             # 段落结束标签换成换行
    parts = re.findall(r"<w:t[^>]*>(.*?)</w:t>", xml, re.S)  # 抽所有文本节点
    return html.unescape("".join(parts))           # 反转义 XML 实体


def _decode_pdf_str(b):
    """把 PDF 括号字符串按字节转成文本（处理常见转义）"""
    b = b.replace(rb"\(", b"(").replace(rb"\)", b")") \
         .replace(rb"\\", b"\\").replace(rb"\n", b"\n") \
         .replace(rb"\r", b"\r").replace(rb"\t", b"\t")
    return b.decode("latin-1", "ignore")           # 按字节解码，不丢内容


def load_pdf(path):
    """读取 PDF 文本：解压流对象后抽取 Tj/TJ 文本（仅简单文本 PDF）"""
    raw = open(path, "rb").read()                  # 读原始字节
    out = []
    # 遍历所有流对象（FlateDecode 压缩的用 zlib 解压）
    for m in re.finditer(rb"stream\r?\n(.*?)\r?\nendstream", raw, re.S):
        data = m.group(1)
        try:
            data = zlib.decompress(data)           # 解压
        except Exception:
            continue                               # 不是压缩流就跳过
        # 抽取 "(...) Tj" 形式的单段文本
        for tm in re.finditer(rb"\(((?:[^()\\]|\\.)*)\)\s*Tj", data):
            out.append(_decode_pdf_str(tm.group(1)))
        # 抽取 "[...] TJ" 形式的多段拼接文本
        for tm in re.finditer(rb"\[(.*?)\]\s*TJ", data, re.S):
            for part in re.finditer(rb"\(((?:[^()\\]|\\.)*)\)", tm.group(1)):
                out.append(_decode_pdf_str(part.group(1)))
    return "".join(out)


def load_document(path):
    """按文件扩展名分派到对应的读取函数，返回纯文本"""
    ext = os.path.splitext(path)[1].lower()        # 取小写扩展名
    if ext in (".txt", ".md", ".markdown"):
        return load_text(path)
    if ext in (".html", ".htm"):
        return load_html(path)
    if ext == ".csv":
        return load_csv(path)
    if ext == ".docx":
        return load_docx(path)
    if ext == ".pdf":
        return load_pdf(path)
    raise ValueError(f"不支持的格式: {ext}")        # 明确报错而不是忽略


def load_folder(folder):
    """递归遍历文件夹，返回 [(文件路径, 文本内容)] 列表"""
    items = []
    for root, _, files in os.walk(folder):         # 递归扫描目录
        for name in sorted(files):                 # 排序保证结果稳定
            path = os.path.join(root, name)
            if os.path.splitext(name)[1].lower() not in _SUPPORTED:
                continue                            # 跳过不支持的格式
            try:
                text = load_document(path)
            except Exception as e:
                print(f"[跳过] {path}: {e}")       # 读失败不中断整体
                continue
            if text.strip():                        # 只收录非空内容
                items.append((path, text))
    return items
