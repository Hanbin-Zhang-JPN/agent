/* ============================================================
 * 文件：11-file/file.c
 * 主题：文件读写
 * 学习点：fopen 打开 / fprintf 写入 / fgets 读取 / fclose 关闭
 * 说明：运行后会在当前目录生成一个 note.txt 演示文件
 * ============================================================ */

#include <stdio.h>                 // 文件操作函数都声明在这里

int main(void)
{
    // 1. 打开文件准备写入，"w" 表示写入模式（文件不存在会自动创建）
    FILE *fp = fopen("note.txt", "w");
    if (fp == NULL) {              // 打开失败会返回 NULL
        printf("文件打开失败\n");  // 提示失败
        return 1;                  // 异常结束
    }

    // 2. 向文件写入一行文字
    fprintf(fp, "今天学了 C 语言文件操作\n");

    // 3. 关闭文件：数据才会真正写入磁盘
    fclose(fp);

    // 4. 重新以读取模式打开，"r" 表示读取
    fp = fopen("note.txt", "r");
    if (fp == NULL) {              // 同样要判断失败
        printf("文件打开失败\n");
        return 1;
    }

    // 5. 用 fgets 一行一行读，读到末尾会返回 NULL
    char line[100];                // 存每一行的字符数组
    while (fgets(line, sizeof(line), fp) != NULL) {  // 读不到内容就退出
        printf("读到：%s", line);  // 打印读到的这一行
    }

    // 6. 用完关闭
    fclose(fp);

    return 0;                      // 程序正常结束
}                                  // main 函数结束
