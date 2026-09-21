package basics; // 声明包名：本文件属于 basics（基础语法）包

/**
 * 流程控制演示 —— 分支与循环
 *
 * 学习目标：
 *   1. 用 if-else 做多条件分支
 *   2. 用 switch 做等值匹配（Java 14+ 支持箭头写法）
 *   3. 掌握 for / while / do-while 三种循环
 *   4. 理解 break（跳出）和 continue（跳过本次）
 *
 * 运行方式：./run.sh basics.ControlFlowDemo
 */
public class ControlFlowDemo { // 定义公开类

    public static void main(String[] args) { // 主方法入口

        // ========== 1. if-else 分支 ==========
        int score = 78;             // 定义一个成绩
        if (score >= 90) {          // 条件1：90 分以上
            System.out.println("优秀");   // 满足条件1才执行
        } else if (score >= 60) {   // 条件2：60~89 分
            System.out.println("及格");   // 满足条件2才执行
        } else {                    // 兜底：其余情况
            System.out.println("不及格"); // 上面都不满足才执行
        }

        // ========== 2. switch 等值匹配（箭头写法）==========
        int day = 3;                // 假设周三是 3
        String week = switch (day) { // switch 表达式会把结果返回给 week
            case 1 -> "周一";        // day==1 时返回"周一"
            case 2 -> "周二";        // day==2 时返回"周二"
            case 3 -> "周三";        // day==3 时返回"周三"
            default -> "其他";       // 兜底值
        }; // switch 表达式以分号结尾
        System.out.println("今天是" + week); // 输出"今天是周三"

        // ========== 3. for 循环：知道次数时使用 ==========
        System.out.print("for 循环：");  // print 不换行
        for (int i = 1; i <= 5; i++) {   // 初值1；条件<=5；每次+1
            System.out.print(i + " ");   // 依次打印 1 2 3 4 5
        }
        System.out.println();            // 补一个换行

        // ========== 4. while 循环：条件满足才进入 ==========
        int sum = 0;            // 累加结果，初始为 0
        int i = 1;              // 从 1 开始累加
        while (i <= 100) {      // 只要 i 不超过 100 就继续
            sum += i;           // 累加当前 i
            i++;                // i 自增，避免死循环
        }
        System.out.println("1 加到 100 = " + sum); // 输出 5050

        // ========== 5. do-while：先执行一次再判断 ==========
        int j = 1;              // 计数器
        do {                    // 先无条件执行一次循环体
            System.out.println("do-while 第 " + j + " 次"); // 打印次数
            j++;                // 计数加一
        } while (j < 3);        // 再判断条件，满足则继续

        // ========== 6. break 与 continue ==========
        System.out.println("break 测试：找到第一个大于 3 的数就停");
        for (int k = 1; k <= 5; k++) { // 遍历 1~5
            if (k > 3) {               // 当 k 大于 3 时
                break;                 // break 立刻跳出整个循环
            }
            System.out.println("k = " + k); // 只打印 1 2 3
        }

        System.out.println("continue 测试：跳过偶数只打印奇数");
        for (int k = 1; k <= 5; k++) { // 遍历 1~5
            if (k % 2 == 0) {          // 如果是偶数
                continue;              // continue 跳过本次循环体剩余部分
            }
            System.out.println("奇数 k = " + k); // 只打印 1 3 5
        }
    } // main 方法结束
} // 类结束
