/* ============================================================
 * 文件：12-practice/guess.c
 * 主题：综合练习一：猜数字游戏
 * 用到：随机数 / while 循环 / if 分支 / scanf 输入
 * 玩法：程序随机生成 1~100 的数字，你来猜，直到猜对
 * ============================================================ */

#include <stdio.h>                 // 引入标准输入输出库
#include <stdlib.h>                // rand / srand 在这里
#include <time.h>                  // time 在这里

int main(void)
{
    // 1. 设置随机数种子：用当前时间，让每次运行结果不同
    srand((unsigned int)time(NULL));

    // 2. 随机生成 1~100 之间的目标数字
    int target = rand() % 100 + 1; // % 100 得到 0~99，加 1 变成 1~100
    int guess = 0;                 // 玩家猜的数字
    int tries = 0;                 // 猜的次数

    printf("猜数字游戏开始！范围 1~100\n");

    // 3. 循环猜，直到猜对为止
    while (1) {                    // 1 恒为真，配合 break 退出
        printf("请输入你猜的数字：");
        scanf("%d", &guess);       // 读取玩家输入的数字
        tries++;                   // 猜的次数加 1

        if (guess > target) {      // 猜大了
            printf("大了，再试试\n");
        } else if (guess < target) {  // 猜小了
            printf("小了，再试试\n");
        } else {                   // 猜中了
            printf("恭喜猜对！答案是 %d，共猜了 %d 次\n", target, tries);
            break;                 // 退出循环，游戏结束
        }
    }

    return 0;                      // 程序正常结束
}                                  // main 函数结束
