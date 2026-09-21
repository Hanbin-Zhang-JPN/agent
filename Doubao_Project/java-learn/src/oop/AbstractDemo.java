package oop; // 声明包名：本文件属于 oop（面向对象）包

/**
 * 抽象类演示 —— 用 abstract 定义"只有声明、没有实现"的方法
 *
 * 学习目标：
 *   1. 明白抽象类：不能 new 出对象，只能被继承
 *   2. 掌握抽象方法：只声明方法签名，由子类去实现
 *   3. 理解抽象类的价值：把"共同的行为约定"抽取出来
 *
 * 运行方式：./run.sh oop.AbstractDemo
 */

// ========== 抽象类：Shape（图形）==========
abstract class Shape {          // abstract 修饰的类就是抽象类
    String name;                // 属性：图形名字

    /** 构造器：所有子类共用 */
    public Shape(String name) { // 抽象类可以有构造器
        this.name = name;       // 保存名字
    }

    /** 抽象方法：只声明不实现，强制子类必须实现 */
    public abstract double area(); // 没有方法体，只有分号结尾

    /** 普通方法：可以直接定义实现，子类也能继承 */
    public void showName() {        // 具体方法
        System.out.println("图形：" + name); // 打印名字
    }
}

// ========== 子类：Circle（圆形）==========
class Circle extends Shape {    // 继承抽象类
    double radius;              // 属性：半径

    /** 构造器：接收名字和半径 */
    public Circle(String name, double radius) { // 构造器
        super(name);            // 调用父类构造器
        this.radius = radius;   // 保存半径
    }

    /** 实现抽象方法：圆的面积 = π × r² */
    @Override                   // 标记这是重写
    public double area() {      // 实现父类声明的抽象方法
        return Math.PI * radius * radius; // 返回面积
    }
}

// ========== 子类：Rect（矩形）==========
class Rect extends Shape {      // 继承抽象类
    double width;               // 属性：宽
    double height;              // 属性：高

    /** 构造器：接收名字、宽、高 */
    public Rect(String name, double width, double height) { // 构造器
        super(name);            // 调用父类构造器
        this.width = width;     // 保存宽
        this.height = height;   // 保存高
    }

    /** 实现抽象方法：矩形面积 = 宽 × 高 */
    @Override                   // 标记这是重写
    public double area() {      // 实现父类声明的抽象方法
        return width * height;  // 返回面积
    }
}

// ========== 主类：负责演示 ==========
public class AbstractDemo {     // 公开类，文件名与之对应
    public static void main(String[] args) { // 主方法入口
        Shape circle = new Circle("小圆", 2.0); // 多态：父类引用指向子类
        Shape rect = new Rect("方框", 3.0, 4.0); // 多态：另一个子类

        circle.showName();      // 调用父类普通方法
        System.out.println("圆的面积：" + circle.area()); // 调用子类实现

        rect.showName();        // 调用父类普通方法
        System.out.println("矩形的面积：" + rect.area()); // 调用子类实现
    } // main 方法结束
} // 类结束
