package basics; // 声明包名：本文件属于 basics（基础语法）包

/**
 * 方法演示 —— 把一段可复用的逻辑封装成方法
 *
 * 学习目标：
 *   1. 掌握方法的定义：修饰符 返回值类型 方法名(参数)
 *   2. 理解"传参、返回"两个方向的流转
 *   3. 会用方法重载（同名不同参）
 *   4. 会用递归解决"自己调自己"的问题
 *
 * 运行方式：./run.sh basics.MethodDemo
 */
public class MethodDemo { // 定义公开类

    public static void main(String[] args) { // 主方法入口

        // 调用下面自定义的方法，把返回值接住并打印
        int sum = add(3, 4);          // 调用 add 方法，3 和 4 是实参
        System.out.println("3 + 4 = " + sum); // 输出 7

        sayHello("小明");             // 调用无返回值方法（void）
        System.out.println("重载测试 2.5 + 3.5 = " + add(2.5, 3.5)); // 调用小数版重载

        int result = factorial(5);    // 调用递归方法：5 的阶乘
        System.out.println("5! = " + result); // 输出 120
    } // main 方法结束

    /**
     * 加法：接收两个整数，返回它们的和
     * @param x 第一个加数
     * @param y 第二个加数
     * @return x + y 的结果
     */
    public static int add(int x, int y) { // 返回值类型 int
        return x + y;                     // return 把结果返回给调用方
    }

    /**
     * 方法重载：方法名相同，但参数类型不同
     * 编译器根据实参类型自动选择调用哪个版本
     */
    public static double add(double x, double y) { // 参数是 double
        return x + y;                             // 返回 double
    }

    /**
     * 无返回值方法：void 表示不返回任何东西
     * @param name 要问候的人名
     */
    public static void sayHello(String name) { // void 无返回值
        System.out.println("你好，" + name + "！"); // 只做打印
    }

    /**
     * 递归：方法内部调用自己
     * n! = n × (n-1) × ... × 1，边界是 1! = 1
     * @param n 目标数字
     * @return n 的阶乘
     */
    public static int factorial(int n) {  // 递归方法
        if (n == 1) {                     // 边界条件：防止无限递归
            return 1;                     // 1 的阶乘就是 1
        }
        return n * factorial(n - 1);      // n! = n * (n-1)!
    }
} // 类结束
