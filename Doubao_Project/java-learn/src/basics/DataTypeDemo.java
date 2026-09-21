package basics; // 声明包名：本文件属于 basics（基础语法）包

/**
 * 数据类型演示 —— 认识 Java 的 8 种基本类型和引用类型 String
 *
 * 学习目标：
 *   1. 记住基本类型：byte short int long float double char boolean
 *   2. 区分"基本类型存值"和"引用类型存地址"
 *   3. 了解整型/浮点型的默认值和字面量写法
 *
 * 运行方式：./run.sh basics.DataTypeDemo
 */
public class DataTypeDemo { // 定义公开类

    public static void main(String[] args) { // 主方法入口

        // ========== 1. 整型：存整数 ==========
        byte b = 100;          // byte：1 字节，范围 -128 ~ 127
        short s = 30000;       // short：2 字节，范围约 ±3.2 万
        int age = 25;          // int：4 字节，最常用的整数类型
        long money = 10000000000L; // long：8 字节，末尾加 L 表示长整型

        // ========== 2. 浮点型：存小数 ==========
        float height = 1.75f;      // float：4 字节，末尾加 f 表示单精度
        double weight = 62.5;      // double：8 字节，Java 默认小数类型

        // ========== 3. 字符与布尔 ==========
        char grade = 'A';      // char：2 字节，用单引号包单个字符
        boolean isOk = true;   // boolean：只有 true / false 两个值

        // ========== 4. 引用类型 String ==========
        // String 存的是"字符串的地址"，不是值本身
        String name = "小明";   // 双引号包一串字符

        // ========== 5. var：让编译器自动推断类型（Java 10+）==========
        var city = "东京";      // 编译器自动推断 city 是 String
        var score = 98;        // 编译器自动推断 score 是 int

        // ========== 6. final：常量，赋值后不可修改 ==========
        final double PI = 3.14159; // 常量名习惯全大写

        // 把上面的变量都打印出来，方便对照观察
        System.out.println("byte=" + b);     // 字符串用 + 拼接变量
        System.out.println("short=" + s);    // 拼接输出 short
        System.out.println("int=" + age);    // 拼接输出 int
        System.out.println("long=" + money); // 拼接输出 long
        System.out.println("float=" + height);   // 输出小数
        System.out.println("double=" + weight);  // 输出小数
        System.out.println("char=" + grade);     // 输出字符
        System.out.println("boolean=" + isOk);   // 输出布尔
        System.out.println("String=" + name);    // 输出字符串
        System.out.println("var city=" + city);  // 输出自动推断结果
        System.out.println("var score=" + score);// 输出自动推断结果
        System.out.println("final PI=" + PI);    // 输出常量
    } // main 方法结束
} // 类结束
