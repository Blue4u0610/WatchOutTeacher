# Windows 安装

[返回首页](../README.md) · [macOS 安装](INSTALL.macos.md) · [English](INSTALL.windows.en.md)

以 **Windows 11 + Chrome / Edge + Python 3.12（64 位）** 为推荐组合。在开始菜单搜索 **PowerShell** 并打开，下面的命令都在那里运行。无需管理员权限，也不需要 WSL。

## 1. 安装并登录 AI 客户端

选择其中一个即可。这里需要 CLI（命令行工具）；仅安装 ChatGPT 或 Claude 桌面应用还不够。

### ChatGPT 账户 → Codex CLI

使用 [Codex 官方原生安装器](https://learn.chatgpt.com/docs/codex/cli)：

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://chatgpt.com/codex/install.ps1 | iex"
```

安装结束后，关闭并重新打开 PowerShell，再运行：

```powershell
codex --version
codex login
codex login status
```

按提示使用 ChatGPT 账户完成浏览器登录。最后一条命令应显示已登录，模型权限和额度取决于该账户。

### 或者：Claude Code

使用 [Claude Code 官方原生安装器](https://code.claude.com/docs/en/setup)：

```powershell
irm https://claude.ai/install.ps1 | iex
```

重新打开 PowerShell：

```powershell
claude --version
claude
```

完成首次登录。如果只安装 Claude Code，稍后在插件设置里把首选服务改为 Claude Code。该适配器已有参数与输出契约测试，真实 Claude 账户调用尚未验证。

**请使用 Windows 原生 `.exe` 安装。** 本插件不会转到 WSL，也不会通过 shell 执行 npm 的 `.cmd` / `.ps1` 包装器。已经用 npm 装过 CLI 的用户，可以再安装官方原生版；检测页会显示实际选中的路径。只安装在 WSL 的账户登录不会自动变成 Windows 登录。

安装或更新 CLI 后，彻底退出并重新打开 Chrome / Edge，让浏览器拿到新的程序路径。插件不要求填写 API Key，也不改变桌面聊天窗口的模型设置。

## 2. 安装浏览器和 Python

安装 [Chrome](https://www.google.com/chrome/) 或 [Edge](https://www.microsoft.com/edge)。

从 [python.org](https://www.python.org/downloads/windows/) 安装 **Python 3.12（64 位）**，保留 Python Launcher，并勾选 **Add python.exe to PATH**。重开 PowerShell 后检查：

```powershell
py -3.12 --version
```

如果没有 `py` 命令，但 `python --version` 显示的是刚安装的 Python，可以把本指南中的 `py -3.12` 换成 `python`。需要 Python 3.9+ 及 SQLite FTS5；推荐 3.12 以使用已有依赖的预编译包。日常使用无需 Node.js、Visual Studio 或编译工具。

## 3. 下载项目

在 [最新版本](https://github.com/Blue4u0610/WatchOutTeacher/releases/latest) 页面的 **Assets** 下载 `WatchOutTeacher-v版本号.zip`。右键压缩包，选择 **全部解压**，将项目放到准备长期保留的文件夹，例如 `C:\Users\你的用户名\Projects\WatchOutTeacher`。不要直接在压缩包预览里操作。

在解压后的项目文件夹中右键选择 **在终端中打开**，确认其中有 `README.md`、`scripts` 和 `extension`。也可以在 PowerShell 中输入：

```powershell
cd "C:\Users\你的用户名\Projects\WatchOutTeacher"
```

这条路径只是例子，请换成实际解压位置；路径带空格时保留引号。已经安装 Git 的话，也可以：

```powershell
git clone https://github.com/Blue4u0610/WatchOutTeacher.git
cd WatchOutTeacher
```

## 4. 安装本地桥接

在项目根目录运行：

```powershell
py -3.12 scripts/install.py
```

安装器会下载 Python 依赖，生成原生 `.exe` 启动入口，并在当前用户的注册表中注册 Chrome / Edge / Chromium。安装完成会显示扩展 ID 和 **Load unpacked extension** 路径。

程序和课程索引位于 `%LOCALAPPDATA%\WatchOutTeacher`，不需要手工修改注册表。浏览器会按需启动桥接，无需常驻终端，也不要直接运行 `bridge/host.py`。

继续[第 5 步：加载扩展](../README.md#5-加载扩展)。Windows 默认按住 **左 Alt** 划选；不使用右 Alt / AltGr 组合输入键。如果与网页快捷键冲突，在设置中选择 **Alt + Shift**。

更新和卸载见[首页说明](../README.md#更新与卸载)。Windows 自动测试覆盖注册、安装、重装、卸载、真实浏览器通信及模拟回答；真实 AI 登录和服务调用仍需在你自己的账户上完成最后一步试题。
