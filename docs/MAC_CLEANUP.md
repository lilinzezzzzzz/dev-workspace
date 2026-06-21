# macOS 电脑垃圾清理指南

## 目标

用于日常清理 macOS 上的临时文件、缓存、安装包、卸载残留和开发构建产物。当前策略以可回滚、可预览、低风险为优先，不做激进系统优化。

## 推荐工具

使用 Mole 作为主要清理工具：

```bash
brew install mole
```

Mole 适合处理：

- 应用缓存、系统日志、浏览器缓存
- 已卸载应用的残留文件
- `.dmg`、`.pkg`、`.zip` 等安装包
- 开发项目中的 `node_modules`、构建目录、虚拟环境等大体积产物
- 磁盘占用分析

## 推荐流程

### 1. 先清理 Downloads

Downloads 里的文件优先通过 Finder 移到废纸篓，不建议直接永久删除。

确认一天内没有误删后，再清空废纸篓。

### 2. 预览 Mole 清理项

先 dry-run，确认它准备删除什么：

```bash
mo clean --dry-run --debug
```

重点检查是否包含不希望删除的数据目录或应用数据。

### 3. 清理缓存和残留

确认 dry-run 输出合理后再执行：

```bash
mo clean
```

### 4. 清理安装包

查找并删除安装包：

```bash
mo installer
```

### 5. 分析大目录

查看 `~/Library` 的磁盘占用：

```bash
mo analyze ~/Library
```

如果需要继续定位，也可以分析具体目录：

```bash
mo analyze ~/Library/Application\ Support
mo analyze ~/Library/Caches
```

### 6. 预览开发产物清理

开发目录清理风险更高，必须先预览：

```bash
mo purge --dry-run
```

确认清单后，再按交互提示选择要删除的项目。

## 暂不建议直接执行

以下命令不要作为第一次清理的默认动作：

```bash
mo optimize
mo uninstall
mo purge
mo touchid
```

原因：

- `mo optimize` 会调整系统缓存和服务状态，不是单纯清垃圾。
- `mo uninstall` 适合明确卸载应用时使用，不适合批量尝试。
- `mo purge` 会删除开发构建产物，必须先 dry-run。
- `mo touchid` 是 sudo 便利性配置，和垃圾清理无直接关系。

## 不要手动删除的目录

除非明确知道影响，否则不要手动删除：

- `~/Library/Application Support`
- `~/Library/Containers`
- `~/Library/Group Containers`
- `/Library`
- `/System`

这些目录可能包含应用数据、登录状态、许可证、配置、系统组件或沙盒数据。优先通过 Mole、应用自带卸载器或 Finder 废纸篓处理。

## 日常命令清单

```bash
# 查看磁盘占用
df -h /System/Volumes/Data

# 预览清理
mo clean --dry-run --debug

# 清理缓存和残留
mo clean

# 清理安装包
mo installer

# 分析 Library 占用
mo analyze ~/Library

# 预览开发产物清理
mo purge --dry-run

# 查看 Mole 操作历史
mo history
```

## 原则

1. 先分析，再删除。
2. 先移到废纸篓，再永久清空。
3. 先 dry-run，再真实执行。
4. 不手动删除不了解的 `~/Library` 子目录。
5. 磁盘空间充足时优先做温和清理，不做激进系统优化。
