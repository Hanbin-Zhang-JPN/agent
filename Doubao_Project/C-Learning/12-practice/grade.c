/* ============================================================
 * 文件：12-practice/grade.c
 * 主题：综合练习二：学生成绩统计
 * 用到：结构体 / 数组 / 函数 / for 循环
 * 功能：输出成绩单，计算平均分，找出最高分
 * ============================================================ */

#include <stdio.h>                 // 引入标准输入输出库

// 定义学生结构体
struct Student {                   // 学生类型
    char name[20];                 // 姓名
    int score;                     // 成绩
};                                 // 结构体定义结束

// 计算平均分：接收结构体数组和人数，返回平均分
float average(struct Student stu[], int n)   // 数组作参数会退化为指针
{
    int sum = 0;                   // 总分累加器
    for (int i = 0; i < n; i++) {  // 遍历每个学生
        sum += stu[i].score;       // 累加成绩
    }
    return (float)sum / n;         // 先转成 float 再除，避免整数除法丢小数
}                                  // average 函数结束

int main(void)
{
    // 1. 准备 4 个学生的数据
    struct Student stu[4] = {      // 结构体数组
        {"小明", 92},              // 第 0 个
        {"小红", 85},              // 第 1 个
        {"小刚", 78},              // 第 2 个
        {"小丽", 95}               // 第 3 个
    };

    int n = 4;                     // 学生人数

    // 2. 输出成绩单
    printf("学生成绩单：\n");
    for (int i = 0; i < n; i++) {  // 遍历打印每个学生
        printf("%s：%d 分\n", stu[i].name, stu[i].score);
    }

    // 3. 调用函数计算平均分
    float avg = average(stu, n);   // 传数组名和人数
    printf("平均分：%.1f\n", avg); // 输出 87.5

    // 4. 遍历找最高分：先假设第一个最高
    int max = stu[0].score;        // 用第一个成绩作基准
    for (int i = 1; i < n; i++) {  // 从第二个开始比较
        if (stu[i].score > max) {  // 发现更高的
            max = stu[i].score;    // 更新最高分
        }
    }
    printf("最高分：%d\n", max);   // 输出 95

    return 0;                      // 程序正常结束
}                                  // main 函数结束
