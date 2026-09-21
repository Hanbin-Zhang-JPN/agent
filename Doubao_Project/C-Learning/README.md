# C 语言学习项目（C-Learning）

> 面向 C 语言初学者的入门项目：知识点拆成小节、每个示例逐行中文注释、一条命令全部编译运行。

---

## 一、项目目的

很多初学者学 C 语言时，最大的障碍是"语法看了，代码却读不懂"。
这个项目把 C 语言的核心知识点拆分成一个个**短小、独立、可直接编译运行**的示例文件，
并且给每一行代码都加上简洁的中文注释，让你：

- 不用查资料，也能看懂每一行代码在做什么；
- 按章节顺序学习，一步步建立起完整的知识体系；
- 边读、边改、边运行，把"看懂"真正变成"会写"。

项目按 **12 个章节**组织，从最基础的"第一个程序"到综合练习，
覆盖 C 语言入门阶段必须掌握的绝大部分内容。

---

## 二、目录结构总览

| 文件夹 | 章节主题 | 包含文件 | 学习要点 |
| --- | --- | --- | --- |
| 01-hello | 第一个程序 | hello.c | main 函数、printf 输出、return 返回 |
| 02-variable | 变量与数据类型 | variable.c / type.c | 变量声明与赋值、int/float/char、sizeof |
| 03-operator | 运算符 | operator.c | 算术、关系、逻辑、赋值运算符 |
| 04-flow | 流程控制 | if_switch.c / loop.c | if、switch、for、while、break、continue |
| 05-array | 数组 | array.c | 一维数组、二维数组、循环遍历 |
| 06-function | 函数 | function.c | 函数定义、返回值、值传递 |
| 07-pointer | 指针 | pointer.c | 地址、解引用、指针与数组、指针交换 |
| 08-string | 字符串 | string.c | 字符数组、strlen / strcpy / strcmp |
| 09-struct | 结构体 | struct.c | 结构体定义、成员访问、结构体数组 |
| 10-memory | 动态内存 | memory.c | malloc 申请、free 释放、判空 |
| 11-file | 文件操作 | file.c | fopen / fclose、写入、逐行读取 |
| 12-practice | 综合练习 | guess.c / grade.c | 猜数字游戏、学生成绩统计 |

> 文件夹命名规则：`章节序号-英文关键词`。序号保证学习顺序，关键词一眼看出主题。

---

## 三、环境准备

C 语言需要先安装编译器，按你的系统三选一：

**Windows**
- 方式一（推荐）：安装 [WinLibs](https://winlibs.com/) 一键包（自带 gcc 和 make），
  或到 [MinGW-w64](https://www.mingw-w64.org/) 官网安装；
- 方式二：使用 [WSL](https://learn.microsoft.com/zh-cn/windows/wsl/install)（Windows 自带 Linux 子系统）；
- 方式三：安装自带编译器的 IDE，如 Dev-C++、Code::Blocks。

**macOS**
- 打开终端执行：`xcode-select --install`（安装命令行工具，自带 clang/gcc 和 make）

**Linux（Debian / Ubuntu）**
- 执行：`sudo apt install gcc make`

安装完成后，在终端输入下面命令验证：

```bash
gcc --version
```

能显示版本号，说明环境就绪，可以开始学习了。

---

## 四、编译与运行

### 方式一：Makefile 一键编译（推荐）

在项目根目录（与 Makefile 同一层）打开终端：

```bash
make                          # 编译全部章节，产物统一输出到 build/ 目录
make build/01-hello/hello     # 只编译某一个文件（后面会讲）
make clean                    # 删除所有编译产物
```

运行编译出的程序：

```bash
# macOS / Linux
./build/01-hello/hello

# Windows
build\01-hello\hello.exe
```

### 方式二：手动用 gcc 编译单个文件

```bash
gcc -Wall -o hello 01-hello/hello.c   # 编译：-o 指定输出文件名
./hello                               # 运行（Windows 下是 hello.exe）
```

> 小知识：`-Wall` 用于开启常见警告，是练习 C 语言时的好习惯。

---

## 五、注释与代码风格约定

为了让注释"清爽不累眼"，整个项目统一遵守以下规则：

1. 行注释统一用 `//`，不用 `/* */` 包单行；
2. 每个文件顶部用块注释说明：文件作用、主题、学习点；
3. 代码右侧的注释尽量**对齐到同一列**，整块看起来整齐；
4. 逻辑段用 `// 1. 主题`、`// 2. 主题` 编号，方便定位；
5. 花括号 `{` 不写注释（视觉上已足够清晰），函数结尾的 `}` 标注函数名；
6. 逻辑块之间空一行，代码和注释都保持简短。

---

## 六、建议学习顺序

```
第一阶段（打基础）：01-hello → 02-variable → 03-operator
第二阶段（学语法）：04-flow   → 05-array   → 06-function
第三阶段（核心难点）：07-pointer → 08-string → 09-struct
第四阶段（进阶应用）：10-memory  → 11-file
第五阶段（综合实战）：12-practice（尝试独立完成，检验学习成果）
```

建议节奏：每天 1~2 个小节。看完注释后**亲手修改几个数值再运行**，
比只看不动效果好得多。

---

## 七、常见问题（FAQ）

**Q1：提示 gcc 不是内部或外部命令 / command not found**
A：编译器没安装或没加入 PATH，回到"三、环境准备"完成安装。

**Q2：运行程序时窗口一闪而过**
A：这是双击运行导致的。请在终端里执行编译命令和运行命令。

**Q3：中文输出乱码**
A：确保源文件以 UTF-8 保存；Windows 终端可先执行 `chcp 65001` 再运行程序。

**Q4：运行 11-file 后多了一个 note.txt**
A：这是文件章节的示例程序**故意生成的**演示文件，说明"写入文件"成功，
内容可以放心删除。

**Q5：猜数字游戏输入字母会卡住**
A：`scanf` 读取数字失败时会陷入循环，这是教学示例的简化写法，
只要输入数字就能正常游玩。

---

## 八、学习建议

1. 先读注释、再读代码、最后自己动手敲一遍；
2. 每章学完，尝试"不看注释复述代码含义"；
3. 遇到报错别慌，先读错误信息的第一行，从文件路径和行号入手；
4. 完成 12-practice 后，尝试自己写一个"通讯录"小程序来检验所学。

祝你学习愉快，早日写出自己的第一个 C 项目！
