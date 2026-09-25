# Agent 生成成果集 / Agent Project Collection / AIエージェント制作物集

[中文](#zh) · [English](#en) · [日本語](#ja)

<a id="zh"></a>
## 中文

本仓库集中保存使用 Claude、Codex、Dola、Doubao、Qoter 等 AI Agent 制作或整理的项目与学习资料。内容既包括可以直接运行的程序，也包括 Markdown、HTML、PDF、DOCX、XLSX 等可直接阅读或使用的成品。

> 仓库以成果归档和学习实验为主。每个可运行项目的详细设计、依赖与使用限制，请以对应子目录中的 README 为准。

### 内容导航

#### Claude

| 内容 | 形式 | 简介 |
| --- | --- | --- |
| [HowToLiveBetter](Claude/HowToLiveBetter-epub-latest/) | Markdown / HTML / 构建工具 | 由 33 个章节组成的高性价比人生指南，包含在线检索页、核实记录、离线 HTML、EPUB 与 PDF 构建脚本，以及配套的决策指南 Skill。 |
| [Vim 从零指南](Claude/Vim从零指南.md) / [HTML 版](<Claude/Vim 从零指南 · macOS JIS 键盘.html>) | Markdown / HTML | 面向 macOS JIS 键盘用户的 Vim 入门、配置与速查资料。 |
| [中国大陆民用运输机场清单](Claude/china-airport.md) | Markdown | 中国大陆民用运输机场资料汇总。 |
| [日本机场清单](Claude/japan-airport.md) | Markdown | 日本固定翼机场资料汇总。 |
| [LaTeX 速查表](Claude/latex-cheatsheet.pdf) | PDF | LaTeX 常用语法与命令速查资料。 |

#### Codex

| 内容 | 形式 | 简介 |
| --- | --- | --- |
| [蜀门甩二](Codex/sichuan-shuai-er/) | HTML / CSS / JavaScript | 四人两队的四川单副升级扑克游戏，可直接在浏览器运行，包含 AI 对手、进度保存和规则测试。 |
| [HowToLiveBetter 离线版](Codex/HowToLiveBetter.html) / [PDF 版](Codex/HowToLiveBetter-1.pdf) | HTML / PDF | 《高性价比人生指南》的离线检索页面与 344 页 PDF 成品。 |
| [IT パスポート 2026 完全复习指南](Codex/ITパスポート_2026_完全復習ガイド_Ver6.5.docx) | DOCX | 日文 IT Passport 考试复习资料。 |
| [日本特色车站名 200 选](Codex/japan_special_station_names_200.xlsx) | XLSX | 日本特色车站名称整理表。 |
| [纸牌人物图像](Codex/generated_images/court-portraits/) | PNG | 蜀门甩二使用的 J、Q、K 牌面人物素材。 |

#### Dola

| 内容 | 技术 | 简介 |
| --- | --- | --- |
| [rag_kit](Dola_work/rag_kit/) | Python 3.9+ | 日文注释的白箱 RAG：文档读取、切块、BM25 与 n-gram 混合检索、RRF、重排、抽取式或可选 LLM 生成，并带评测与单元测试。核心仅使用 Python 标准库。 |

#### Doubao

| 内容 | 技术 | 简介 |
| --- | --- | --- |
| [C-Learning](Doubao_Project/C-Learning/) | C / Make | 12 章 C 语言入门示例，覆盖基础语法、流程控制、指针、结构体、动态内存、文件操作和综合练习；另附 [ZIP 包](Doubao_Project/C-Learning.zip)。 |
| [java-learn](Doubao_Project/java-learn/) | Java 11+ | 零第三方依赖的 Java 语法学习项目，覆盖基础、面向对象、集合、异常、泛型、IO、多线程与 Lambda/Stream。 |
| [easy_rag](Doubao_Project/easy_rag/) | Python | 零强制依赖的中文白箱 RAG，支持文档入库、混合检索、重排、引用溯源、评测、命令行和本地网页。 |
| [rag_kit](Doubao_Project/rag_kit/) | Python 3.9+ | 与 Dola 目录版本内容一致的日文白箱 RAG 实现。 |
| [rag_pro](Doubao_Project/rag_pro/) | Python 3.8+ | 功能更完整的中文 RAG 工程，增加查询改写、MMR、上下文预算、增量入库、HTTP API 和 Recall/MRR/Hit 评测。 |

#### Qoter

| 内容 | 形式 | 简介 |
| --- | --- | --- |
| [HTML 学习资料](Qoter/HTML学习资料.md) / [HTML 页面版](Qoter/2026-09-22/9724f4c3/html-学习资料.html) | Markdown / HTML | HTML 标签、结构和常用写法的学习资料。 |
| [Python 语法详解](Qoter/python-syntax-guide.html) | HTML | Python 基础语法学习页面。 |
| [Markdown 学习手册](Qoter/2026-09-22/e70ab758/markdown-guide.html) | HTML | Markdown 常用语法与示例。 |
| [LaTeX 语法学习资料](Qoter/2026-09-22/06654f8a/LaTeX语法学习资料.md) | Markdown | LaTeX 语法学习文档。 |

### 快速运行

以下命令均从仓库根目录执行。

#### RAG 项目

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

#### 编程语言学习项目

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

#### 浏览器游戏

进入 `Codex/sichuan-shuai-er/` 后，直接打开 `index.html`；macOS 也可以双击 `打开游戏.command`。规则测试需要 Node.js：

```bash
cd Codex/sichuan-shuai-er
node --test tests/rules.test.js
```

### 仓库结构

```text
.
├── Claude/          # 书籍项目、Vim/机场资料、LaTeX 速查表
├── Codex/           # 浏览器游戏、文档、表格、PDF/HTML 成品与图像素材
├── Dola_work/       # 日文白箱 RAG 项目
├── Doubao_Project/  # C/Java 教学项目与多套 RAG 实现
├── Qoter/           # HTML、Python、Markdown、LaTeX 学习资料
└── README.MD        # 仓库总览
```

### 使用说明

- HTML 文件通常可直接用现代浏览器打开；`HowToLiveBetter` 源码版需要通过本地 HTTP 服务访问，具体方法见其项目说明。
- RAG 项目默认可在不配置大模型 API 的情况下运行离线检索或抽取式回答；接入在线模型的方法见各项目 README。
- DOCX、XLSX、PDF 等文件可直接下载后使用对应办公软件或阅读器打开。
- 仓库内各成果的许可与免责声明可能不同，请查看具体子项目中的说明或许可证文件。

---

首次提交：2026-09-22 08:33（UTC+9，日本东京）<br>
README 更新：2026-09-26

---

<a id="en"></a>
## English

This repository collects projects and learning materials made or organized with Claude, Codex, Dola, Doubao, Qoter, and other AI agents. It includes runnable software as well as Markdown, HTML, PDF, DOCX, and XLSX files that can be read or used directly.

> This is an archive of results and learning experiments. For design details, dependencies, and limitations, see the README in each runnable project's directory.

### Project guide

#### Claude

| Project or resource | Format | Description |
| --- | --- | --- |
| [HowToLiveBetter](Claude/HowToLiveBetter-epub-latest/) | Markdown / HTML / build tools | A 33-chapter guide to making practical life decisions. Includes a searchable web page, fact-checking notes, tools for building offline HTML, EPUB, and PDF editions, and a related decision-guide skill. |
| [Vim beginner's guide](Claude/Vim从零指南.md) / [HTML edition](<Claude/Vim 从零指南 · macOS JIS 键盘.html>) | Markdown / HTML | A Vim guide for macOS users with JIS keyboards, covering the basics, configuration, and quick reference. |
| [Mainland China civil transport airports](Claude/china-airport.md) | Markdown | Reference list of civil transport airports in mainland China. |
| [Japan airports](Claude/japan-airport.md) | Markdown | Reference list of fixed-wing airports in Japan. |
| [LaTeX cheat sheet](Claude/latex-cheatsheet.pdf) | PDF | Quick reference for common LaTeX syntax and commands. |

#### Codex

| Project or resource | Format | Description |
| --- | --- | --- |
| [Shu Men Shuai Er](Codex/sichuan-shuai-er/) | HTML / CSS / JavaScript | A four-player, two-team Sichuan card game that runs in a browser. Includes AI opponents, saved progress, and rules tests. |
| [HowToLiveBetter offline edition](Codex/HowToLiveBetter.html) / [PDF edition](Codex/HowToLiveBetter-1.pdf) | HTML / PDF | An offline searchable edition of the life guide and a 344-page PDF. |
| [IT Passport 2026 complete review guide](Codex/ITパスポート_2026_完全復習ガイド_Ver6.5.docx) | DOCX | Japanese-language study material for the IT Passport exam. |
| [200 distinctive Japanese station names](Codex/japan_special_station_names_200.xlsx) | XLSX | Spreadsheet of distinctive station names in Japan. |
| [Card portraits](Codex/generated_images/court-portraits/) | PNG | J, Q, and K character artwork for Shu Men Shuai Er. |

#### Dola

| Project | Technology | Description |
| --- | --- | --- |
| [rag_kit](Dola_work/rag_kit/) | Python 3.9+ | A Japanese-commented, transparent RAG implementation with document loading, chunking, BM25 and n-gram hybrid retrieval, RRF, reranking, extractive or optional LLM answers, evaluation, and unit tests. Its core uses only the Python standard library. |

#### Doubao

| Project | Technology | Description |
| --- | --- | --- |
| [C-Learning](Doubao_Project/C-Learning/) | C / Make | Twelve chapters of C examples, from basic syntax and control flow to pointers, structs, dynamic memory, files, and exercises. A [ZIP archive](Doubao_Project/C-Learning.zip) is also available. |
| [java-learn](Doubao_Project/java-learn/) | Java 11+ | A Java learning project without third-party dependencies, covering basics, object-oriented programming, collections, exceptions, generics, I/O, threads, and Lambda/Stream. |
| [easy_rag](Doubao_Project/easy_rag/) | Python | A Chinese-language, transparent RAG implementation with no required third-party packages. Includes ingestion, hybrid retrieval, reranking, citations, evaluation, a CLI, and a local web interface. |
| [rag_kit](Doubao_Project/rag_kit/) | Python 3.9+ | A copy of the Japanese-language `rag_kit` in the Dola directory. |
| [rag_pro](Doubao_Project/rag_pro/) | Python 3.8+ | An extended Chinese-language RAG project with query rewriting, MMR, context budgeting, incremental ingestion, an HTTP API, and Recall/MRR/Hit evaluation. |

#### Qoter

| Resource | Format | Description |
| --- | --- | --- |
| [HTML study notes](Qoter/HTML学习资料.md) / [HTML page](Qoter/2026-09-22/9724f4c3/html-学习资料.html) | Markdown / HTML | Lessons on HTML tags, document structure, and common patterns. |
| [Python syntax guide](Qoter/python-syntax-guide.html) | HTML | An introductory Python syntax reference. |
| [Markdown guide](Qoter/2026-09-22/e70ab758/markdown-guide.html) | HTML | Common Markdown syntax with examples. |
| [LaTeX study notes](Qoter/2026-09-22/06654f8a/LaTeX语法学习资料.md) | Markdown | LaTeX syntax learning material. |

### Quick start

Run each group of commands from the repository root.

#### RAG projects

```bash
# Dola rag_kit: build an index, ask a question, and run tests
cd Dola_work/rag_kit
python3 app/cli.py build data out
python3 app/cli.py ask out "RAGとは何ですか？"
python3 -m unittest discover -s tests -v
```

```bash
# Doubao easy_rag: build an index, search offline, and start the web UI
cd Doubao_Project/easy_rag
python3 app.py build
python3 app.py ask "退款政策是什么？" --no-llm
python3 app.py serve --port 8080
```

```bash
# Doubao rag_pro: build an index, ask, evaluate, and start the API
cd Doubao_Project/rag_pro
python3 run.py build --dir data/sample
python3 run.py ask --q "什么是RAG？"
python3 run.py eval --qa data/sample/qa.json
python3 run.py serve --port 8765
```

#### Programming examples

```bash
# C: compile all examples
cd Doubao_Project/C-Learning
make
./build/01-hello/hello
```

```bash
# Java: compile and run an example
cd Doubao_Project/java-learn
./compile.sh
./run.sh basics.HelloWorld
```

#### Browser game

Open `Codex/sichuan-shuai-er/index.html` in a browser. On macOS, you can also double-click `打开游戏.command`. Node.js is needed only for the rules tests:

```bash
cd Codex/sichuan-shuai-er
node --test tests/rules.test.js
```

### Repository layout

```text
.
├── Claude/          # Book project, Vim and airport guides, LaTeX cheat sheet
├── Codex/           # Browser game, documents, spreadsheets, PDF/HTML, artwork
├── Dola_work/       # Japanese-language transparent RAG project
├── Doubao_Project/  # C/Java lessons and several RAG implementations
├── Qoter/           # HTML, Python, Markdown, and LaTeX study materials
└── README.MD        # Repository overview
```

### Notes

- Most HTML files open directly in a modern browser. The source version of `HowToLiveBetter` needs a local HTTP server; see its project README.
- The RAG projects can run offline retrieval or extractive answers without an LLM API. Each project README explains how to connect an online model.
- Download DOCX, XLSX, and PDF files and open them with a compatible office application or reader.
- Licenses and disclaimers can differ by project. Check the relevant project documentation or license file.

First commit: 2026-09-22 08:33 (UTC+9, Tokyo, Japan)<br>
README updated: 2026-09-26

---

<a id="ja"></a>
## 日本語

このリポジトリには、Claude、Codex、Dola、Doubao、Qoter などの AI エージェントを使って制作・整理したプロジェクトと学習資料をまとめています。実行できるプログラムのほか、Markdown、HTML、PDF、DOCX、XLSX 形式の成果物があります。

> 学習と成果物の保管を目的としたリポジトリです。各プロジェクトの設計、依存関係、制限事項は、それぞれのディレクトリにある README を参照してください。

### コンテンツ一覧

#### Claude

| 内容 | 形式 | 概要 |
| --- | --- | --- |
| [HowToLiveBetter](Claude/HowToLiveBetter-epub-latest/) | Markdown / HTML / ビルドツール | 33 章からなる生活上の意思決定ガイド。検索ページ、根拠の確認記録、オフライン HTML・EPUB・PDF の生成ツール、関連する意思決定ガイド Skill を収録。 |
| [Vim 入門ガイド](Claude/Vim从零指南.md) / [HTML 版](<Claude/Vim 从零指南 · macOS JIS 键盘.html>) | Markdown / HTML | macOS の JIS キーボード利用者向け。Vim の基本操作、設定、早見表を掲載。 |
| [中国本土の民間輸送空港一覧](Claude/china-airport.md) | Markdown | 中国本土の民間輸送空港を整理した資料。 |
| [日本の空港一覧](Claude/japan-airport.md) | Markdown | 日本の固定翼機用空港を整理した資料。 |
| [LaTeX 早見表](Claude/latex-cheatsheet.pdf) | PDF | よく使う LaTeX の構文とコマンドの早見表。 |

#### Codex

| 内容 | 形式 | 概要 |
| --- | --- | --- |
| [蜀門甩二](Codex/sichuan-shuai-er/) | HTML / CSS / JavaScript | 4 人が 2 チームに分かれて対戦する四川式カードゲーム。ブラウザで動作し、AI 対戦相手、進行状況の保存、ルールのテストを備えています。 |
| [HowToLiveBetter オフライン版](Codex/HowToLiveBetter.html) / [PDF 版](Codex/HowToLiveBetter-1.pdf) | HTML / PDF | 検索できるオフライン版と 344 ページの PDF。 |
| [IT パスポート 2026 完全復習ガイド](Codex/ITパスポート_2026_完全復習ガイド_Ver6.5.docx) | DOCX | 日本語の IT パスポート試験対策資料。 |
| [日本の特色ある駅名 200 選](Codex/japan_special_station_names_200.xlsx) | XLSX | 日本の特色ある駅名をまとめた表。 |
| [絵札の人物画像](Codex/generated_images/court-portraits/) | PNG | 蜀門甩二で使用する J・Q・K の人物画像。 |

#### Dola

| 内容 | 技術 | 概要 |
| --- | --- | --- |
| [rag_kit](Dola_work/rag_kit/) | Python 3.9+ | 日本語のコメントを付けたホワイトボックス RAG。文書の読み込み・分割、BM25 と n-gram によるハイブリッド検索、RRF、再ランキング、抽出型または任意の LLM による回答、評価、単体テストを備えています。中核部分は Python 標準ライブラリのみを使用します。 |

#### Doubao

| 内容 | 技術 | 概要 |
| --- | --- | --- |
| [C-Learning](Doubao_Project/C-Learning/) | C / Make | 基本構文から制御構文、ポインタ、構造体、動的メモリ、ファイル操作、演習までを扱う全 12 章の C 言語入門。 [ZIP 版](Doubao_Project/C-Learning.zip)もあります。 |
| [java-learn](Doubao_Project/java-learn/) | Java 11+ | 外部依存のない Java 学習プロジェクト。基本構文、オブジェクト指向、コレクション、例外、ジェネリクス、入出力、スレッド、Lambda/Stream を扱います。 |
| [easy_rag](Doubao_Project/easy_rag/) | Python | 外部パッケージが必須ではない中国語のホワイトボックス RAG。文書登録、ハイブリッド検索、再ランキング、出典表示、評価、CLI、ローカル Web 画面を備えています。 |
| [rag_kit](Doubao_Project/rag_kit/) | Python 3.9+ | Dola ディレクトリにある日本語版 `rag_kit` と同じ内容のコピー。 |
| [rag_pro](Doubao_Project/rag_pro/) | Python 3.8+ | クエリ書き換え、MMR、コンテキストの長さ制御、追加登録、HTTP API、Recall/MRR/Hit 評価を加えた中国語の RAG プロジェクト。 |

#### Qoter

| 内容 | 形式 | 概要 |
| --- | --- | --- |
| [HTML 学習資料](Qoter/HTML学习资料.md) / [HTML ページ](Qoter/2026-09-22/9724f4c3/html-学习资料.html) | Markdown / HTML | HTML タグ、文書構造、よく使う書き方の学習資料。 |
| [Python 構文学習ページ](Qoter/python-syntax-guide.html) | HTML | Python の基本構文を解説するページ。 |
| [Markdown ガイド](Qoter/2026-09-22/e70ab758/markdown-guide.html) | HTML | Markdown の主な構文と使用例。 |
| [LaTeX 学習資料](Qoter/2026-09-22/06654f8a/LaTeX语法学习资料.md) | Markdown | LaTeX の構文を学ぶための資料。 |

### クイックスタート

各コマンド群はリポジトリのルートから実行してください。

#### RAG プロジェクト

```bash
# Dola rag_kit：索引作成、質問、テスト
cd Dola_work/rag_kit
python3 app/cli.py build data out
python3 app/cli.py ask out "RAGとは何ですか？"
python3 -m unittest discover -s tests -v
```

```bash
# Doubao easy_rag：索引作成、オフライン検索、Web 画面の起動
cd Doubao_Project/easy_rag
python3 app.py build
python3 app.py ask "退款政策是什么？" --no-llm
python3 app.py serve --port 8080
```

```bash
# Doubao rag_pro：索引作成、質問、評価、API の起動
cd Doubao_Project/rag_pro
python3 run.py build --dir data/sample
python3 run.py ask --q "什么是RAG？"
python3 run.py eval --qa data/sample/qa.json
python3 run.py serve --port 8765
```

#### プログラミング学習用のサンプル

```bash
# C：すべてのサンプルをコンパイル
cd Doubao_Project/C-Learning
make
./build/01-hello/hello
```

```bash
# Java：コンパイルして指定したサンプルを実行
cd Doubao_Project/java-learn
./compile.sh
./run.sh basics.HelloWorld
```

#### ブラウザゲーム

`Codex/sichuan-shuai-er/index.html` をブラウザで開いてください。macOS では `打开游戏.command` をダブルクリックして起動することもできます。ルールのテストを実行するときだけ Node.js が必要です。

```bash
cd Codex/sichuan-shuai-er
node --test tests/rules.test.js
```

### ディレクトリ構成

```text
.
├── Claude/          # 書籍、Vim・空港の資料、LaTeX 早見表
├── Codex/           # ブラウザゲーム、文書、表、PDF/HTML、画像素材
├── Dola_work/       # 日本語のホワイトボックス RAG
├── Doubao_Project/  # C/Java 学習用サンプルと複数の RAG 実装
├── Qoter/           # HTML、Python、Markdown、LaTeX の学習資料
└── README.MD        # リポジトリ全体の案内
```

### 利用上の注意

- 多くの HTML ファイルはブラウザでそのまま開けます。`HowToLiveBetter` のソース版はローカル HTTP サーバーが必要です。方法はプロジェクトの README を参照してください。
- RAG プロジェクトは、LLM API を設定しなくてもオフライン検索や抽出型の回答を利用できます。オンラインモデルとの接続方法は各 README に記載しています。
- DOCX、XLSX、PDF ファイルは、対応するアプリやビューアーで開いてください。
- ライセンスや免責事項はプロジェクトごとに異なる場合があります。各プロジェクトの説明またはライセンスファイルを確認してください。

初回コミット：2026-09-22 08:33（UTC+9、東京）<br>
README 更新日：2026-09-26
