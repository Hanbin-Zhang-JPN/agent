package basics; // 声明包名：本文件属于 basics（基础语法）包

/**
 * 第一个 Java 程序 —— HelloWorld
 *
 * 学习目标：
 *   1. 认识程序入口 main 方法的固定写法
 *   2. 掌握最基本的输出语句 System.out.println
 *
 * 运行方式：./run.sh basics.HelloWorld
 */
public class HelloWorld { // 定义公开类，类名必须和文件名一致

    /**
     * 主方法：Java 程序运行的唯一入口
     * @param args 命令行传入的参数数组（这里暂不使用）
     */
    public static void main(String[] args) {
        // println = print line，打印一行文字并自动换行
        System.out.println("Hello, Java!"); // 向控制台输出问候语
    } // main 方法结束
} // 类结束
