package generic; // 声明包名：本文件属于 generic（泛型）包

/**
 * 泛型演示 —— 让"类型"也成为参数，写一次代码适配多种类型
 *
 * 学习目标：
 *   1. 掌握泛型类：类名后跟 <T>，T 代表任意类型
 *   2. 掌握泛型方法：方法返回值前声明 <T>
 *   3. 掌握泛型通配符 ? 和 上界 extends
 *   4. 理解泛型的好处：编译期就检查类型，避免强转
 *
 * 运行方式：./run.sh generic.GenericDemo
 */

// ========== 泛型类：Box 盒子，可以装任意类型 ==========
class Box<T> {             // <T> 是类型参数，使用时再指定具体类型
    private T content;     // 属性：内容，类型是 T

    /** 放入内容 */
    public void put(T item) { // 参数类型也是 T
        this.content = item;  // 保存内容
    }

    /** 取出内容 */
    public T get() {          // 返回值类型是 T
        return content;       // 返回内容
    }
}

// ========== 主类 ==========
public class GenericDemo { // 定义公开类

    public static void main(String[] args) { // 主方法入口

        // 1. 装字符串的盒子：<String> 指定类型
        Box<String> stringBox = new Box<>(); // 创建字符串盒子
        stringBox.put("Hello");              // 只能放入字符串
        String s = stringBox.get();          // 取出时自动是 String，无需强转
        System.out.println("字符串盒子：" + s); // 输出 Hello

        // 2. 装整数的盒子：<Integer> 指定类型
        Box<Integer> intBox = new Box<>();   // 创建整数盒子
        intBox.put(100);                     // 只能放入整数
        int n = intBox.get();                // 取出时自动是 Integer
        System.out.println("整数盒子：" + n);  // 输出 100

        // 3. 泛型方法：传入不同类型都能正常工作
        print("任意字符串");                   // 泛型方法接收 String
        print(12345);                        // 泛型方法接收 Integer
        print(3.14);                         // 泛型方法接收 Double

        // 4. 泛型上界 <T extends Number>：方法只接受"数字及其子类"
        System.out.println("数字数组求和：" + sum(new Integer[]{1, 2, 3, 4})); // 10
        System.out.println("小数数组求和：" + sum(new Double[]{1.5, 2.5}));   // 4.0
    } // main 方法结束

    /**
     * 泛型方法：<T> 写在返回值类型前面
     * @param item 任意类型的参数
     * @param <T> 类型参数
     */
    public static <T> void print(T item) {   // 泛型方法声明
        System.out.println("泛型方法收到：" + item); // 直接打印内容
    }

    /**
     * 泛型上界：<T extends Number> 表示 T 必须是 Number 或其子类
     * 这样 Integer[]、Double[] 等数字数组都能传进来
     * @param array 任意数字类型的数组
     * @return 数组元素之和
     */
    public static <T extends Number> double sum(T[] array) { // 带上界的泛型方法
        double total = 0;          // 累加结果，用 double 存小数
        for (T item : array) {     // 遍历数组每个元素
            total += item.doubleValue(); // doubleValue() 把数字统一转成 double
        }
        return total;              // 返回总和
    }
} // 类结束
