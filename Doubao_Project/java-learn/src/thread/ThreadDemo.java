package thread; // 声明包名：本文件属于 thread（多线程）包

/**
 * 多线程演示 —— 让多个任务"同时"执行，提高效率
 *
 * 学习目标：
 *   1. 掌握两种创建线程的方式：继承 Thread、实现 Runnable
 *   2. 掌握 start() 启动线程（不是调用 run()）
 *   3. 掌握 sleep() 让线程暂停、join() 等待线程结束
 *
 * 运行方式：./run.sh thread.ThreadDemo
 */

// ========== 方式1：继承 Thread 类 ==========
class MyThread extends Thread { // 继承 Thread 变成线程类
    private String name;        // 属性：线程名称

    /** 构造器：接收名字 */
    public MyThread(String name) { // 构造器
        this.name = name;       // 保存名字
    }

    /** run()：线程启动后要执行的代码写在这里 */
    @Override
    public void run() {         // 重写 run 方法
        for (int i = 1; i <= 3; i++) { // 循环 3 次
            System.out.println(name + " 执行第 " + i + " 次"); // 打印进度
            try {
                Thread.sleep(100); // 睡 100 毫秒，模拟耗时工作
            } catch (InterruptedException e) { // 中断异常
                e.printStackTrace(); // 打印异常堆栈
            }
        }
    }
}

// ========== 方式2：实现 Runnable 接口（更推荐）==========
class MyRunnable implements Runnable { // 实现 Runnable 接口
    private String name;        // 属性：任务名称

    /** 构造器：接收名字 */
    public MyRunnable(String name) { // 构造器
        this.name = name;       // 保存名字
    }

    /** run()：任务要执行的代码 */
    @Override
    public void run() {         // 实现接口的 run
        System.out.println(name + " 任务开始执行"); // 打印开始
    }
}

// ========== 主类 ==========
public class ThreadDemo { // 定义公开类

    public static void main(String[] args) throws InterruptedException { // 主方法，声明可能中断异常
        System.out.println("主线程开始"); // 主线程提示

        // ========== 1. 用继承 Thread 的方式创建并启动线程 ==========
        MyThread t1 = new MyThread("线程A"); // 创建线程对象
        t1.start();                     // start() 启动线程（会另起一条执行流）

        // ========== 2. 用实现 Runnable 的方式创建并启动线程 ==========
        MyRunnable task = new MyRunnable("任务B"); // 创建任务对象
        Thread t2 = new Thread(task);   // 把任务包进 Thread
        t2.start();                     // 启动线程

        // ========== 3. join()：等待某个线程结束后再继续 ==========
        t1.join();                      // 主线程等 t1 跑完
        t2.join();                      // 主线程等 t2 跑完
        System.out.println("主线程结束（两个线程都已执行完毕）"); // 最后打印
    } // main 方法结束
} // 类结束
