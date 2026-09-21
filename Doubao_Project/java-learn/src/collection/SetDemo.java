package collection; // 声明包名：本文件属于 collection（集合框架）包

// 导入需要用到的集合类
import java.util.HashSet; // HashSet：基于哈希表，无序、去重
import java.util.Set;     // Set 接口：不包含重复元素的集合
import java.util.TreeSet; // TreeSet：基于红黑树，自动升序排序

/**
 * Set 演示 —— 无序（或有序）、不重复的集合
 *
 * 学习目标：
 *   1. 掌握 HashSet 的去重特性
 *   2. 掌握 TreeSet 的自动排序特性
 *   3. 记住 Set 没有下标，只能遍历，不能 get(i)
 *
 * 运行方式：./run.sh collection.SetDemo
 */
public class SetDemo { // 定义公开类

    public static void main(String[] args) { // 主方法入口

        // ========== 1. HashSet：去重，但顺序不保证 ==========
        Set<String> names = new HashSet<>(); // 创建哈希集合
        names.add("小明"); // 加入第一个元素
        names.add("小红"); // 加入第二个元素
        names.add("小明"); // 重复加入，会被自动去重
        names.add("小刚"); // 加入第三个元素

        System.out.println("HashSet 内容：" + names); // 只有 3 个，顺序不固定
        System.out.println("元素个数：" + names.size()); // 3，重复的被去掉

        // ========== 2. TreeSet：自动按升序排序 ==========
        Set<Integer> numbers = new TreeSet<>(); // 创建树形集合
        numbers.add(50); // 加入 50
        numbers.add(10); // 加入 10
        numbers.add(30); // 加入 30
        numbers.add(10); // 重复的 10 会被去掉

        System.out.println("TreeSet 内容：" + numbers); // 输出 [10, 30, 50]，自动排序

        // ========== 3. 常用操作 ==========
        System.out.println("是否包含 30：" + numbers.contains(30)); // true
        numbers.remove(30); // 删除元素 30
        System.out.println("删除后：" + numbers); // [10, 50]

        // ========== 4. 遍历（Set 没有下标，只能用增强 for）==========
        System.out.print("遍历 names：");
        for (String name : names) { // 每轮取出一个元素
            System.out.print(name + " "); // 依次打印
        }
        System.out.println(); // 换行
    } // main 方法结束
} // 类结束
