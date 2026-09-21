package collection; // 声明包名：本文件属于 collection（集合框架）包

// 导入需要用到的集合类
import java.util.HashMap; // HashMap：键值对存储，键不重复
import java.util.Map;     // Map 接口：键值对（K-V）映射
import java.util.TreeMap; // TreeMap：按键自动排序

/**
 * Map 演示 —— 以"键-值"对方式存储数据，通过键快速取值
 *
 * 学习目标：
 *   1. 掌握 put / get / remove 的增删查
 *   2. 掌握三种遍历方式：keySet、values、entrySet
 *   3. 认识 HashMap（无序）与 TreeMap（按键排序）的区别
 *
 * 运行方式：./run.sh collection.MapDemo
 */
public class MapDemo { // 定义公开类

    public static void main(String[] args) { // 主方法入口

        // <String, Integer> 表示"键是字符串，值是整数"
        Map<String, Integer> scores = new HashMap<>(); // 创建哈希表

        // ========== 增 / 改（put）==========
        scores.put("语文", 88); // 存入键"语文"，值 88
        scores.put("数学", 95); // 存入键"数学"，值 95
        scores.put("英语", 90); // 存入键"英语"，值 90
        scores.put("数学", 100); // 键已存在：put 会覆盖旧值，变成 100

        // ========== 查（get）==========
        System.out.println("数学成绩：" + scores.get("数学")); // 按键取值，100
        System.out.println("地图大小：" + scores.size()); // 3（键去重后）
        System.out.println("是否包含键'语文'：" + scores.containsKey("语文")); // true
        System.out.println("是否包含值 95：" + scores.containsValue(95)); // true

        // ========== 删（remove）==========
        scores.remove("英语"); // 按键删除这一对数据
        System.out.println("删除后内容：" + scores); // 直接打印全部键值对

        // ========== 遍历方式1：遍历所有键 ==========
        System.out.print("所有科目：");
        for (String key : scores.keySet()) { // keySet() 返回所有键的集合
            System.out.print(key + " ");     // 依次打印键
        }
        System.out.println(); // 换行

        // ========== 遍历方式2：遍历所有值 ==========
        System.out.print("所有分数：");
        for (Integer value : scores.values()) { // values() 返回所有值的集合
            System.out.print(value + " ");      // 依次打印值
        }
        System.out.println(); // 换行

        // ========== 遍历方式3：同时取键和值 ==========
        for (Map.Entry<String, Integer> entry : scores.entrySet()) { // 每个条目
            String key = entry.getKey();   // 取出键
            Integer value = entry.getValue(); // 取出值
            System.out.println(key + " = " + value); // 成对打印
        }

        // ========== TreeMap：按键自动排序 ==========
        Map<String, String> cityMap = new TreeMap<>(); // 创建树形表
        cityMap.put("Tokyo", "东京"); // 加入东京
        cityMap.put("Osaka", "大阪"); // 加入大阪
        cityMap.put("Kyoto", "京都"); // 加入京都
        System.out.println("TreeMap 按键排序：" + cityMap); // 按键字母序排列
    } // main 方法结束
} // 类结束
