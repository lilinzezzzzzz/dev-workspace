# Linux 服务器常见目录速查

Linux 目录用途通常参考 [FHS 文件系统层级标准](https://specifications.freedesktop.org/fhs/latest-single/)。不同发行版和团队的具体布局可能有所区别。

| 目录 | 主要用途 | 常见内容 |
|---|---|---|
| `/` | 文件系统的根目录 | 其他目录的起点 |
| `/bin` | 常用基础命令 | `ls`、`cp` 等 |
| `/sbin` | 系统管理相关命令 | 磁盘和系统维护工具 |
| `/lib` | 基础共享库和内核模块 | 程序运行所需的库 |
| `/boot` | 系统启动所需文件 | 内核、引导程序文件 |
| `/usr` | 系统程序、库和共享资源 | `/usr/bin`、`/usr/lib`、`/usr/share` |
| `/opt` | 独立安装的附加应用 | `/opt/myapp/` 中的程序和依赖 |
| `/etc` | 主机和服务配置 | `/etc/myapp/`、系统配置文件 |
| `/home` | 普通用户的主目录 | `/home/alice/` |
| `/root` | root 用户的默认主目录 | root 用户的配置和个人文件 |
| `/srv` | 本机服务提供的站点数据和内容 | `/srv/www/`、`/srv/files/` |
| `/var` | 运行过程中会变化的数据 | 状态、日志、缓存、队列 |
| `/var/lib` | 需要保存的应用内部状态和数据 | 数据库文件、应用状态 |
| `/var/log` | 文件形式的系统和服务日志 | `/var/log/myapp/` |
| `/run` | 当前开机周期内的运行数据 | PID、Unix socket、运行时 unit |
| `/tmp` | 临时文件 | 临时下载、程序中间文件 |
| `/dev` | 设备文件和特殊文件 | `/dev/sda`、`/dev/null` |
| `/proc` | 内核和进程的运行时信息 | `/proc/cpuinfo`、`/proc/<PID>/` |
| `/sys` | 内核暴露的设备、驱动和其他对象信息 | `/sys/devices/`、`/sys/class/` |
| `/mnt` | 临时挂载文件系统 | 管理员手动挂载的磁盘 |
| `/media` | 可移动介质的常见挂载位置 | U 盘、光盘 |

`/` 是整个文件系统的根目录；`/root` 是 root 用户的主目录。普通用户的主目录通常位于 `/home`，但也可以配置在其他位置。

一些现代发行版将 `/bin`、`/sbin` 或 `/lib` 作为指向 `/usr` 下相应目录的链接。`/usr/local` 通常用于管理员在本机安装的软件。

## 部署时如何选择

以名为 `myapp` 的服务为例，一种常见布局是：

| 内容 | 可选位置 |
|---|---|
| 程序、虚拟环境、构建产物 | `/opt/myapp/` |
| 服务配置 | `/etc/myapp/` |
| 持久状态 | `/var/lib/myapp/` |
| 日志文件 | `/var/log/myapp/` |
| 单独管理的网站内容 | `/srv/www/myapp/` |

`/opt` 侧重附加应用；`/srv` 侧重本机服务提供的内容，既可以服务内网，也可以服务公网。团队也可以约定将整个应用放在 `/srv/myapp/`，或使用 `/data/apps/`。

严格按 FHS 为 `/opt/<软件包>` 布局时，其主机配置和可变数据分别对应 `/etc/opt/<软件包>` 和 `/var/opt/<软件包>`；自建项目采用上表的路径也很常见。

## 持久性与运行时数据

- **目录名不保证数据持久化。** `/opt`、`/var/lib` 或自定义 `/data` 能否保留，取决于实际挂载、磁盘和容器生命周期。
- `/run` 是本次开机的运行数据，重启后会被清除或重新生成。`/tmp` 中的文件也可能在重启或定期清理时删除；`/var/tmp` 通常跨重启保留，但仍可能被定期清理。
- `/proc` 和 `/sys` 是内核提供的虚拟文件系统。部分条目可写，修改可能直接影响运行中的内核或设备，应先了解其作用。 [Linux 内核文档：proc](https://docs.kernel.org/filesystems/proc.html)；[sysfs](https://docs.kernel.org/filesystems/sysfs.html)
- 如果使用 systemd，管理员维护的持久服务 unit 通常放在 `/etc/systemd/system/`；是否开机启动还取决于启用配置或其他 unit 的触发。日志可以交给 journald，但是否跨重启保留取决于其存储配置。 [systemd unit 文档](https://www.freedesktop.org/software/systemd/man/latest/systemd.unit.html)；[journald 文档](https://www.freedesktop.org/software/systemd/man/latest/systemd-journald.service.html)
