package oop; // 声明包名：本文件属于 oop（面向对象）包

/**
 * 继承演示 —— 用 extends 复用父类的属性和方法
 *
 * 学习目标：
 *   1. 掌握 extends 关键字和"子类 is-a 父类"的关系
 *   2. 掌握 super 调用父类构造器和父类方法
 *   3. 掌握方法重写（Override）：子类改写父类方法
 *
 * 运行方式：./run.sh oop.InheritanceDemo
 */

// ========== 父类：Animal（动物）==========
class Animal {            // 父类（基类）
    String name;          // 属性：名字

    /** 父类构造器：接收名字 */
    public Animal(String name) { // 构造器
        this.name = name;        // 保存名字
    }

    /** 父类方法：叫 */
    public void speak() {              // 通用叫声方法
        System.out.println(name + " 发出叫声"); // 父类默认实现
    }
}

// ========== 子类：Dog（狗），继承 Animal ==========
class Dog extends Animal {       // extends 表示继承
    /** 子类构造器：把名字转交给父类构造器处理 */
    public Dog(String name) {
        super(name);             // super(...) 必须写在第一行，调用父类构造器
    }

    /** 重写父类的 speak 方法：狗的叫声更具体 */
    @Override                    // @Override 注解：告诉编译器"这是重写"
    public void speak() {        // 方法签名与父类保持一致
        System.out.println(name + " 汪汪叫"); // 子类自己的实现
    }
}

// ========== 主类：负责演示 ==========
public class InheritanceDemo {   // 公开类，文件名与之对应
    public static void main(String[] args) { // 主方法入口
        Dog dog = new Dog("旺财"); // 创建子类对象，构造器会联动父类构造器
        dog.speak();              // 调用的是子类重写后的方法
        System.out.println("这只狗的名字是：" + dog.name); // 继承了父类的属性
    } // main 方法结束
} // 类结束
