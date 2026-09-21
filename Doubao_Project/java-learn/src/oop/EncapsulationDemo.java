package oop; // 声明包名：本文件属于 oop（面向对象）包

/**
 * 封装演示 —— 用 private 保护数据，用 getter/setter 提供受控访问
 *
 * 学习目标：
 *   1. 明白为什么要封装：防止外部随意改动数据、破坏程序
 *   2. 掌握 private 私有属性的用法
 *   3. 用 getter（读取）和 setter（修改+校验）控制访问
 *
 * 运行方式：./run.sh oop.EncapsulationDemo
 */
public class EncapsulationDemo { // 定义公开类

    // private 属性：外部无法直接访问，只能通过方法间接操作
    private String password; // 密码（私有，外部不能直接读写）
    private int balance;     // 余额（私有）

    /** 构造器：创建账户时初始化密码和余额 */
    public EncapsulationDemo(String password, int balance) { // 带参构造器
        this.password = password; // 初始化私有密码
        this.balance = balance;   // 初始化私有余额
    }

    /** getter：读取余额（只读，不能修改） */
    public int getBalance() {  // getter 命名规范：get + 属性名首字母大写
        return balance;        // 返回当前余额
    }

    /** 存款方法：带业务校验，而不是让外部直接改 balance */
    public void deposit(int money) {     // 存钱
        if (money <= 0) {                // 校验：金额必须为正
            System.out.println("存款金额必须大于 0"); // 拒绝非法操作
            return;                      // 提前结束方法
        }
        balance += money;                // 校验通过才累加余额
        System.out.println("存入 " + money + " 元，当前余额 " + balance); // 反馈
    }

    /** 校验密码：外部想验证密码只能走这个方法 */
    public boolean checkPassword(String input) { // 检查密码是否正确
        return this.password.equals(input);      // 返回比对结果
    }

    public static void main(String[] args) { // 主方法入口
        EncapsulationDemo account = new EncapsulationDemo("123456", 100); // 建账户
        System.out.println("初始余额：" + account.getBalance()); // 用 getter 读取

        account.deposit(200); // 正常存款 200
        account.deposit(-50); // 非法存款 -50，会被方法内部的校验拦下

        System.out.println("密码输入 123456 是否正确：" + account.checkPassword("123456")); // true
        System.out.println("密码输入 000000 是否正确：" + account.checkPassword("000000")); // false
    } // main 方法结束
} // 类结束
