package collection; // 声明包名：本文件属于 collection（集合框架）包

// 导入需要用到的集合类，import 语句放在包声明之后
import java.util.ArrayList; // ArrayList：可自动扩容的"动态数组"
import java.util.List;      // List 接口：有序、可重复的列表

/**
 * List 演示 —— 有序、可重复、按下标访问的集合
 *
 * 学习目标：
 *   1. 掌握 ArrayList 的增删改查
 *   2. 掌握两种遍历方式：普通 for 和增强 for
 *   3. 理解 List 与数组的区别：长度可变、方法丰富
 *
 * 运行方式：./run.sh collection.ListDemo
 */
public class ListDemo { // 定义公开类

    public static void main(String[] args) { // 主方法入口

        // <String> 是泛型：规定这个列表只能装字符串
        List<String> fruits = new ArrayList<>(); // 创建空列表（钻石语法<>）

        // ========== 增 ==========
        fruits.add("苹果");   // add 追加到末尾
        fruits.add("香蕉");   // 继续追加
        fruits.add("橙子");   // 继续追加
        fruits.add(1, "葡萄"); // 重载版：在指定下标 1 处插入

        // ========== 查 ==========
        System.out.println("列表内容：" + fruits); // 直接打印整个列表
        System.out.println("元素个数：" + fruits.size()); // size() 获取长度
        System.out.println("下标 0 的元素：" + fruits.get(0)); // get 按下标取值

        // ========== 改 ==========
        fruits.set(0, "西瓜"); // set(下标, 新值)：替换指定位置的元素
        System.out.println("修改后：" + fruits); // 输出变化

        // ========== 删 ==========
        fruits.remove("香蕉");   // 按内容删除第一个匹配项
        fruits.remove(0);        // 按下标删除第 0 个
        System.out.println("删除后：" + fruits); // 输出变化

        // ========== 遍历 ==========
        System.out.print("增强 for 遍历：");
        for (String fruit : fruits) { // 每轮取出一个元素赋给 fruit
            System.out.print(fruit + " "); // 打印每个水果
        }
        System.out.println(); // 换行

        // ========== 包含判断 ==========
        System.out.println("是否包含橙子：" + fruits.contains("橙子")); // true
        System.out.println("是否为空：" + fruits.isEmpty()); // false
    } // main 方法结束
} // 类结束
