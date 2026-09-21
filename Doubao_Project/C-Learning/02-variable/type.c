/* ============================================================
 * 文件：02-variable/type.c
 * 主题：常见数据类型
 * 学习点：int / float / double / char / sizeof 查看字节数
 * ============================================================ */

#include <stdio.h>                 // printf 需要这个库

int main(void)
{
    // 1. 整数类型：最常用
    int n = 100;                   // int 通常占 4 字节，能存正负数

    // 2. 小数类型
    float f = 3.14f;               // float 单精度，字面量要加 f 后缀
    double d = 3.1415926;          // double 双精度，精度更高，优先用它

    // 3. 字符类型：单引号包一个字符
    char c = 'A';                  // char 占 1 字节，存的是字符编码

    // 4. 无符号整数：只存正数，正数范围翻一倍
    unsigned int u = 300;          // unsigned 修饰词去掉符号位

    // 5. 用占位符输出各种类型
    printf("int       = %d\n", n);          // %d 输出整数
    printf("float     = %.2f\n", f);        // %.2f 保留 2 位小数
    printf("double    = %.4f\n", d);        // %.4f 保留 4 位小数
    printf("char      = %c\n", c);          // %c 输出单个字符
    printf("unsigned  = %u\n", u);          // %u 输出无符号整数

    // 6. sizeof 返回类型占用的字节数
    printf("int 占 %zu 字节\n", sizeof(int));       // %zu 对应 size_t 类型
    printf("double 占 %zu 字节\n", sizeof(double));

    return 0;                      // 程序正常结束
}                                  // main 函数结束
