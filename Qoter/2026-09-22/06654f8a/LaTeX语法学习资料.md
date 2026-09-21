# LaTeX 语法学习详细资料

> 本资料系统讲解 LaTeX 排版语言的语法，从环境搭建到文档结构、数学公式、图表、参考文献等，配有大量可直接使用的代码示例。适合从零基础到进阶学习。

---

## 目录

1. [LaTeX 简介](#1-latex-简介)
2. [环境搭建与编译](#2-环境搭建与编译)
3. [文档基本结构](#3-文档基本结构)
4. [文字与段落排版](#4-文字与段落排版)
5. [数学公式](#5-数学公式)
6. [列表](#6-列表)
7. [表格](#7-表格)
8. [图片与浮动体](#8-图片与浮动体)
9. [交叉引用与超链接](#9-交叉引用与超链接)
10. [参考文献](#10-参考文献)
11. [自定义命令与宏](#11-自定义命令与宏)
12. [页面布局与页眉页脚](#12-页面布局与页眉页脚)
13. [中文支持](#13-中文支持)
14. [常用宏包速查](#14-常用宏包速查)
15. [常见错误与调试](#15-常见错误与调试)
16. [学习资源](#16-学习资源)

---

## 1. LaTeX 简介

**LaTeX**（读作 "Lay-tech" 或 "Lah-tech"）是一套基于 TeX 的排版系统，由 Leslie Lamport 开发。它广泛应用于学术论文、书籍、报告、幻灯片等，尤其擅长排版数学公式和处理长文档。

### 特点

- **内容与格式分离**：作者专注于内容，格式由系统统一处理。
- **高质量输出**：排版精美，尤其数学公式无可替代。
- **交叉引用自动化**：图表、章节、公式编号自动管理。
- **纯文本源码**：便于版本控制（Git）和协作。

### LaTeX vs Word

| 对比项 | LaTeX | Word |
|--------|-------|------|
| 学习曲线 | 较陡 | 平缓 |
| 数学公式 | 极强 | 一般 |
| 长文档稳定性 | 极稳 | 易乱 |
| 排版一致性 | 自动保证 | 手动维护 |
| 所见即所得 | 否（编译后可见） | 是 |

---

## 2. 环境搭建与编译

### 2.1 本地安装

| 平台 | 推荐发行版 |
|------|-----------|
| Windows | [MiKTeX](https://miktex.org/) 或 [TeX Live](https://tug.org/texlive/) |
| macOS | [MacTeX](https://tug.org/mactex/) |
| Linux | TeX Live（`sudo apt install texlive-full`） |

编辑器推荐：**TeXstudio**、**VS Code + LaTeX Workshop 插件**。

### 2.2 在线平台

- **[Overleaf](https://www.overleaf.com/)**：无需安装，浏览器直接编写，适合协作和新手。

### 2.3 编译命令

```bash
# 编译为 PDF（推荐使用 xelatex，对中文和字体支持好）
xelatex main.tex

# 传统 pdflatex
pdflatex main.tex

# 带参考文献时需要多次编译
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

> **提示**：现代工具链推荐使用 `latexmk` 自动处理多次编译：
> ```bash
> latexmk -xelatex main.tex
> ```

---

## 3. 文档基本结构

一个最小的 LaTeX 文档如下：

```latex
\documentclass{article}   % 文档类

\begin{document}          % 正文开始
Hello, LaTeX!
\end{document}            % 正文结束
```

### 3.1 文档类（documentclass）

```latex
\documentclass[选项]{文档类}
```

常见文档类：

| 文档类 | 用途 |
|--------|------|
| `article` | 短文、论文 |
| `report` | 报告（有章 chapter） |
| `book` | 书籍（双面、章节） |
| `beamer` | 幻灯片 |
| `letter` | 信件 |

常见选项：

```latex
\documentclass[12pt, a4paper, twoside]{article}
% 12pt 字号，A4 纸张，双面排版
```

- 字号：`10pt`（默认）、`11pt`、`12pt`
- 纸张：`a4paper`、`letterpaper`、`b5paper`
- 分栏：`onecolumn`（默认）、`twocolumn`
- 单双面：`oneside`、`twoside`

### 3.2 导言区（Preamble）

`\documentclass` 与 `\begin{document}` 之间的部分称为**导言区**，用于加载宏包、定义命令、设置全局参数。

```latex
\documentclass{article}

% ===== 导言区 =====
\usepackage{amsmath}      % 数学公式增强
\usepackage{graphicx}     % 插入图片
\usepackage[utf8]{inputenc}

\title{我的第一篇文档}
\author{张三}
\date{\today}
% ==================

\begin{document}
\maketitle                % 生成标题
正文内容……
\end{document}
```

### 3.3 章节结构

```latex
\part{部分}
\chapter{章}          % 仅 report/book 可用
\section{节}
\subsection{小节}
\subsubsection{小小节}
\paragraph{段落}
\subparagraph{子段落}
```

带星号 `*` 的版本不编号、不进目录：

```latex
\section*{不编号的节}
```

生成目录：

```latex
\tableofcontents
```

---

## 4. 文字与段落排版

### 4.1 特殊字符转义

以下字符有特殊含义，需要转义输出：

| 字符 | 输入方式 |
|------|---------|
| `#` | `\#` |
| `$` | `\$` |
| `%` | `\%` |
| `&` | `\&` |
| `_` | `\_` |
| `{` `}` | `\{` `\}` |
| `~` | `\textasciitilde` |
| `^` | `\textasciicircum` |
| `\` | `\textbackslash` |

### 4.2 字体样式

```latex
\textbf{粗体}          % bold
\textit{斜体}          % italic
\underline{下划线}
\texttt{等宽字体}      % typewriter
\textsc{小型大写}      % small caps
\emph{强调}            % emphasis（通常斜体）
```

### 4.3 字号

```latex
\tiny \scriptsize \footnotesize \small
\normalsize
\large \Large \LARGE \huge \Huge
```

用法（作用范围用花括号限制）：

```latex
{\Large 这是大字}普通字。
```

### 4.4 段落与换行

- **空一行**表示新段落。
- `\\` 或 `\newline` 表示换行（不分段）。
- `\par` 也表示分段。
- 强制分页：`\newpage` 或 `\clearpage`。

```latex
第一段内容。

第二段内容（上面空了一行）。\\
这是第二段内的换行。
```

### 4.5 对齐

```latex
\begin{center} 居中 \end{center}
\begin{flushleft} 左对齐 \end{flushleft}
\begin{flushright} 右对齐 \end{flushright}
```

### 4.6 注释

```latex
% 这是一行注释，编译时被忽略
```

### 4.7 空格与间距

```latex
\quad       % 一个字宽的水平间距
\qquad      % 两个字宽
\,          % 微小间距
\vspace{1cm}  % 垂直间距
\hspace{2cm}  % 水平间距
```

---

## 5. 数学公式

数学是 LaTeX 的核心优势。**务必在导言区加载 `amsmath` 宏包**。

```latex
\usepackage{amsmath, amssymb}
```

### 5.1 行内公式与行间公式

```latex
行内公式：$E = mc^2$，嵌在文字中。

行间公式（居中、不编号）：
\[
  E = mc^2
\]

行间公式（居中、带编号）：
\begin{equation}
  E = mc^2
\end{equation}
```

> **不推荐**使用旧式的 `$$...$$`，请用 `\[...\]` 或 `equation` 环境。

### 5.2 上标与下标

```latex
$x^2$          % 上标
$x_i$          % 下标
$x_i^2$        % 同时
$x^{2n}$       % 多字符需用花括号
$x_{i,j}$
```

### 5.3 分数、根号

```latex
$\frac{a}{b}$          % 分数
$\dfrac{a}{b}$         % 行内显示大分数
$\sqrt{x}$             % 平方根
$\sqrt[3]{x}$          % 立方根
```

### 5.4 常用符号

```latex
% 希腊字母
$\alpha \beta \gamma \delta \pi \theta \lambda \mu \sigma \omega$
$\Gamma \Delta \Theta \Lambda \Pi \Sigma \Omega$

% 运算符
$\times \div \pm \mp \cdot \ast$
$\leq \geq \neq \approx \equiv \sim \propto$
$\subset \supset \in \notin \cup \cap$
$\rightarrow \Rightarrow \leftrightarrow \Leftrightarrow$
$\infty \partial \nabla \forall \exists$
```

### 5.5 求和、积分、极限

```latex
$\sum_{i=1}^{n} i$
$\prod_{i=1}^{n} i$
$\int_{a}^{b} f(x)\,dx$
$\iint \iiint \oint$
$\lim_{x \to \infty} f(x)$
```

### 5.6 矩阵

```latex
\begin{equation}
A =
\begin{pmatrix}   % 圆括号，还有 bmatrix[方括号] vmatrix[竖线] Bmatrix[花括号]
  a & b \\
  c & d
\end{pmatrix}
\end{equation}
```

### 5.7 多行公式对齐

使用 `align` 环境，用 `&` 对齐（通常对齐等号）：

```latex
\begin{align}
  f(x) &= (x+1)^2 \\
       &= x^2 + 2x + 1
\end{align}
```

不编号版本用 `align*`。

### 5.8 分段函数

```latex
\begin{equation}
f(x) =
\begin{cases}
  x^2,  & x \geq 0 \\
  -x^2, & x < 0
\end{cases}
\end{equation}
```

### 5.9 常用函数名

直接写 `sin` 会被当作变量斜体，应使用命令：

```latex
$\sin x, \cos x, \tan x, \log x, \ln x, \exp x, \max, \min, \gcd$
```

---

## 6. 列表

### 6.1 无序列表

```latex
\begin{itemize}
  \item 第一项
  \item 第二项
    \begin{itemize}
      \item 嵌套项
    \end{itemize}
\end{itemize}
```

### 6.2 有序列表

```latex
\begin{enumerate}
  \item 第一步
  \item 第二步
\end{enumerate}
```

### 6.3 描述列表

```latex
\begin{description}
  \item[LaTeX] 一套排版系统
  \item[TeX] LaTeX 的底层引擎
\end{description}
```

> 使用 `enumitem` 宏包可自定义列表间距和编号样式：
> ```latex
> \usepackage{enumitem}
> \begin{enumerate}[label=(\alph*), itemsep=2pt]
>   \item 用 (a)(b)(c) 编号
> \end{enumerate}
> ```

---

## 7. 表格

### 7.1 基本表格

```latex
\begin{tabular}{|l|c|r|}   % l左 c中 r右对齐，| 表示竖线
  \hline
  姓名 & 年龄 & 城市 \\
  \hline
  张三 & 25 & 北京 \\
  李四 & 30 & 上海 \\
  \hline
\end{tabular}
```

- 列定义：`l`（左）、`c`（中）、`r`（右）、`p{宽度}`（定宽换行）。
- `&` 分隔单元格，`\\` 换行，`\hline` 画横线。

### 7.2 带标题的浮动表格

```latex
\begin{table}[htbp]        % 位置：here top bottom page
  \centering
  \caption{学生信息表}
  \label{tab:students}
  \begin{tabular}{lcr}
    \hline
    姓名 & 年龄 & 城市 \\
    \hline
    张三 & 25 & 北京 \\
    \hline
  \end{tabular}
\end{table}
```

### 7.3 合并单元格

```latex
% 需要 \usepackage{multirow}
\multicolumn{2}{c}{跨两列}      % 横向合并
\multirow{2}{*}{跨两行}         % 纵向合并
```

### 7.4 三线表（学术论文常用）

```latex
% \usepackage{booktabs}
\begin{tabular}{lcr}
  \toprule
  姓名 & 年龄 & 城市 \\
  \midrule
  张三 & 25 & 北京 \\
  李四 & 30 & 上海 \\
  \bottomrule
\end{tabular}
```

---

## 8. 图片与浮动体

需要加载 `graphicx` 宏包。

```latex
\usepackage{graphicx}
```

### 8.1 插入图片

```latex
\begin{figure}[htbp]
  \centering
  \includegraphics[width=0.8\textwidth]{image.png}
  \caption{示意图}
  \label{fig:demo}
\end{figure}
```

常用可选参数：

```latex
\includegraphics[width=5cm]{img}          % 指定宽度
\includegraphics[height=3cm]{img}         % 指定高度
\includegraphics[scale=0.5]{img}          % 缩放
\includegraphics[angle=90]{img}           % 旋转
\includegraphics[width=0.5\textwidth]{img} % 占文本宽度一半
```

### 8.2 并排图片

```latex
% \usepackage{subcaption}
\begin{figure}[htbp]
  \centering
  \begin{subfigure}{0.45\textwidth}
    \includegraphics[width=\linewidth]{a.png}
    \caption{子图 A}
  \end{subfigure}
  \hfill
  \begin{subfigure}{0.45\textwidth}
    \includegraphics[width=\linewidth]{b.png}
    \caption{子图 B}
  \end{subfigure}
  \caption{并排图}
\end{figure}
```

---

## 9. 交叉引用与超链接

### 9.1 交叉引用

先用 `\label{标记}` 标记，再用 `\ref{标记}` 引用（页码用 `\pageref`）：

```latex
\section{引言}\label{sec:intro}
如第 \ref{sec:intro} 节所述，见第 \pageref{sec:intro} 页。

\begin{equation}\label{eq:einstein}
  E = mc^2
\end{equation}
公式 \eqref{eq:einstein} 是著名的质能方程。   % \eqref 自动加括号
```

> **标记命名约定**：`sec:` 章节，`fig:` 图，`tab:` 表，`eq:` 公式，便于管理。

### 9.2 超链接

```latex
\usepackage{hyperlink}   % 注意：真实宏包名是 hyperref
\usepackage{hyperref}

\href{https://www.latex-project.org}{LaTeX 官网}   % 带文字的链接
\url{https://www.overleaf.com}                     % 直接显示网址
```

`hyperref` 还会自动让目录、引用可点击跳转。

---

## 10. 参考文献

### 10.1 手动方式（thebibliography）

```latex
\begin{thebibliography}{99}
  \bibitem{knuth} Knuth, D. \emph{The TeXbook}. 1984.
\end{thebibliography}

正文中引用：\cite{knuth}
```

### 10.2 BibTeX 方式（推荐）

创建 `refs.bib` 文件：

```bibtex
@book{knuth1984,
  author    = {Donald E. Knuth},
  title     = {The TeXbook},
  publisher = {Addison-Wesley},
  year      = {1984}
}

@article{einstein1905,
  author  = {Albert Einstein},
  title   = {Zur Elektrodynamik bewegter Körper},
  journal = {Annalen der Physik},
  year    = {1905}
}
```

正文中：

```latex
\usepackage{cite}

正文引用 \cite{knuth1984} 和 \cite{einstein1905}。

\bibliographystyle{plain}   % 样式：plain, ieeetr, unsrt 等
\bibliography{refs}         % 不带 .bib 后缀
```

### 10.3 BibLaTeX 方式（现代，更灵活）

```latex
\usepackage[backend=biber, style=numeric]{biblatex}
\addbibresource{refs.bib}

正文引用 \cite{knuth1984}。

\printbibliography
```

> 使用 biblatex 需用 `biber` 后端编译。

---

## 11. 自定义命令与宏

### 11.1 定义新命令

```latex
\newcommand{\R}{\mathbb{R}}              % 无参数
\newcommand{\abs}[1]{\left| #1 \right|}  % 一个参数 #1
\newcommand{\pd}[2]{\frac{\partial #1}{\partial #2}}  % 两个参数

% 使用
$\R$              % 输出实数集符号
$\abs{x}$         % 输出 |x|
$\pd{f}{x}$       % 偏导数
```

### 11.2 带默认值的参数

```latex
\newcommand{\greet}[2][你好]{#1，#2！}
\greet{世界}          % 输出：你好，世界！
\greet[Hi]{World}     % 输出：Hi，World！
```

### 11.3 定义新环境

```latex
\newenvironment{note}
  {\begin{quote}\textbf{注意：}}   % 环境开始
  {\end{quote}}                    % 环境结束

\begin{note}
  这是一段提示文字。
\end{note}
```

### 11.4 定理类环境

```latex
\usepackage{amsthm}
\newtheorem{theorem}{定理}[section]   % 按节编号
\newtheorem{lemma}{引理}

\begin{theorem}[勾股定理]
  直角三角形中 $a^2 + b^2 = c^2$。
\end{theorem}
```

---

## 12. 页面布局与页眉页脚

### 12.1 页边距

```latex
\usepackage[margin=2.5cm]{geometry}
% 或分别设置
\usepackage[top=3cm, bottom=2cm, left=2.5cm, right=2.5cm]{geometry}
```

### 12.2 行距

```latex
\usepackage{setspace}
\onehalfspacing    % 1.5 倍行距
\doublespacing     % 双倍行距
% 或局部
\begin{spacing}{1.5} 这段是 1.5 倍行距 \end{spacing}
```

### 12.3 页眉页脚

```latex
\usepackage{fancyhdr}
\pagestyle{fancy}
\fancyhf{}                       % 清空默认
\lhead{左页眉}
\chead{中页眉}
\rhead{右页眉}
\lfoot{左页脚}
\cfoot{\thepage}                 % 页脚中间显示页码
\rfoot{右页脚}
```

---

## 13. 中文支持

### 13.1 推荐方案：ctex 宏包 + XeLaTeX

```latex
\documentclass{ctexart}   % 中文文章类（还有 ctexrep, ctexbook）

\begin{document}
你好，世界！这是中文 LaTeX 文档。
\end{document}
```

或在普通文档类中加载宏包：

```latex
\documentclass{article}
\usepackage{ctex}
```

> **编译时必须使用 `xelatex`**，否则中文可能无法显示。

### 13.2 设置字体

```latex
\usepackage{ctex}
\setCJKmainfont{SimSun}      % 宋体
\setCJKsansfont{SimHei}      % 黑体
```

---

## 14. 常用宏包速查

| 宏包 | 功能 |
|------|------|
| `amsmath` | 数学公式增强 |
| `amssymb` | 更多数学符号 |
| `amsthm` | 定理环境 |
| `graphicx` | 插入图片 |
| `geometry` | 页面尺寸/边距 |
| `hyperref` | 超链接、书签 |
| `booktabs` | 专业三线表 |
| `multirow` | 表格合并单元格 |
| `xcolor` | 颜色支持 |
| `listings` | 代码高亮 |
| `enumitem` | 自定义列表 |
| `caption` / `subcaption` | 标题/子图 |
| `fancyhdr` | 页眉页脚 |
| `setspace` | 行距 |
| `ctex` | 中文支持 |
| `tikz` | 绘图 |
| `float` | 浮动体位置控制（`[H]`） |

### 代码高亮示例（listings）

```latex
\usepackage{listings}
\usepackage{xcolor}

\lstset{
  language=Python,
  basicstyle=\ttfamily\small,
  keywordstyle=\color{blue},
  commentstyle=\color{green!60!black},
  numbers=left,
  frame=single
}

\begin{lstlisting}
def hello():
    print("Hello, LaTeX!")
\end{lstlisting}
```

---

## 15. 常见错误与调试

| 错误信息 | 原因与解决 |
|----------|-----------|
| `Undefined control sequence` | 命令拼写错误，或缺少宏包 |
| `Missing $ inserted` | 数学符号写在文本模式，需加 `$...$` |
| `Runaway argument` | 花括号 `{}` 不匹配 |
| `File not found` | 图片/文件路径错误 |
| `Missing \begin{document}` | 导言区放了正文内容 |
| `! LaTeX Error: Something's wrong--perhaps a missing \item` | 列表环境缺少 `\item` |
| 中文不显示 | 未用 `ctex` 或未用 `xelatex` 编译 |

### 调试技巧

1. **逐段注释**：出错时注释掉部分内容，缩小定位范围。
2. **看第一个错误**：LaTeX 报错常连锁，优先解决第一个。
3. **检查括号匹配**：`{}`、`\begin{}...\end{}` 必须成对。
4. **删除辅助文件**：编译异常时删除 `.aux`、`.toc` 等中间文件重新编译。

---

## 16. 学习资源

- **官方文档**：[The LaTeX Project](https://www.latex-project.org/)
- **在线编辑器**：[Overleaf](https://www.overleaf.com/)（含大量文档教程）
- **速查手册**：Overleaf 的 [Learn LaTeX in 30 minutes](https://www.overleaf.com/learn/latex/Learn_LaTeX_in_30_minutes)
- **符号查询**：[Detexify](https://detexify.kirelabs.org/)（手写识别 LaTeX 符号）
- **社区问答**：[TeX Stack Exchange](https://tex.stackexchange.com/)
- **经典书籍**：《LaTeX 入门》（刘海洋著，中文推荐）

---

## 附录：完整示例文档

```latex
\documentclass[12pt, a4paper]{ctexart}

\usepackage{amsmath, amssymb}
\usepackage{graphicx}
\usepackage[margin=2.5cm]{geometry}
\usepackage{hyperref}
\usepackage{booktabs}

\title{LaTeX 学习示例}
\author{你的名字}
\date{\today}

\begin{document}

\maketitle
\tableofcontents

\section{引言}\label{sec:intro}
这是一篇 LaTeX 示例文档，用于演示常见语法。

\section{数学公式}
著名的质能方程如公式 \eqref{eq:emc2} 所示：
\begin{equation}\label{eq:emc2}
  E = mc^2
\end{equation}

多行推导：
\begin{align}
  (a+b)^2 &= (a+b)(a+b) \\
          &= a^2 + 2ab + b^2
\end{align}

\section{表格}
\begin{table}[htbp]
  \centering
  \caption{示例数据}
  \begin{tabular}{lcr}
    \toprule
    项目 & 数量 & 价格 \\
    \midrule
    苹果 & 3 & 15 \\
    香蕉 & 5 & 10 \\
    \bottomrule
  \end{tabular}
\end{table}

\section{列表}
\begin{itemize}
  \item 第一点
  \item 第二点
\end{itemize}

更多资料见 \href{https://www.overleaf.com}{Overleaf}。

\end{document}
```

---

*本资料可作为 LaTeX 学习和查阅手册。建议边学边在 [Overleaf](https://www.overleaf.com/) 上动手实践。*
