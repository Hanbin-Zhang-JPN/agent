package io; // 声明包名：本文件属于 io（输入输出）包

// 导入文件读写需要的类
import java.io.BufferedReader;   // 带缓冲的字符读取器：按行读很方便
import java.io.BufferedWriter;   // 带缓冲的字符写入器
import java.io.File;             // File：代表一个文件或目录
import java.io.FileReader;       // 字符文件读取流
import java.io.FileWriter;       // 字符文件写入流
import java.io.IOException;      // 输入输出异常

/**
 * 文件读写演示 —— 用纯 JDK 的字符流读写一个文本文件
 *
 * 学习目标：
 *   1. 掌握 BufferedWriter / BufferedReader 的用法
 *   2. 掌握 try-with-resources 自动关闭资源
 *   3. 掌握 File 类的基本操作：判断存在、删除
 *
 * 说明：程序会在当前目录生成一个 demo.txt 文件，运行后可以打开查看。
 *
 * 运行方式：./run.sh io.FileIODemo
 */
public class FileIODemo { // 定义公开类

    // 定义要操作的文件名（相对当前运行目录）
    private static final String FILE_NAME = "demo.txt"; // 常量：文件名

    public static void main(String[] args) { // 主方法入口

        // ========== 1. 写入文件 ==========
        // try-with-resources：括号里创建的流用完后自动关闭
        try (BufferedWriter writer = new BufferedWriter(new FileWriter(FILE_NAME))) {
            writer.write("第一行：你好，Java！"); // 写第一行内容
            writer.newLine();                  // 写入换行符
            writer.write("第二行：这是文件读写演示"); // 写第二行内容
            writer.newLine();                  // 写入换行符
            writer.write("第三行：文件操作完成");   // 写第三行内容
            writer.newLine();                  // 写入换行符
            System.out.println("✔ 已写入文件：" + FILE_NAME); // 提示写入成功
        } catch (IOException e) {              // 捕获 IO 异常
            System.out.println("写入失败：" + e.getMessage()); // 打印错误
        } // 离开 try 块时 writer 自动关闭

        // ========== 2. 读取文件 ==========
        // FileReader 按字符读，BufferedReader 加缓冲并按行读取
        try (BufferedReader reader = new BufferedReader(new FileReader(FILE_NAME))) {
            System.out.println("--- 开始读取文件内容 ---"); // 提示开始读
            String line;                            // 存放每行内容
            while ((line = reader.readLine()) != null) { // readLine 读一行，读完返回 null
                System.out.println(line);           // 打印这一行
            }
            System.out.println("--- 读取结束 ---");   // 提示读取完成
        } catch (IOException e) {                   // 捕获 IO 异常
            System.out.println("读取失败：" + e.getMessage()); // 打印错误
        } // 离开 try 块时 reader 自动关闭

        // ========== 3. File 类基本操作 ==========
        File file = new File(FILE_NAME); // 用文件路径创建 File 对象
        System.out.println("文件是否存在：" + file.exists()); // true
        System.out.println("文件大小（字节）：" + file.length()); // 字节数

        // 演示结束后删除临时文件，保持目录整洁
        if (file.delete()) {             // delete 删除文件，成功返回 true
            System.out.println("已删除临时文件：" + FILE_NAME); // 提示删除成功
        }
    } // main 方法结束
} // 类结束
