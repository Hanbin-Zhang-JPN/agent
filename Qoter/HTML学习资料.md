# HTML 语法学习详细资料

> 一份系统、由浅入深的 HTML 学习手册。适合零基础入门，也可作为速查参考。

---

## 目录

1. [HTML 是什么](#1-html-是什么)
2. [文档基本结构](#2-文档基本结构)
3. [核心概念：元素、标签、属性](#3-核心概念元素标签属性)
4. [文本相关标签](#4-文本相关标签)
5. [列表](#5-列表)
6. [链接与图片](#6-链接与图片)
7. [表格](#7-表格)
8. [表单](#8-表单)
9. [语义化标签](#9-语义化标签)
10. [多媒体：音频与视频](#10-多媒体音频与视频)
11. [常用全局属性](#11-常用全局属性)
12. [字符实体](#12-字符实体)
13. [块级元素 vs 行内元素](#13-块级元素-vs-行内元素)
14. [最佳实践](#14-最佳实践)
15. [完整示例页面](#15-完整示例页面)
16. [学习路线与练习](#16-学习路线与练习)

---

## 1. HTML 是什么

**HTML**（HyperText Markup Language，超文本标记语言）是构建网页的基础语言。它使用"标签"来描述网页内容的**结构**和**语义**，例如标题、段落、链接、图片等。

- **HTML** 负责结构（内容是什么）
- **CSS** 负责表现（长什么样）
- **JavaScript** 负责行为（能做什么）

HTML 不是编程语言，而是**标记语言**——它不做计算或逻辑，只描述内容。

---

## 2. 文档基本结构

一个标准的 HTML5 文档骨架如下：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>页面标题</title>
</head>
<body>
    <h1>你好，世界！</h1>
    <p>这是我的第一个网页。</p>
</body>
</html>
```

**各部分说明：**

| 部分 | 作用 |
|------|------|
| `<!DOCTYPE html>` | 声明文档类型为 HTML5，必须放在第一行 |
| `<html lang="zh-CN">` | 根元素，`lang` 指定页面语言，利于 SEO 和无障碍 |
| `<head>` | 元信息区，内容不直接显示在页面上 |
| `<meta charset="UTF-8">` | 指定字符编码，防止中文乱码 |
| `<meta name="viewport" ...>` | 响应式设置，让页面适配移动端 |
| `<title>` | 浏览器标签页显示的标题 |
| `<body>` | 页面主体，所有可见内容都在这里 |

---

## 3. 核心概念：元素、标签、属性

### 元素（Element）

一个完整元素通常由**开始标签**、**内容**和**结束标签**组成：

```html
<p>这是一个段落。</p>
```

- `<p>` — 开始标签
- `这是一个段落。` — 内容
- `</p>` — 结束标签

### 空元素（自闭合）

有些元素没有内容，也没有结束标签，称为**空元素**：

```html
<br>       <!-- 换行 -->
<hr>       <!-- 水平分割线 -->
<img src="photo.jpg" alt="照片">
```

### 属性（Attribute）

属性为元素提供额外信息，写在开始标签内，采用 `名称="值"` 的形式：

```html
<a href="https://example.com" target="_blank">链接</a>
```

- `href` 和 `target` 是属性名
- 属性值建议用双引号包裹

### 嵌套

元素可以互相嵌套，但必须正确闭合，不能交叉：

```html
<!-- 正确 -->
<p>这是<strong>加粗</strong>的文字。</p>

<!-- 错误：交叉嵌套 -->
<p>这是<strong>加粗</p></strong>
```

### 注释

```html
<!-- 这是注释，浏览器不会显示 -->
```

---

## 4. 文本相关标签

### 标题

HTML 提供 6 级标题，`<h1>` 最重要，`<h6>` 最次要：

```html
<h1>一级标题</h1>
<h2>二级标题</h2>
<h3>三级标题</h3>
<h4>四级标题</h4>
<h5>五级标题</h5>
<h6>六级标题</h6>
```

> 一个页面通常只用一个 `<h1>`，标题层级要按顺序使用，不要跳级。

### 段落与换行

```html
<p>这是一个段落。</p>
<p>这是另一个段落。</p>

第一行<br>第二行
```

### 文本格式化

```html
<strong>重要（语义加粗）</strong>
<b>加粗（纯样式）</b>
<em>强调（语义斜体）</em>
<i>斜体（纯样式）</i>
<mark>高亮</mark>
<small>小号文字</small>
<del>删除线</del>
<ins>下划线（插入）</ins>
<sub>下标</sub> H<sub>2</sub>O
<sup>上标</sup> x<sup>2</sup>
```

> 优先使用有**语义**的 `<strong>` / `<em>`，而非仅表示外观的 `<b>` / `<i>`。

### 引用与代码

```html
<blockquote cite="来源网址">
    这是一段长引用。
</blockquote>

<q>这是短引用</q>

<code>console.log('行内代码')</code>

<pre>
    保留空格和换行的
    预格式化文本
</pre>
```

---

## 5. 列表

### 无序列表（Unordered List）

```html
<ul>
    <li>苹果</li>
    <li>香蕉</li>
    <li>橙子</li>
</ul>
```

### 有序列表（Ordered List）

```html
<ol>
    <li>第一步</li>
    <li>第二步</li>
    <li>第三步</li>
</ol>
```

### 定义列表（Description List）

```html
<dl>
    <dt>HTML</dt>
    <dd>超文本标记语言</dd>
    <dt>CSS</dt>
    <dd>层叠样式表</dd>
</dl>
```

### 嵌套列表

```html
<ul>
    <li>水果
        <ul>
            <li>苹果</li>
            <li>香蕉</li>
        </ul>
    </li>
    <li>蔬菜</li>
</ul>
```

---

## 6. 链接与图片

### 链接（Anchor）

```html
<!-- 外部链接，新窗口打开 -->
<a href="https://example.com" target="_blank" rel="noopener">访问网站</a>

<!-- 内部页面 -->
<a href="about.html">关于我们</a>

<!-- 页面内锚点跳转 -->
<a href="#section2">跳到第二节</a>
<h2 id="section2">第二节</h2>

<!-- 邮件与电话 -->
<a href="mailto:hi@example.com">发邮件</a>
<a href="tel:+8613800138000">打电话</a>
```

> `target="_blank"` 建议搭配 `rel="noopener"`，提升安全性。

### 图片（Image）

```html
<img src="images/cat.jpg" alt="一只橘猫" width="300" height="200">
```

- `src` — 图片路径（必需）
- `alt` — 替代文本，图片加载失败或屏幕阅读器会用到（必需，利于无障碍与 SEO）
- `width` / `height` — 尺寸（像素）

### 响应式图片

```html
<img src="small.jpg"
     srcset="small.jpg 480w, large.jpg 1080w"
     sizes="(max-width: 600px) 480px, 1080px"
     alt="风景图">
```

---

## 7. 表格

```html
<table>
    <caption>学生成绩表</caption>
    <thead>
        <tr>
            <th>姓名</th>
            <th>语文</th>
            <th>数学</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>张三</td>
            <td>90</td>
            <td>85</td>
        </tr>
        <tr>
            <td>李四</td>
            <td>88</td>
            <td>92</td>
        </tr>
    </tbody>
    <tfoot>
        <tr>
            <td>平均</td>
            <td>89</td>
            <td>88.5</td>
        </tr>
    </tfoot>
</table>
```

**关键标签：**

| 标签 | 含义 |
|------|------|
| `<table>` | 表格容器 |
| `<caption>` | 表格标题 |
| `<thead>` / `<tbody>` / `<tfoot>` | 表头 / 表体 / 表尾 |
| `<tr>` | 表格行（table row） |
| `<th>` | 表头单元格（默认加粗居中） |
| `<td>` | 数据单元格（table data） |

**合并单元格：**

```html
<td colspan="2">跨两列</td>
<td rowspan="3">跨三行</td>
```

---

## 8. 表单

表单用于收集用户输入。

```html
<form action="/submit" method="post">
    <!-- 文本输入 -->
    <label for="name">姓名：</label>
    <input type="text" id="name" name="name" placeholder="请输入姓名" required>

    <!-- 密码 -->
    <label for="pwd">密码：</label>
    <input type="password" id="pwd" name="pwd">

    <!-- 邮箱 -->
    <input type="email" name="email">

    <!-- 单选按钮 -->
    <input type="radio" id="male" name="gender" value="male">
    <label for="male">男</label>
    <input type="radio" id="female" name="gender" value="female">
    <label for="female">女</label>

    <!-- 复选框 -->
    <input type="checkbox" id="agree" name="agree">
    <label for="agree">同意协议</label>

    <!-- 下拉选择 -->
    <label for="city">城市：</label>
    <select id="city" name="city">
        <option value="bj">北京</option>
        <option value="sh">上海</option>
    </select>

    <!-- 多行文本 -->
    <label for="msg">留言：</label>
    <textarea id="msg" name="msg" rows="4" cols="30"></textarea>

    <!-- 其他常用输入类型 -->
    <input type="number" min="0" max="100">
    <input type="date">
    <input type="range" min="0" max="10">
    <input type="color">
    <input type="file">

    <!-- 按钮 -->
    <button type="submit">提交</button>
    <button type="reset">重置</button>
</form>
```

**表单要点：**

- `<label>` 的 `for` 应与 `<input>` 的 `id` 对应，点击文字即可聚焦输入框
- `name` 属性决定提交时的字段名，非常重要
- 常用属性：`required`（必填）、`placeholder`（提示）、`disabled`（禁用）、`readonly`（只读）
- `method` 常用 `get`（数据显示在 URL）或 `post`（数据在请求体中）

---

## 9. 语义化标签

HTML5 引入了描述页面结构的语义标签，替代无意义的 `<div>`：

```html
<body>
    <header>页头：Logo、导航等</header>

    <nav>
        <ul>
            <li><a href="#">首页</a></li>
            <li><a href="#">关于</a></li>
        </ul>
    </nav>

    <main>
        <article>
            <h2>文章标题</h2>
            <section>
                <h3>章节标题</h3>
                <p>章节内容……</p>
            </section>
        </article>

        <aside>侧边栏：相关链接、广告等</aside>
    </main>

    <footer>页脚：版权信息等</footer>
</body>
```

| 标签 | 用途 |
|------|------|
| `<header>` | 页头或区块头部 |
| `<nav>` | 导航链接区 |
| `<main>` | 主要内容（每页只应有一个） |
| `<article>` | 独立、可自成一体的内容（如一篇博客） |
| `<section>` | 主题性内容分区 |
| `<aside>` | 侧边、附属内容 |
| `<footer>` | 页脚或区块底部 |
| `<figure>` / `<figcaption>` | 图片/图表及其说明 |

**语义化的好处：** 利于 SEO、无障碍访问（屏幕阅读器）、代码可读性。

---

## 10. 多媒体：音频与视频

```html
<!-- 音频 -->
<audio controls>
    <source src="music.mp3" type="audio/mpeg">
    您的浏览器不支持音频播放。
</audio>

<!-- 视频 -->
<video controls width="640" poster="cover.jpg">
    <source src="movie.mp4" type="video/mp4">
    <source src="movie.webm" type="video/webm">
    您的浏览器不支持视频播放。
</video>

<!-- 嵌入外部内容（如地图、YouTube） -->
<iframe src="https://example.com" width="600" height="400" title="嵌入页面"></iframe>
```

常用属性：`controls`（显示控件）、`autoplay`（自动播放）、`loop`（循环）、`muted`（静音）。

---

## 11. 常用全局属性

这些属性几乎可用于所有元素：

| 属性 | 作用 |
|------|------|
| `id` | 元素唯一标识（页面内唯一） |
| `class` | 类名，用于 CSS/JS 选择（可多个，空格分隔） |
| `style` | 内联样式 |
| `title` | 鼠标悬停提示文字 |
| `data-*` | 自定义数据属性，如 `data-user-id="5"` |
| `hidden` | 隐藏元素 |
| `contenteditable` | 内容是否可编辑 |
| `tabindex` | 控制 Tab 键聚焦顺序 |

```html
<div id="header" class="container dark" title="提示" data-role="banner">
    内容
</div>
```

---

## 12. 字符实体

某些字符在 HTML 中有特殊含义，需要用**实体**表示：

| 字符 | 实体 | 说明 |
|------|------|------|
| `<` | `&lt;` | 小于号 |
| `>` | `&gt;` | 大于号 |
| `&` | `&amp;` | & 符号 |
| `"` | `&quot;` | 双引号 |
| 空格 | `&nbsp;` | 不换行空格 |
| `©` | `&copy;` | 版权符号 |
| `®` | `&reg;` | 注册商标 |

```html
<p>使用 &lt;p&gt; 标签定义段落。</p>
<p>版权所有 &copy; 2026</p>
```

---

## 13. 块级元素 vs 行内元素

### 块级元素（Block）

- 独占一行，前后自动换行
- 可设置宽高
- 例：`<div>`、`<p>`、`<h1>~<h6>`、`<ul>`、`<li>`、`<section>` 等

### 行内元素（Inline）

- 不换行，与其他内容同行显示
- 宽高由内容决定
- 例：`<span>`、`<a>`、`<strong>`、`<em>`、`<img>` 等

```html
<div>块级元素，独占一行</div>
<span>行内</span><span>元素，同一行</span>
```

> 注意：这是 HTML 元素的**默认**显示特性，可通过 CSS 的 `display` 属性改变。

---

## 14. 最佳实践

1. **始终声明 `<!DOCTYPE html>`** 和字符编码 `UTF-8`。
2. **使用小写标签和属性名**，属性值加双引号。
3. **图片必须写 `alt`**，利于无障碍与 SEO。
4. **优先使用语义化标签**，而非到处 `<div>`。
5. **正确嵌套、正确闭合**元素。
6. **表单控件配 `<label>`**，提升可用性。
7. **结构与样式分离**：样式交给 CSS，别滥用内联 `style`。
8. **标题层级有序**，一个页面一个 `<h1>`。
9. **保持代码缩进整洁**，便于维护。
10. **验证 HTML**：可用 [W3C Validator](https://validator.w3.org/) 检查错误。

---

## 15. 完整示例页面

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>我的个人主页</title>
</head>
<body>
    <header>
        <h1>张三的个人主页</h1>
        <nav>
            <ul>
                <li><a href="#about">关于我</a></li>
                <li><a href="#skills">技能</a></li>
                <li><a href="#contact">联系</a></li>
            </ul>
        </nav>
    </header>

    <main>
        <section id="about">
            <h2>关于我</h2>
            <p>我是一名<strong>前端开发者</strong>，热爱学习新技术。</p>
        </section>

        <section id="skills">
            <h2>我的技能</h2>
            <ul>
                <li>HTML</li>
                <li>CSS</li>
                <li>JavaScript</li>
            </ul>
        </section>

        <section id="contact">
            <h2>联系我</h2>
            <form action="/submit" method="post">
                <label for="name">姓名：</label>
                <input type="text" id="name" name="name" required>
                <br>
                <label for="email">邮箱：</label>
                <input type="email" id="email" name="email" required>
                <br>
                <button type="submit">发送</button>
            </form>
        </section>
    </main>

    <footer>
        <p>版权所有 &copy; 2026 张三</p>
    </footer>
</body>
</html>
```

---

## 16. 学习路线与练习

### 建议学习顺序

1. 掌握文档结构与基础标签（标题、段落、列表）
2. 学会链接、图片、表格
3. 熟悉表单及各种输入类型
4. 理解语义化标签，写出结构清晰的页面
5. 学习块级/行内元素的区别
6. 进阶：多媒体、iframe、响应式图片
7. 之后进入 **CSS**（样式）和 **JavaScript**（交互）

### 练习建议

- **个人简历页**：用语义化标签 + 列表 + 图片
- **产品展示页**：表格 + 图片 + 链接
- **注册表单**：各种 input 类型 + label + 校验属性
- **博客文章页**：`<article>` + `<section>` + 引用 + 代码块

### 推荐资源

- [MDN Web Docs（权威文档，中文）](https://developer.mozilla.org/zh-CN/docs/Web/HTML)
- [W3C HTML 校验器](https://validator.w3.org/)
- [W3Schools HTML 教程](https://www.w3schools.com/html/)

---

> **记住**：HTML 是网页的骨架。先把结构写正确、写语义化，再用 CSS 美化、用 JavaScript 添加交互。多写多练是最快的学习方式！
