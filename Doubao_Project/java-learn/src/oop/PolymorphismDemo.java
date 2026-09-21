package oop; // 声明包名：本文件属于 oop（面向对象）包

/**
 * 多态演示 —— "父类引用指向子类对象"，运行时决定调用哪个方法
 *
 * 学习目标：
 *   1. 掌握向上转型：Animal a = new Dog(...)，a 的类型是父类
 *   2. 理解动态绑定：调用方法时，实际执行的是对象的真实类型的方法
 *   3. 会用 instanceof 判断对象的真实类型
 *
 * 依赖说明：本示例复用了 InheritanceDemo.java 中定义的 Animal / Dog 类，
 *           同一个包（oop）内的类可以互相引用。
 *
 * 运行方式：./run.sh oop.PolymorphismDemo
 */
public class PolymorphismDemo { // 定义公开类

    public static void main(String[] args) { // 主方法入口

        // 向上转型：声明类型是 Animal，实际对象是 Dog
        Animal pet = new Dog("小黑"); // 父类引用"指向"子类对象

        // 调用 speak()：编译看声明类型，运行看实际类型（动态绑定）
        pet.speak(); // 实际执行的是 Dog 重写后的"汪汪叫"

        // instanceof：判断对象的真实类型是否是指定类或其子类
        if (pet instanceof Dog) {        // pet 真实类型确实是 Dog
            System.out.println("pet 确实是 Dog 类型"); // 输出提示
        }

        // 多态的核心价值：同一段代码可以处理多种子类对象
        // 例如方法参数写成父类类型，就能接收所有子类对象
        makeItSpeak(new Dog("大黄")); // 传入 Dog 对象也能调用
    } // main 方法结束

    /** 接收父类类型参数：任何 Animal 的子类都能传进来 */
    public static void makeItSpeak(Animal animal) { // 参数类型是父类
        animal.speak(); // 具体执行哪个版本的 speak，由传入对象的类型决定
    }
} // 类结束
