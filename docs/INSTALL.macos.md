# macOS 安装

[返回首页](../README.md) · [Windows 安装](INSTALL.windows.md) · [English](INSTALL.macos.en.md)

准备 Chrome / Edge、Python 3.9+ 和可用的 AI 账户。按 `⌘ Space` 搜索“终端”，下面的命令都在那里运行。

## 1. 安装并登录 AI 客户端

选一条路线即可，不必两个都装。

**路线 A：ChatGPT 账户 + Codex CLI（已完成真实调用验证）**

如果平时使用 ChatGPT，继续用自己的账户即可。这里需要的是 **Codex 命令行工具**，仅安装 ChatGPT 桌面应用不会自动完成这一步。

按 [Codex 官方安装说明](https://learn.chatgpt.com/docs/codex/cli) 安装：

```sh
curl -fsSL https://chatgpt.com/codex/install.sh | sh
```

重新打开终端，然后登录：

```sh
codex --version
codex login
codex login status
```

按提示选择 ChatGPT 登录并完成浏览器验证。最后一条命令应显示已登录。是否有模型调用权限、额度多少，以你的账户为准。

**路线 B：Claude Code（可选，适配器尚未完成真实账户验证）**

按 [Claude Code 官方安装说明](https://code.claude.com/docs/en/setup) 安装：

```sh
curl -fsSL https://claude.ai/install.sh | bash
```

重新打开终端，运行：

```sh
claude --version
claude
```

跟随首次启动的登录流程。Claude 桌面应用与这里的 `claude` 命令不是一回事。插件会检查 CLI 所需参数；不兼容的版本会提示更新，不会偷偷换一套调用方式。

两条路线都使用 CLI 自己的登录状态。插件不需要你填写 API Key，也不会接管桌面聊天框。如果只安装了 Claude，稍后记得在设置中把首选服务改为 Claude Code。

## 2. 准备浏览器和 Python

安装 [Chrome](https://www.google.com/chrome/) 或 [Edge](https://www.microsoft.com/edge)，然后检查 Python：

```sh
python3 --version
```

需要 **Python 3.9+**，且自带 SQLite FTS5。没有 Python 时可用 [python.org 的 macOS 安装包](https://www.python.org/downloads/macos/)，或通过已安装的 [Homebrew](https://brew.sh/) 执行 `brew install python`。

日常使用不需要 Node.js 或 Xcode；第一次安装依赖需要联网。

## 3. 下载项目

在 [最新版本](https://github.com/Blue4u0610/WatchOutTeacher/releases/latest) 页面的 **Assets** 下载 `WatchOutTeacher-v版本号.zip`，解压到准备长期保留的位置。终端输入 `cd `（末尾留一个空格），把解压后的项目文件夹拖进终端，再按回车。

熟悉 Git 的话，也可以：

```sh
mkdir -p ~/Projects
cd ~/Projects
git clone https://github.com/Blue4u0610/WatchOutTeacher.git
cd WatchOutTeacher
```

下面所有项目命令，都在包含 `README.md`、`bridge`、`extension` 的这个目录里执行。

## 4. 安装本地桥接

```sh
python3 scripts/install.py
```

看到扩展 ID 和 “Load unpacked extension” 路径后，桥接安装完成。安装器会创建独立 Python 环境，为当前用户注册 Chrome / Edge / Chromium 的本地通信入口，不需要 `sudo`。

浏览器会按需启动桥接。无需另开一个终端“挂着服务”，也不要直接运行 `bridge/host.py`。

完成后，继续[第 5 步：加载扩展](../README.md#5-加载扩展)。macOS 默认按住 **Option ⌥** 划选提问。
