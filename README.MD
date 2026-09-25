# Agent 生成成果集

本仓库集中保存使用 Claude、Codex、Dola、Doubao、Qoter 等 AI Agent 制作或整理的项目与学习资料。内容既包括可以直接运行的程序，也包括 Markdown、HTML、PDF、DOCX、XLSX 等可直接阅读或使用的成品。

> 仓库以成果归档和学习实验为主。每个可运行项目的详细设计、依赖与使用限制，请以对应子目录中的 README 为准。

## 内容导航

### Claude

| 内容 | 形式 | 简介 |
| --- | --- | --- |
| [HowToLiveBetter](Claude/HowToLiveBetter-epub-latest/) | Markdown / HTML / 构建工具 | 由 33 个章节组成的高性价比人生指南，包含在线检索页、核实记录、离线 HTML、EPUB 与 PDF 构建脚本，以及配套的决策指南 Skill。 |
| [Vim 从零指南](Claude/Vim从零指南.md) / [HTML 版](<Claude/Vim 从零指南 · macOS JIS 键盘.html>) | Markdown / HTML | 面向 macOS JIS 键盘用户的 Vim 入门、配置与速查资料。 |
| [中国大陆民用运输机场清单](Claude/china-airport.md) | Markdown | 中国大陆民用运输机场资料汇总。 |
| [日本机场清单](Claude/japan-airport.md) | Markdown | 日本固定翼机场资料汇总。 |
| [LaTeX 速查表](Claude/latex-cheatsheet.pdf) | PDF | LaTeX 常用语法与命令速查资料。 |

### Codex

| 内容 | 形式 | 简介 |
| --- | --- | --- |
| [蜀门甩二](Codex/sichuan-shuai-er/) | HTML / CSS / JavaScript | 四人两队的四川单副升级扑克游戏，可直接在浏览器运行，包含 AI 对手、进度保存和规则测试。 |
| [HowToLiveBetter 离线版](Codex/HowToLiveBetter.html) / [PDF 版](Codex/HowToLiveBetter-1.pdf) | HTML / PDF | 《高性价比人生指南》的离线检索页面与 344 页 PDF 成品。 |
| [IT パスポート 2026 完全复习指南](Codex/ITパスポート_2026_完全復習ガイド_Ver6.5.docx) | DOCX | 日文 IT Passport 考试复习资料。 |
| [日本特色车站名 200 选](Codex/japan_special_station_names_200.xlsx) | XLSX | 日本特色车站名称整理表。 |
| [纸牌人物图像](Codex/generated_images/court-portraits/) | PNG | 蜀门甩二使用的 J、Q、K 牌面人物素材。 |

### Dola

| 内容 | 技术 | 简介 |
| --- | --- | --- |
| [rag_kit](Dola_work/rag_kit/) | Python 3.9+ | 日文注释的白箱 RAG：文档读取、切块、BM25 与 n-gram 混合检索、RRF、重排、抽取式或可选 LLM 生成，并带评测与单元测试。核心仅使用 Python 标准库。 |

### Doubao

| 内容 | 技术 | 简介 |
| --- | --- | --- |
| [C-Learning](Doubao_Project/C-Learning/) | C / Make | 12 章 C 语言入门示例，覆盖基础语法、流程控制、指针、结构体、动态内存、文件操作和综合练习；另附 [ZIP 包](Doubao_Project/C-Learning.zip)。 |
| [java-learn](Doubao_Project/java-learn/) | Java 11+ | 零第三方依赖的 Java 语法学习项目，覆盖基础、面向对象、集合、异常、泛型、IO、多线程与 Lambda/Stream。 |
| [easy_rag](Doubao_Project/easy_rag/) | Python | 零强制依赖的中文白箱 RAG，支持文档入库、混合检索、重排、引用溯源、评测、命令行和本地网页。 |
| [rag_kit](Doubao_Project/rag_kit/) | Python 3.9+ | 与 Dola 目录版本内容一致的日文白箱 RAG 实现。 |
| [rag_pro](Doubao_Project/rag_pro/) | Python 3.8+ | 功能更完整的中文 RAG 工程，增加查询改写、MMR、上下文预算、增量入库、HTTP API 和 Recall/MRR/Hit 评测。 |

### Qoter

| 内容 | 形式 | 简介 |
| --- | --- | --- |
| [HTML 学习资料](Qoter/HTML学习资料.md) / [HTML 页面版](Qoter/2026-09-22/9724f4c3/html-学习资料.html) | Markdown / HTML | HTML 标签、结构和常用写法的学习资料。 |
| [Python 语法详解](Qoter/python-syntax-guide.html) | HTML | Python 基础语法学习页面。 |
| [Markdown 学习手册](Qoter/2026-09-22/e70ab758/markdown-guide.html) | HTML | Markdown 常用语法与示例。 |
| [LaTeX 语法学习资料](Qoter/2026-09-22/06654f8a/LaTeX语法学习资料.md) | Markdown | LaTeX 语法学习文档。 |

## 快速运行

以下命令均从仓库根目录执行。

### RAG 项目

```bash
# Dola rag_kit：构建索引、提问、运行测试
cd Dola_work/rag_kit
python3 app/cli.py build data out
python3 app/cli.py ask out "RAGとは何ですか？"
python3 -m unittest discover -s tests -v
```

```bash
# Doubao easy_rag：构建索引、离线检索、启动网页
cd Doubao_Project/easy_rag
python3 app.py build
python3 app.py ask "退款政策是什么？" --no-llm
python3 app.py serve --port 8080
```

```bash
# Doubao rag_pro：构建索引、问答、评测、启动 API
cd Doubao_Project/rag_pro
python3 run.py build --dir data/sample
python3 run.py ask --q "什么是RAG？"
python3 run.py eval --qa data/sample/qa.json
python3 run.py serve --port 8765
```

### 编程语言学习项目

```bash
# C：编译全部示例
cd Doubao_Project/C-Learning
make
./build/01-hello/hello
```

```bash
# Java：编译并运行指定示例
cd Doubao_Project/java-learn
./compile.sh
./run.sh basics.HelloWorld
```

### 浏览器游戏

进入 `Codex/sichuan-shuai-er/` 后，直接打开 `index.html`；macOS 也可以双击 `打开游戏.command`。规则测试需要 Node.js：

```bash
cd Codex/sichuan-shuai-er
node --test tests/rules.test.js
```

## 仓库结构

```text
.
├── Claude/          # 书籍项目、Vim/机场资料、LaTeX 速查表
├── Codex/           # 浏览器游戏、文档、表格、PDF/HTML 成品与图像素材
├── Dola_work/       # 日文白箱 RAG 项目
├── Doubao_Project/  # C/Java 教学项目与多套 RAG 实现
├── Qoter/           # HTML、Python、Markdown、LaTeX 学习资料
└── README.MD        # 仓库总览
```

## 使用说明

- HTML 文件通常可直接用现代浏览器打开；`HowToLiveBetter` 源码版需要通过本地 HTTP 服务访问，具体方法见其项目说明。
- RAG 项目默认可在不配置大模型 API 的情况下运行离线检索或抽取式回答；接入在线模型的方法见各项目 README。
- DOCX、XLSX、PDF 等文件可直接下载后使用对应办公软件或阅读器打开。
- 仓库内各成果的许可与免责声明可能不同，请查看具体子项目中的说明或许可证文件。

---

首次提交：2026-09-22 08:33（UTC+9，日本东京）<br>
README 更新：2026-09-26
