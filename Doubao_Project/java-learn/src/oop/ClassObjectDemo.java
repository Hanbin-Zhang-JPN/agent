package oop; // 声明包名：本文件属于 oop（面向对象）包

/**
 * 类与对象演示 —— 认识类的三大成员：属性、构造器、方法
 *
 * 学习目标：
 *   1. 明白"类"是模板，"对象"是模板造出来的实例
 *   2. 掌握构造器（构造方法）的用法和 this 关键字
 *   3. 区分实例成员（属于对象）和静态成员（属于类）
 *
 * 运行方式：./run.sh oop.ClassObjectDemo
 */
public class ClassObjectDemo { // 定义公开类

    // ========== 类的属性（成员变量）：描述对象的特征 ==========
    String name;      // 姓名（实例属性，每个对象各自拥有一份）
    int age;          // 年龄（实例属性）
    static String school = "Java 大学"; // 静态属性，所有对象共享一份

    // ========== 构造器（构造方法）：创建对象时自动执行 ==========
    // 方法名必须与类名相同，且没有返回值类型
    public ClassObjectDemo(String name, int age) { // 带参构造器
        this.name = name; // this 指向当前对象，区分"属性name"和"参数name"
        this.age = age;   // 把传入的年龄赋给当前对象的属性
    }

    // ========== 普通方法：描述对象的行为 ==========
    public void introduce() {         // 实例方法，属于对象
        // 直接访问实例属性，无需加 this 前缀
        System.out.println("我是 " + name + "，今年 " + age + " 岁");
    }

    public static void main(String[] args) { // 主方法入口

        // new 关键字调用构造器，创建一个对象（实例）
        ClassObjectDemo stu1 = new ClassObjectDemo("小红", 18); // 造出第一个对象
        ClassObjectDemo stu2 = new ClassObjectDemo("小刚", 20); // 造出第二个对象

        stu1.introduce(); // 调用 stu1 自己的方法
        stu2.introduce(); // 调用 stu2 自己的方法（各自的数据互不影响）

        // 通过"对象.属性"访问实例属性
        System.out.println(stu1.name + " 明年 " + (stu1.age + 1) + " 岁"); // 修改演示

        // 通过"类名.属性"访问静态属性（属于类，不依赖具体对象）
        System.out.println("学校：" + ClassObjectDemo.school); // 静态属性共享
    } // main 方法结束
} // 类结束
