package basics; // 声明包名：本文件属于 basics（基础语法）包

/**
 * 运算符演示 —— 算数、赋值、比较、逻辑、三元
 *
 * 学习目标：
 *   1. 掌握 + - * / % 等算术运算符
 *   2. 了解 ++ -- 自增自减的两种位置差异
 *   3. 会用比较运算符和逻辑运算符组成判断条件
 *   4. 会用三元运算符简化简单的 if-else
 *
 * 运行方式：./run.sh basics.OperatorDemo
 */
public class OperatorDemo { // 定义公开类

    public static void main(String[] args) { // 主方法入口

        // ========== 1. 算术运算符 ==========
        int a = 10;     // 定义第一个操作数
        int b = 3;      // 定义第二个操作数
        System.out.println("a + b = " + (a + b)); // 加法：10+3=13
        System.out.println("a - b = " + (a - b)); // 减法：10-3=7
        System.out.println("a * b = " + (a * b)); // 乘法：10*3=30
        System.out.println("a / b = " + (a / b)); // 整除：整数相除只留整数部分=3
        System.out.println("a % b = " + (a % b)); // 取余：10 除以 3 余 1

        // ========== 2. 自增自减（注意前置与后置的区别）==========
        int x = 5;          // 准备一个整数
        x++;                // 后置自增：先用后加，x 变成 6
        System.out.println("x++ 后 x = " + x); // 输出 6
        ++x;                // 前置自增：先加后用，x 变成 7
        System.out.println("++x 后 x = " + x); // 输出 7

        // ========== 3. 赋值运算符（含复合赋值）==========
        int n = 10;     // 直接赋值
        n += 5;         // 等价于 n = n + 5，n 变成 15
        n -= 3;         // 等价于 n = n - 3，n 变成 12
        n *= 2;         // 等价于 n = n * 2，n 变成 24
        n /= 4;         // 等价于 n = n / 4，n 变成 6
        System.out.println("复合赋值后 n = " + n); // 输出 6

        // ========== 4. 比较运算符（结果都是布尔值）==========
        int p = 8;          // 准备数据
        int q = 8;          // 准备数据
        System.out.println("p == q : " + (p == q)); // 等于，输出 true
        System.out.println("p != q : " + (p != q)); // 不等于，输出 false
        System.out.println("p >= q : " + (p >= q)); // 大于等于，输出 true
        System.out.println("p < q  : " + (p < q));  // 小于，输出 false

        // ========== 5. 逻辑运算符（用于组合多个条件）==========
        boolean sunny = true;   // 今天是晴天
        boolean warm = false;   // 今天不暖和
        System.out.println("晴天 && 暖和 : " + (sunny && warm)); // 与：都真才真
        System.out.println("晴天 || 暖和 : " + (sunny || warm)); // 或：一真即真
        System.out.println("!晴天 : " + (!sunny));                // 非：取反

        // ========== 6. 三元运算符（if-else 的简写）==========
        int score = 85;                 // 准备一个分数
        String result = score >= 60 ? "及格" : "不及格"; // 条件 ? 真值 : 假值
        System.out.println("成绩判定：" + result);        // 输出"及格"
    } // main 方法结束
} // 类结束
