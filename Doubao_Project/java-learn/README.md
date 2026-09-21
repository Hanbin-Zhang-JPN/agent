# Java 语法学习项目（java-learn）

一个 **零外部依赖、纯 JDK** 的 Java 语法学习项目。
每个源文件的 **每一行都有简洁的中文注释**，按主题分模块，适合从零开始学 Java 语法，也适合随时回来查某个知识点。

---

## 一、这个项目是做什么的？

- **目的**：用一个个"能直接运行"的小示例，把 Java 的核心语法讲清楚。
- **原则**：不引入 Maven / Gradle，不引入任何第三方库，只用 JDK 自带的 `javac` 和 `java`。
  因此每个文件都能独立看懂、独立编译运行，不存在"黑盒依赖"。
- **风格**：代码行内注释覆盖每一行，注释短小清晰，不啰嗦、不刺眼。

---

## 二、环境要求

| 项目 | 要求 |
| ---- | ---- |
| JDK | 11 及以上（推荐 17 或 21 LTS），本项目在 JDK 21 下验证通过 |
| 操作系统 | macOS / Linux / Windows（脚本 `compile.sh` / `run.sh` 为 bash 脚本，Windows 可用 Git Bash 运行） |

> 检查你的 Java：终端执行 `java -version`，能看到版本号即可。

---

## 三、目录结构与组成

```
java-learn/
├── README.md                 # 本说明文件
├── compile.sh                # 一键编译脚本（编译全部源码到 out/ 目录）
├── run.sh                    # 一键运行脚本（运行指定示例类）
├── .gitignore                # git 忽略规则（忽略编译产物 out/ 等）
└── src/                      # 全部源码，按主题分成 8 个包
    ├── basics/               # 01 基础语法
    ├── oop/                  # 02 面向对象
    ├── collection/           # 03 集合框架
    ├── exception/            # 04 异常处理
    ├── generic/              # 05 泛型
    ├── io/                   # 06 文件读写（IO）
    ├── thread/               # 07 多线程
    └── lambda/               # 08 函数式编程（Lambda / Stream）
```

### 各模块内容明细（建议按此顺序学习）

| 序号 | 包名 | 文件 | 讲解内容 |
| ---- | ---- | ---- | ---- |
| 01 | `basics` | `HelloWorld` | 第一个程序、main 入口、输出语句 |
| | | `DataTypeDemo` | 8 种基本类型、String、var、final 常量 |
| | | `OperatorDemo` | 算术、赋值、比较、逻辑、三元运算符 |
| | | `ControlFlowDemo` | if-else、switch、for、while、do-while、break、continue |
| | | `ArrayDemo` | 一维/二维数组、下标访问、增强 for 遍历 |
| | | `MethodDemo` | 方法定义、传参返回、方法重载、递归 |
| 02 | `oop` | `ClassObjectDemo` | 类、对象、构造器、this、static 静态成员 |
| | | `EncapsulationDemo` | 封装、private、getter/setter、业务校验 |
| | | `InheritanceDemo` | 继承、extends、super、方法重写 @Override |
| | | `PolymorphismDemo` | 多态、向上转型、动态绑定、instanceof |
| | | `AbstractDemo` | 抽象类、抽象方法 |
| | | `InterfaceDemo` | 接口、implements、多接口实现、default 方法 |
| 03 | `collection` | `ListDemo` | List / ArrayList 增删改查与遍历 |
| | | `SetDemo` | Set / HashSet 去重、TreeSet 排序 |
| | | `MapDemo` | Map / HashMap 键值对、三种遍历方式 |
| 04 | `exception` | `ExceptionDemo` | try-catch-finally、throws、throw、自定义异常 |
| 05 | `generic` | `GenericDemo` | 泛型类、泛型方法、上界 `extends` |
| 06 | `io` | `FileIODemo` | 文件写入/读取、BufferedReader/Writer、try-with-resources |
| 07 | `thread` | `ThreadDemo` | 继承 Thread、实现 Runnable、start/join/sleep |
| 08 | `lambda` | `LambdaStreamDemo` | Lambda 语法、Stream 的 filter/map/sorted/collect、方法引用 |

> 小提示：`oop` 包里的 `PolymorphismDemo` 复用了 `InheritanceDemo` 中定义的类，这正好演示了"同一个包内的类可以互相引用"这一知识点。

---

## 四、怎么运行？

项目提供了两个脚本，全部操作都在终端完成：

```bash
# 1. 进入项目目录
cd java-learn

# 2. 一键编译所有源码
./compile.sh

# 3. 运行任意一个示例（包名.类名）
./run.sh basics.HelloWorld
./run.sh basics.DataTypeDemo
./run.sh oop.InheritanceDemo
./run.sh collection.MapDemo
./run.sh lambda.LambdaStreamDemo
```

也可以手动用 JDK 命令（了解原理）：

```bash
# 编译：-encoding UTF-8 保证中文注释不乱码，-d out 指定输出目录
javac -encoding UTF-8 -d out $(find src -name "*.java")

# 运行：-cp out 指定类路径
java -cp out basics.HelloWorld
```

> 所有示例类都带有 `main` 方法，运行后会在终端打印结果，可直接对照源码观察输出。

---

## 五、项目特点与设计说明

1. **零依赖**：不使用构建工具，不引入任何 jar 包，所有代码只依赖 JDK 标准库。
2. **每行注释**：每个文件的重要代码行都配有中文注释，重要知识点还有方法级说明。
3. **注释清爽**：注释遵循"一句话说清"原则，配合代码缩进，读起来不累眼。
4. **模块清晰**：目录名短小直观（basics / oop / collection…），README 有完整对照表。
5. **可直接运行**：每个文件都是独立完整的程序，编译后逐个运行即可看到效果。
6. **中文输出**：示例程序内部会打印中文说明，方便观察程序行为。

---

## 六、适合哪些人？

- **Java 初学者**：按 01 → 08 的顺序逐个阅读并运行，循序渐进。
- **准备面试/考试的人**：需要快速复习某个知识点时，直接跳到对应文件。
- **想看懂 Java 代码的人**：本项目代码量小、注释全，是最佳的"第一份阅读材料"。

---

## 七、已知限制与说明

- 项目刻意未使用 Maven/Gradle，因此不包含依赖管理、单元测试框架等工程化能力；如需工程化，可在此基础上引入。
- 部分示例（如 `io` 模块）会读写当前目录下的临时文件，运行结束后会自动清理。
- 脚本 `compile.sh` / `run.sh` 为 bash 脚本，Windows 原生 CMD 请直接使用上面的 `javac` / `java` 手动命令。
