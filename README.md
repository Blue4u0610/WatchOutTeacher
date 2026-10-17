<p align="center">
  <img src="extension/icons/icon-128.png" width="88" alt="WatchOutTeacher">
</p>

<h1 align="center">WatchOutTeacher</h1>
<p align="center">少切一个窗口，多看一眼出处。</p>
<p align="center"><strong>中文</strong> · <a href="README.en.md">English</a></p>

按住 **Option ⌥** 划选网页上的问题，答案就出现在旁边。需要解释和出处时，点右下角的 **⌄**；需要复制时，直接选中文字。

WatchOutTeacher 是一个运行在 **macOS + Chrome / Edge / Chromium** 上的课程辅助扩展，通过本机 **Codex CLI** 或 **Claude Code** 回答问题。可以导入自己的课件，让回答参考当前课程资料。它不会替你点击选项或提交作业——鼠标的最后一票，还是你的。

[安装](#安装从零开始) · [使用](#日常使用) · [资料与隐私](#资料怎么用数据去哪儿) · [排障](#遇到问题) · [开发](#开发与测试)

## 能做什么

- **原地问答**：划选后显示答案，滚动页面也会保留；解释单独展开，文字可以复制。
- **按课程查资料**：导入 PDF、PPTX、TXT、Markdown；引用标明文件及页码、幻灯片或文本片段。
- **自己选模型和强度**：Codex 模型列表由本机 CLI 提供，支持自动或手动推理强度。
- **可选备用服务**：首选服务失败后可尝试另一个，也可以关闭这个开关。
- **按需授权网站**：从一个课程网站开始，或自行开启所有 HTTP / HTTPS 网站。

<details>
<summary>看一眼界面</summary>

![展开的答案、解释与来源](docs/evidence/mock-source.png)

这是仓库自带的演示题，答案来自测试替身，用于展示界面。真实 Codex 调用记录与覆盖范围见 [测试说明](docs/TESTING.md)。

</details>

## 安装：从零开始

准备一台 Mac、Chrome 或 Edge，以及可登录的 AI 服务账户。下面的命令在 macOS「终端」中运行；按 `⌘ Space` 搜索“终端”即可打开。

> 这是本机扩展，不是要部署到服务器的网站。GitHub 存放代码；回答由你电脑上的 CLI 发起。Safari 暂不支持，浏览器界面目前为中文。

### 1. 安装并登录 AI 客户端

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

### 2. 准备浏览器和 Python

安装 [Chrome](https://www.google.com/chrome/) 或 [Edge](https://www.microsoft.com/edge)，然后检查 Python：

```sh
python3 --version
```

需要 **Python 3.9+**，且自带 SQLite FTS5。没有 Python 时可用 [python.org 的 macOS 安装包](https://www.python.org/downloads/macos/)，或通过已安装的 [Homebrew](https://brew.sh/) 执行 `brew install python`。

日常使用不需要 Node.js 或 Xcode；第一次安装依赖需要联网。

### 3. 下载项目

在本页点击 **Code → Download ZIP**，解压到准备长期保留的位置。终端输入 `cd `（末尾留一个空格），把解压后的项目文件夹拖进终端，再按回车。

熟悉 Git 的话，也可以：

```sh
mkdir -p ~/Projects
cd ~/Projects
git clone https://github.com/Blue4u0610/WatchOutTeacher.git
cd WatchOutTeacher
```

下面所有项目命令，都在包含 `README.md`、`bridge`、`extension` 的这个目录里执行。

### 4. 安装本地桥接

```sh
python3 scripts/install.py
```

看到扩展 ID 和“加载扩展目录”后，桥接安装完成。安装器会创建独立 Python 环境，为当前用户注册 Chrome / Edge / Chromium 的本地通信入口，不需要 `sudo`。

浏览器会按需启动桥接。无需另开一个终端“挂着服务”，也不要直接运行 `bridge/host.py`。

### 5. 加载扩展

1. Chrome 打开 `chrome://extensions`；Edge 打开 `edge://extensions`。
2. 开启右上角的 **开发者模式**。
3. 点击 **加载已解压的扩展程序**。
4. 选择项目里的 **`extension` 子文件夹**。
5. 将 WatchOutTeacher 固定到工具栏，点击图标打开设置。

**选 `extension`，不要选项目根目录。** 如果看到 `Manifest file is missing or unreadable`，通常就是选错了这一层。

### 6. 授权网站、选择服务

1. 设置页应显示“本地桥接已连接”。
2. 输入课程网站，例如 `https://school.instructure.com`，点击授权并接受浏览器提示。也可选择“授权所有网站”。
3. 点击 **检测 CLI**，确认准备使用的工具已安装并登录。
4. 选择首选服务、模型和 Codex 推理强度，点击 **保存设置**。只有一个 CLI 时，可以关闭备用服务。
5. 刷新要使用的网页。Chrome 内部页、扩展商店等受保护页面不支持。

安装检测不会生成答案，也不代表账户一定还有额度。下一步用一个小问题检查实际调用。

### 7. 试一道题，再导入课件

在获授权的网页上，按住 **⌥**，从文字处按下鼠标左键并拖选题干和选项。松开后，等待答案出现。

想先用固定示例？在项目目录运行：

```sh
python3 -m http.server 8765 --bind 127.0.0.1 --directory tests
```

授权 `http://localhost:8765`，打开 [本地演示页](http://localhost:8765/fixture.html)，划选第一道 `2 + 2`。**这会实际调用你的 CLI，使用对应账户的额度。** 测完按 `Ctrl+C` 关闭演示服务器；日常使用不需要它。

然后在设置页创建课程，选择 PDF、PPTX、TXT 或 MD 文件，等到显示“已导入”。可以先导入仓库里的 `tests/material.md`，再划选演示页第二题；资料把虚构 Lumen 协议的就绪颜色定义为 Violet，引用应指向这份文件。

## 日常使用

| 想做什么 | 怎么操作 |
| --- | --- |
| 提问 | 按住 ⌥，左键拖选文字；普通划词不会提问 |
| 看解释、出处 | 点击答案框右下角 ⌄；再点一次收起 |
| 复制答案 | 直接选中文字，按 ⌘C；展开后也有“复制”按钮 |
| 滚动、缩放 | 答案保留，并重新定位到可见区域 |
| 关闭答案 | 左键点击浮层外，并取消或替换原选区 |
| 换一道题 | 再次 ⌥ 拖选；旧请求会取消 |
| 快捷键冲突 | 设置中改为 Option + Shift |
| 换课程 | 在设置页切换；新问题使用新课程的资料 |

右键、中键和 Esc 不关闭浮层。页面跳转、刷新、原文字节点被移除或课程变更，会清理旧答案。

### 模型与推理强度

模型和强度在 **本插件设置** 中选择，保存后对下一题生效。更改某个 Codex 聊天窗口的模型不会影响插件。

- **自动**：不指定强度，交给 CLI / 服务默认处理。
- **手动**：显示所选模型支持的普通档位，例如 Low、Medium、High、XHigh、Max，并明确传给 CLI。
- **自定义模型**：可以填完整模型 ID；实际支持情况由 CLI 校验。

更高强度通常更慢、消耗更多，也不保证每题更准。Ultra 涉及自动任务分派，本插件暂不提供。Claude 使用其自身默认强度。模型列表会变化，点击“刷新模型列表”即可更新，不需要照抄 README 里的旧名单。

## 资料怎么用，数据去哪儿

```text
网页选区 + 当前题目
        ↓
本机课程索引 → 取出相关片段
        ↓
Codex CLI / Claude Code → 对应 AI 服务
        ↓
答案 + 解释 + 来源 → 网页浮层
```

导入时，文件解析成文本并存入本机 SQLite。每道题最多检索 **12 个片段**发送给模型；不会每题重新打开所有原文件，也不是把整门课训练进模型。每题是独立会话。

| 文件 | 能读取的内容 | 需要注意 |
| --- | --- | --- |
| PDF | 可提取文本、文件页码 | 扫描件先做 OCR；加密 PDF 不支持 |
| PPTX | 文字框、组合文字、表格 | 不读取图片、图表含义和演讲者备注 |
| TXT / Markdown | UTF-8 文本 | 来源是文本片段编号，不是行号 |

单个文件上限 **30 MB**。旧 `.ppt`、Word、图片和自动截图目前不支持。关键词检索对同义词、中文分词和跨语言问题有限；没有命中时会提示回退到开头片段。引用说明“提供过哪份材料”，不等于推论一定正确。

课程索引保存在 `~/Library/Application Support/CourseAssist/courses.sqlite3`。目录沿用旧名称以兼容已有安装。选区、题目上下文和检索片段会经 CLI 发往所选 AI 服务，因此**不是离线问答**。删除资料会删除本地索引，不会删除原文件。

默认不保存题目和答案正文日志。诊断只记录服务、请求的模型与强度、错误类别、用时及检索数量。模型权限、订阅额度和服务费用以 CLI 所登录账户为准。

## 更新与卸载

**Git 安装：**先关闭题目页和设置页，在扩展管理页禁用 WatchOutTeacher，然后在项目目录运行：

```sh
git pull --ff-only
python3 scripts/install.py
```

重新启用扩展，点击 **重新加载**，再刷新题目页。ZIP 安装则下载新版并替换源码；若移动了文件夹，需要重新加载新的 `extension` 路径。不要删除已经加载的源码文件夹。

**卸载：**

```sh
python3 scripts/install.py --uninstall
```

再从浏览器移除扩展。课程资料默认保留；如需一并移除，退出浏览器后在 Finder 中前往 `~/Library/Application Support/CourseAssist`，将这个文件夹移到废纸篓。

## 遇到问题

| 现象 | 先检查这里 |
| --- | --- |
| 找不到 manifest | 加载的是项目里的 `extension` 文件夹吗？ |
| 找不到本地宿主 / 宿主退出 | 重新运行安装器，再重新加载扩展；不要将运行副本改回 Documents 中的虚拟环境 |
| 桥接连接断开 | 设置页点“重连 / 刷新资料”，刷新题目页再划选 |
| 划词没反应 | 网站授权、页面刷新、鼠标按下前按住 ⌥；输入框内不触发，选区最多 8,000 字符 |
| Canvas 内层题目没反应 | 题目可能来自另一个 iframe 域名；授权该域名，或自行选择所有网站授权 |
| 认证或额度错误 | 终端运行 `codex login status`，或打开 `claude` 检查登录及账户提示 |
| CLI 参数不兼容 | 更新 CLI 后重新检测；[已验证环境](docs/TESTING.md) 列出版本 |
| 回答缺少选项或公式 | 补选完整题目；图片与不可提取公式目前不会传给模型 |
| 资料没有被引用 | 检查导入警告、当前课程和本题检索数量；资料不足时可能使用通用知识 |
| 想在 Safari 用 | 目前没有 Safari 安装包；见 [移植说明](docs/SAFARI.md) |

## 开发与测试

运行需要 Python；浏览器测试另外需要 **Node.js 22+**。测试使用临时浏览器配置和测试课程，不读取日常浏览器账户。

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
npm ci
npx playwright install chromium
npm test
npm run test:browser
```

真实模型测试需先登录 Codex，并会使用账户额度：

```sh
npm run test:live
```

[架构](docs/ARCHITECTURE.md) · [测试说明](docs/TESTING.md) · [版本记录](CHANGELOG.md) · [贡献指南](CONTRIBUTING.md)

本项目用于课程阅读与复习，请遵守课程对 AI 的使用要求。它与 OpenAI、Anthropic、Canvas 没有隶属关系。
