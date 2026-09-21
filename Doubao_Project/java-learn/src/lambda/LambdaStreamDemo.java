package lambda; // 声明包名：本文件属于 lambda（函数式编程）包

// 导入函数式接口和流工具
import java.util.Arrays;   // 数组工具类
import java.util.List;     // 列表接口
import java.util.stream.Collectors; // 把流收集回集合

/**
 * Lambda 与 Stream 演示 —— Java 8 带来的函数式编程写法
 *
 * 学习目标：
 *   1. 掌握 Lambda 表达式的语法：(参数) -> 实现
 *   2. 掌握 Stream 流水线：filter 过滤 / map 转换 / forEach 遍历
 *   3. 掌握方法引用：类名::方法名 的简写
 *
 * 运行方式：./run.sh lambda.LambdaStreamDemo
 */
public class LambdaStreamDemo { // 定义公开类

    // 准备一组测试数据：整数列表
    static List<Integer> numbers = Arrays.asList(5, 3, 8, 1, 9, 2, 7, 6); // 原始数据

    public static void main(String[] args) { // 主方法入口

        // ========== 1. Lambda 基本语法 ==========
        // Runnable 是函数式接口，可以用 Lambda 实现
        Runnable task = () -> System.out.println("Lambda 跑起来了"); // 箭头函数
        task.run(); // 调用 run 方法

        // ========== 2. forEach：遍历每个元素 ==========
        System.out.print("全部元素：");
        numbers.forEach(n -> System.out.print(n + " ")); // 对每个 n 打印
        System.out.println(); // 换行

        // ========== 3. filter：过滤出符合条件的元素 ==========
        System.out.print("偶数：");
        numbers.stream()                // 把列表转成流
               .filter(n -> n % 2 == 0) // 只保留偶数
               .forEach(n -> System.out.print(n + " ")); // 打印结果
        System.out.println(); // 换行

        // ========== 4. map：把每个元素做一次转换 ==========
        System.out.print("每个数 × 10：");
        numbers.stream()                      // 转成流
               .map(n -> n * 10)              // 每个元素乘 10
               .forEach(n -> System.out.print(n + " ")); // 打印结果
        System.out.println(); // 换行

        // ========== 5. sorted：排序 ==========
        System.out.print("升序排列：");
        numbers.stream()                      // 转成流
               .sorted()                      // 默认升序排序
               .forEach(n -> System.out.print(n + " ")); // 打印结果
        System.out.println(); // 换行

        // ========== 6. collect：把流结果收集回列表 ==========
        List<Integer> evens = numbers.stream() // 转成流
                .filter(n -> n % 2 == 0)       // 过滤出偶数
                .collect(Collectors.toList()); // 收集成新列表
        System.out.println("收集到的偶数列表：" + evens); // 打印新列表

        // ========== 7. 方法引用：类名::方法名 的简写 ==========
        System.out.print("用方法引用打印：");
        numbers.stream()                    // 转成流
               .limit(3)                    // 只取前 3 个
               .forEach(System.out::print); // 等价于 n -> System.out.print(n)
        System.out.println(); // 换行
    } // main 方法结束
} // 类结束
