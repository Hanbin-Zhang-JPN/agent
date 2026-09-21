/* ============================================================
 * 文件：08-string/string.c
 * 主题：字符串
 * 学习点：字符数组 / 字符串长度 / 复制 / 比较 / 遍历
 * ============================================================ */

#include <stdio.h>                 // 引入标准输入输出库
#include <string.h>                // 字符串函数 strlen / strcpy / strcmp 在这里

int main(void)
{
    // 1. 字符串本质是字符数组，以 \0（空字符）结尾
    char str[] = "hello";          // 等价于 {'h','e','l','l','o','\0'}
    printf("%s\n", str);           // %s 输出整个字符串

    // 2. 用 strlen 求长度（不含结尾的 \0）
    int len = strlen(str);         // strlen 返回字符个数
    printf("长度：%d\n", len);     // 输出 5

    // 3. 用 strcpy 复制字符串（不能直接用 = 赋值）
    char copy[20];                 // 目标数组要足够大
    strcpy(copy, str);             // 把 str 的内容复制进 copy
    printf("复制结果：%s\n", copy);

    // 4. 用 strcmp 比较字符串（不能直接用 ==）
    char a[] = "apple";            // 第一个字符串
    char b[] = "apple";            // 第二个字符串
    int cmp = strcmp(a, b);        // 相等返回 0；a 大返回正数；a 小返回负数
    printf("比较结果：%d\n", cmp); // 输出 0，表示两个字符串相等

    // 5. 用循环逐个字符遍历，遇到 \0 说明到末尾
    for (int i = 0; str[i] != '\0'; i++) {   // 条件：不是结束符就继续
        printf("%c ", str[i]);               // 一个字符一个字符打印
    }
    printf("\n");                  // 打印完换行

    return 0;                      // 程序正常结束
}                                  // main 函数结束
