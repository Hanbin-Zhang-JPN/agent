package basics; // 声明包名：本文件属于 basics（基础语法）包

/**
 * 数组演示 —— 一组相同类型数据的容器
 *
 * 学习目标：
 *   1. 掌握数组的两种创建方式：静态初始化和动态初始化
 *   2. 用下标访问数组元素（下标从 0 开始）
 *   3. 用增强 for 循环（foreach）遍历数组
 *   4. 认识二维数组
 *
 * 运行方式：./run.sh basics.ArrayDemo
 */
public class ArrayDemo { // 定义公开类

    public static void main(String[] args) { // 主方法入口

        // ========== 1. 静态初始化：创建时就给好值 ==========
        int[] scores = {88, 92, 75, 60}; // int[] 表示整数数组，大括号直接给值

        // ========== 2. 动态初始化：先定长度再逐个赋值 ==========
        String[] names = new String[3]; // 创建长度 3 的字符串数组，默认全是 null
        names[0] = "张三";               // 下标 0 放第一个名字
        names[1] = "李四";               // 下标 1 放第二个名字
        names[2] = "王五";               // 下标 2 放第三个名字

        // ========== 3. 下标访问 ==========
        System.out.println("第一个成绩：" + scores[0]); // 下标 0 是第一个元素
        System.out.println("数组长度：" + scores.length); // .length 获取长度

        // ========== 4. 普通 for 循环遍历 ==========
        System.out.print("普通 for 遍历成绩：");
        for (int i = 0; i < scores.length; i++) { // 下标从 0 到 length-1
            System.out.print(scores[i] + " ");    // 按下标逐个打印
        }
        System.out.println(); // 换行

        // ========== 5. 增强 for（foreach）：只取值，不管下标 ==========
        System.out.print("增强 for 遍历姓名：");
        for (String name : names) {  // 每轮把 names 里的一个元素赋给 name
            System.out.print(name + " "); // 依次打印张三 李四 王五
        }
        System.out.println(); // 换行

        // ========== 6. 二维数组：数组套数组，可看作表格 ==========
        int[][] table = {          // 定义一个 2 行 3 列的表
            {1, 2, 3},             // 第 0 行
            {4, 5, 6}              // 第 1 行
        };
        System.out.println("二维数组 [1][2] = " + table[1][2]); // 第1行第2列=6
    } // main 方法结束
} // 类结束
