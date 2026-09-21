package exception; // 声明包名：本文件属于 exception（异常处理）包

// 导入需要用到的类
import java.util.Scanner; // Scanner：用于读取用户输入（这里演示用）

/**
 * 异常处理演示 —— 让程序遇到错误时不崩溃，而是"优雅地处理"
 *
 * 学习目标：
 *   1. 掌握 try-catch-finally 的基本结构
 *   2. 掌握 throws 把异常抛给调用方处理
 *   3. 会用 try-with-resources 自动关闭资源
 *   4. 会自定义异常类
 *
 * 运行方式：./run.sh exception.ExceptionDemo
 */

// ========== 自定义异常类：继承 Exception ==========
class MyException extends Exception { // 自定义异常
    /** 构造器：把错误信息传给父类 */
    public MyException(String message) { // 构造器
        super(message); // 调用父类构造器保存错误信息
    }
}

// ========== 主类 ==========
public class ExceptionDemo { // 定义公开类

    public static void main(String[] args) { // 主方法入口

        // ========== 1. try-catch：捕获并处理异常 ==========
        try {                                // 把"可能出错"的代码放进来
            int result = 10 / 0;             // 除以 0 会抛出 ArithmeticException
            System.out.println(result);      // 这行不会执行到
        } catch (ArithmeticException e) {    // 捕获算术异常
            System.out.println("捕获到异常：" + e.getMessage()); // 打印错误信息
        } finally {                          // 无论是否异常都会执行
            System.out.println("finally：无论如何都会执行"); // 常用于释放资源
        }

        // ========== 2. 多分支 catch：不同类型分别处理 ==========
        String text = "abc";                 // 一个无法转成数字的字符串
        try {                                // 尝试区域
            int num = Integer.parseInt(text); // 解析会抛出 NumberFormatException
            System.out.println(num);         // 不会执行到
        } catch (NumberFormatException e) {  // 数字格式异常
            System.out.println("数字格式错误：" + e.getMessage()); // 提示信息
        } catch (Exception e) {              // 兜底：其他所有异常
            System.out.println("其他异常：" + e); // 打印完整信息
        }

        // ========== 3. 调用可能抛异常的方法（throws 声明）==========
        try {                                // 方法抛出了异常，调用方要处理
            checkAge(15);                    // 传入未成年年龄
        } catch (MyException e) {            // 捕获自定义异常
            System.out.println("自定义异常：" + e.getMessage()); // 打印信息
        }

        // ========== 4. try-with-resources：自动关闭资源 ==========
        // Scanner 实现了 AutoCloseable，用完后自动关闭，无需手动 close
        try (Scanner scanner = new Scanner("hello world")) { // 括号内声明资源
            System.out.println("读取到的第一个词：" + scanner.next()); // 取第一个词
        } // 离开 try 块时，scanner 自动关闭
    } // main 方法结束

    /**
     * 通过 throws 声明"这个方法可能会抛异常"
     * @param age 要检查的年龄
     * @throws MyException 年龄不合法时抛出
     */
    public static void checkAge(int age) throws MyException { // 声明抛出异常
        if (age < 18) {                     // 年龄小于 18
            throw new MyException("未满 18 岁不允许进入"); // throw 主动抛出异常
        }
        System.out.println("年龄合法");      // 只有年龄合法才打印
    }
} // 类结束
