# Python 项目 .gitignore 模板

将 [python.gitignore](python.gitignore) 用作新项目根目录的 `.gitignore`。已有项目可以对照合并，并保留现有项目专用规则。

模板覆盖 Python 构建产物、虚拟环境、测试与分析缓存、本机环境变量文件和 PyCharm 的个人工作区文件。`.vscode/` 整个目录用于保存本机工作区配置。PyCharm 的共享项目配置可以纳入版本控制，提交前检查其中是否含有个人路径或凭证。

`uv.lock`、`poetry.lock`、`.python-version` 和 `.env.example` 可纳入版本控制。数据库、运行数据和日志目录按项目实际位置加规则。已跟踪的文件需要单独处理，Git 会继续跟踪它们。

规则参考 [GitHub Python 模板](https://github.com/github/gitignore/blob/main/Python.gitignore)和 [PyCharm 项目配置共享说明](https://www.jetbrains.com/help/pycharm/sharing-project-settings.html)。
