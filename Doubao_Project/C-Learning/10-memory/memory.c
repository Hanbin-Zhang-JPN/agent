/* ============================================================
 * 文件：10-memory/memory.c
 * 主题：动态内存
 * 学习点：malloc 申请 / 判断失败 / 像数组一样使用 / free 释放
 * ============================================================ */

#include <stdio.h>                 // 引入标准输入输出库
#include <stdlib.h>                // malloc 和 free 函数在这里声明

int main(void)
{
    // 1. 动态申请：程序运行时才决定需要多大空间
    int n = 5;                     // 需要的元素个数
    int *arr = (int *)malloc(n * sizeof(int));  // 申请能放 5 个 int 的空间
    if (arr == NULL) {             // 申请失败会返回 NULL（空指针）
        printf("内存申请失败\n");  // 提示失败
        return 1;                  // 返回非 0 表示异常结束
    }

    // 2. 使用申请到的空间：用法和数组一模一样
    for (int i = 0; i < n; i++) {  // i 从 0 到 4
        arr[i] = i * i;            // 存入 i 的平方
    }
    for (int i = 0; i < n; i++) {  // 再遍历一遍
        printf("arr[%d] = %d\n", i, arr[i]);   // 打印每个元素
    }

    // 3. 用完必须释放，把空间还给系统
    free(arr);                     // free 释放 malloc 申请的内存
    arr = NULL;                    // 置空防止误用，是好习惯

    return 0;                      // 程序正常结束
}                                  // main 函数结束
