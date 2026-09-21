package oop; // 声明包名：本文件属于 oop（面向对象）包

/**
 * 接口演示 —— 用 interface 定义"能力约定"，用 implements 去实现
 *
 * 学习目标：
 *   1. 掌握 interface 定义方法和 implements 实现接口
 *   2. 理解"一个类可以实现多个接口"，弥补单继承的限制
 *   3. 了解接口的默认方法（default）和常量
 *
 * 运行方式：./run.sh oop.InterfaceDemo
 */

// ========== 接口1：Flyable（会飞的）==========
interface Flyable {              // 接口用 interface 关键字
    /** 抽象方法：飞行能力，实现者必须给出具体做法 */
    void fly();                  // 接口中的方法默认是抽象的

    /** 接口常量：默认是 public static final */
    int MAX_SPEED = 900;         // 接口里的变量自动是常量
}

// ========== 接口2：Swimmable（会游泳的）==========
interface Swimmable {            // 第二个接口
    /** 抽象方法：游泳能力 */
    void swim();                 // 实现者必须实现
}

// ========== 实现类：Duck（鸭子），同时实现两个接口 ==========
class Duck implements Flyable, Swimmable { // 用逗号隔开多个接口
    String name;                 // 属性：名字

    /** 构造器：接收名字 */
    public Duck(String name) {   // 构造器
        this.name = name;        // 保存名字
    }

    /** 实现 Flyable 的 fly */
    @Override                    // 标记重写
    public void fly() {          // 必须实现，否则编译报错
        System.out.println(name + " 扑腾翅膀飞起来"); // 鸭子也会"飞"
    }

    /** 实现 Swimmable 的 swim */
    @Override                    // 标记重写
    public void swim() {         // 必须实现
        System.out.println(name + " 在水里游"); // 鸭子天生会游泳
    }
}

// ========== 接口带默认方法：default ==========
interface Greeter {              // 问候接口
    /** 抽象方法：打招呼内容由实现者定 */
    void greet();                // 抽象方法

    /** default 默认方法：接口里也能写有实现的方法 */
    default void hello() {       // Java 8+ 支持
        System.out.println("（默认问候）你好呀"); // 默认实现
    }
}

// ========== 主类：负责演示 ==========
public class InterfaceDemo {     // 公开类，文件名与之对应
    public static void main(String[] args) { // 主方法入口
        Duck duck = new Duck("小黄"); // 创建鸭子对象

        duck.fly();              // 调用接口1的方法
        duck.swim();             // 调用接口2的方法
        System.out.println("接口常量 MAX_SPEED = " + Flyable.MAX_SPEED); // 接口常量

        // 接口引用指向实现类对象（也是多态）
        Flyable f = new Duck("飞飞"); // 按 Flyable 接口看待鸭子
        f.fly();                 // 只能调用接口中声明的方法

        // 演示 default 方法
        Greeter greeter = new Greeter() { // 匿名内部类实现接口
            @Override            // 只实现抽象方法
            public void greet() { // 实现 greet
                System.out.println("（自定义问候）天天开心"); // 自定义内容
            }
        };
        greeter.greet();         // 调用实现的方法
        greeter.hello();         // 调用接口默认方法
    } // main 方法结束
} // 类结束
