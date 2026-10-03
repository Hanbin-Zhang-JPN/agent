# 磁盘观察

一款本机运行的 Mac 磁盘监控小程序。窗口显示物理磁盘实时读写速度、最近两分钟活动、本次开机和本程序打开以来的读写量；菜单栏显示简要状态。

## 打开

双击 [`build/DiskWatch.app`](build/DiskWatch.app)，或在终端运行：

```sh
open build/DiskWatch.app
```

修改源码后运行 `./build-app.sh` 重新构建。需要 macOS 14 或更高版本的 Apple Silicon Mac，以及 Apple Command Line Tools。本项目没有网络请求，也不保存磁盘序列号。

## 数值含义

- **本次开机读写**来自 IOKit 物理磁盘驱动计数器，重启或驱动重置后会归零。
- **监控期间读写**是本程序运行时累积的计数器增量，退出后不保留。
- **终身读写和已用寿命**来自 NVMe SMART，需要安装 `smartmontools`（`brew install smartmontools`），并且设备及 macOS 允许读取。未提供时显示“不可用”。Apple 内置 SSD 在部分 Mac 或系统版本上可能拒绝 SMART 访问；程序不会推算一个假的磨损百分比。
- SMART 终身读写是主机数据量；已用寿命是 SSD 固件估计值，两者不能直接换算为 NAND 擦写量。

该版本适用于 NVMe SMART；其他磁盘仍可查看实时和开机以来的 IOKit 读写统计。
