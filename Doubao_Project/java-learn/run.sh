#!/bin/bash
# ============================================================
# 一键运行脚本：运行指定的示例类
# 用法：./run.sh <包名>.<类名>
# 示例：./run.sh basics.HelloWorld
#       ./run.sh oop.InheritanceDemo
# ============================================================

# 进入脚本所在目录
cd "$(dirname "$0")"

# 如果没有传参，打印使用帮助并退出
if [ $# -lt 1 ]; then
    echo "用法: ./run.sh <包名>.<类名>"
    echo "例如: ./run.sh basics.HelloWorld"
    exit 1
fi

# 先确保编译过；若 out 目录不存在则自动编译一次
if [ ! -d out ]; then
    echo "未找到 out 目录，先自动编译..."
    ./compile.sh
fi

# -cp out 指定类路径，-Dfile.encoding=UTF-8 保证中文输出不乱码
java -cp out -Dfile.encoding=UTF-8 "$1"
