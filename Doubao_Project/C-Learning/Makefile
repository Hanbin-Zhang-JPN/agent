# ============================================================
# C-Learning 项目一键编译脚本
# 用法：
#   make                              编译全部章节，输出到 build/ 目录
#   make build/01-hello/hello         只编译指定的某一个文件
#   make clean                        删除所有编译产物
# ============================================================

CC      = gcc                      # 编译器（macOS 的 gcc 指向 clang，同样可用）
CFLAGS  = -Wall -Wextra -std=c11   # 开启警告，使用 C11 标准
SRCS    = $(shell find . -name "*.c")               # 自动收集所有 .c 源文件
BINS    = $(patsubst ./%.c,build/%,$(SRCS))         # 把源文件路径换算成输出路径

# 默认目标：编译全部
all: $(BINS)

# 模式规则：build/xxx 依赖同路径下的 xxx.c
build/%: %.c
	@mkdir -p $(dir $@)            # 先创建输出目录（@ 表示不回显命令）
	$(CC) $(CFLAGS) $< -o $@       # 编译：$< 是源文件，$@ 是目标文件

# 清理目标：删除整个 build 目录
clean:
	rm -rf build

.PHONY: all clean                 # 声明伪目标，避免与同名文件冲突
