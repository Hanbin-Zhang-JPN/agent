/* ============================================================
 * 文件：04-flow/if_switch.c
 * 主题：条件判断
 * 学习点：if 单分支 / else 双分支 / else if 多分支 / switch
 * ============================================================ */

#include <stdio.h>                 // 引入标准输入输出库

int main(void)
{
    int score = 85;                // 模拟一个成绩分数

    // 1. if 单分支：条件成立才执行花括号里的代码
    if (score >= 60) {             // 85 >= 60 成立，进入
        printf("及格了\n");        // 会打印
    }

    // 2. if / else 双分支：二选一，必走其一
    if (score >= 60) {             // 成立走这里
        printf("通过了\n");
    } else {                       // 不成立走这里
        printf("没通过\n");
    }

    // 3. if / else if 多分支：从上往下匹配，命中一个就结束
    if (score >= 90) {             // 85 不满足
        printf("等级：A\n");
    } else if (score >= 75) {      // 85 满足，进入
        printf("等级：B\n");
    } else if (score >= 60) {      // 不再判断
        printf("等级：C\n");
    } else {                       // 兜底：以上都不满足
        printf("等级：D\n");
    }

    // 4. switch：适合"变量等于某个具体值"的多选一
    int day = 3;                   // 模拟星期几
    switch (day) {                 // switch 后面跟要判断的变量
        case 1:                    // day 等于 1 时
            printf("星期一\n");
            break;                 // break 跳出 switch，不能省略
        case 2:                    // day 等于 2 时
            printf("星期二\n");
            break;
        case 3:                    // day 等于 3 时
            printf("星期三\n");
            break;
        default:                   // 都不匹配时执行
            printf("其他\n");
            break;
    }

    return 0;                      // 程序正常结束
}                                  // main 函数结束
