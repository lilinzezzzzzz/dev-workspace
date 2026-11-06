# Finder Menu（macOS）

[Finder Menu](https://github.com/nikgrbn/finder-menu) 为 macOS Finder 添加新建文件、在当前目录打开终端、复制路径等右键菜单操作。

## 安装与启用

在已安装 Homebrew 的 macOS 本机终端执行：

```bash
brew install nikgrbn/tap/finder-menu
finder-menu enable
```

启用后，Finder 会自动加载扩展，无需手动启动应用。

## 使用

在 Finder 文件夹的空白处右键，可以新建文件、打开终端、使用编辑器打开当前文件夹、复制路径或前往上级文件夹。

打开设置，选择显示的菜单项和默认终端：

```bash
finder-menu settings
```

也可以直接将终端设为 Ghostty：

```bash
finder-menu terminal Ghostty
```

首次使用“前往上级文件夹”时，按系统提示允许 Finder Menu 控制 Finder。

## 更新与卸载

通过 Homebrew 更新后，重新启用扩展：

```bash
brew update && brew upgrade finder-menu
finder-menu enable
```

卸载前先禁用扩展：

```bash
finder-menu disable
brew uninstall finder-menu
```

## 菜单未出现

- 按住 Option（⌥）键，右键点击 Dock 中的 Finder，选择“重新开启”；同时检查系统设置中的 Finder 扩展是否已启用 Finder Menu。
- OneDrive、Dropbox、Google Drive 和 iCloud Drive 等使用 Apple File Provider 的同步目录受 macOS 限制，可能不显示扩展菜单；可先在普通本地文件夹中验证。
