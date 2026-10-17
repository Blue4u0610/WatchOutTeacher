# 架构与权限边界

## 数据路径

```text
已授权网页 / 独立 frame
  content.js：可信 pointerdown 的 Option 状态 + 有效文本选区
      ↓ 扩展内部 Port（不监听 window.postMessage）
  background.js：校验 sender、域名权限、操作白名单、长度
      ↓ chrome.runtime.connectNative
  host.py：4-byte native-endian 长度 + UTF-8 JSON，验证扩展 origin
      ↓
  Store：当前课程、FTS5 最多 12 个片段
      ↓ 每题独立 prompt / 临时目录
  CodexAdapter 或 ClaudeAdapter（串行主备）
      ↓ 严格 schema + 引用白名单
  source_id → 本地 document_id / 名称 / 文件页或幻灯片编号
      ↓ 当前 request ID 才允许显示
  closed Shadow DOM 浮层（所有模型/文件名内容用 textContent）
```

生产不监听 TCP 端口。扩展不请求 history、cookies、debugger、clipboardRead 或默认全站访问。`optional_host_permissions` 仅定义可申请范围；网站授权必须由设置页的用户手势发起，按主机申请 HTTP/HTTPS，或通过「授权所有网站」显式申请全部 HTTP/HTTPS 主机。没有向页面暴露可调用 CLI 的 API。

Native Messaging 清单固定扩展 ID，宿主还校验启动参数中的 origin。这个边界防止普通网页或其他扩展直接访问；它不用于防范本机同一用户启动任意程序的攻击者。安装器不读取或复制任何登录凭据。

## 文件与存储

安装副本、虚拟环境、SQLite 位于当前用户 Application Support。目录默认 0700，数据库及注册清单 0600，宿主 umask 077。源码独立保留。浏览器不直接读取任意本地路径；用户文件选择器读到的内容以 192 KiB 分块传给宿主，后者只接受已分配上传 token、严格偏移与预期总大小。

临时上传文件以随机 ID 命名，不使用用户文件名构造路径。PDF/PPTX 解析在单独进程中执行，45 秒墙钟、35 秒 CPU、1 GiB RSS 检测上限（macOS 定期检查）与输出大小限制。RSS 检测不是精确的瞬时硬内存沙箱；CPU/文件大小/解压体积限制共同缩小风险。PPTX 解压总大小限制 150 MiB。正常请求结束会删除临时原文件，仅保存可提取的正文和索引。强制 SIGKILL 或整机崩溃不保证清理系统临时目录。

每门课的文档与 chunks 通过外键隔离。删除文档/课程触发 FTS5 删除；SQLite WAL 支持同时读取。课程变更取消活动请求。每次生成都重新读取当前课程资料；不依赖模型会话状态。

FTS5 是关键词检索，没有云向量数据库。最多使用前 48 个不同查询词、12 个片段，所有上限均在诊断中暴露。模型仍收到完整允许范围内的选区与题目上下文；未命中时显示回退到开头片段的限制。无 OCR、跨语言语义索引或“全文已完全读过”的保证。

## Provider 契约

`CLIProvider.detect()`：固定受信任搜索路径查找程序，检查本地 help、版本、安全所需 flags；Codex 另检查 feature 列表和 login status。缓存 60 秒，设置页可强制检测。不把“已安装”误报为 Claude 已登录。

`answer(prompt, model, cancel, timeout, effort="")`：数组 argv + `shell=False`、stdin 输入、独立临时 cwd、最小环境变量集合。不会接收网页提供的 executable、工作路径、工具参数、API Key 或环境变量。模型设置限于名称格式。

Codex 的限制选项经过本机 0.153.4 真实调用。Claude 的参数来自官方文档并在实际安装后检查 help；没有安装因此不能声称已验证其工具隔离与认证流程。两个适配器复用各自 CLI 的账户存储，不复制、不伪造认证。组织级受管理配置可能仍适用。

调用的 stdout/stderr 放在临时文件，不写入 Native Messaging stdout。Codex 只读取 final message 文件；Claude 只接受 JSON `result` envelope 的 `structured_output`（或严格 JSON 的 result）。进度、工具事件、错误诊断不会被拼进答案。输出的字段、长度、枚举、布尔值和每个 source_id 都校验；引用标题/页码只能从当前发送片段的本地映射得到。

引用校验验证的是“确实存在且确实发送过的来源”，不是自然语言推论的语义正确性。答案仍需要使用者核对。模型正常返回 insufficient 会直接显示，不作为后端故障。

总预算采用 monotonic deadline；主用至多使用剩余时间 65%，备用使用剩余预算。全部失败保留每个 Provider 的错误类别。格式失败零额外修复调用，至多一次备用；不无限重试。主动取消不会备用。取消/超时先 SIGTERM，随后对整个独立子进程组 SIGKILL 并 wait；取消事件也参与能力检测和锁等待。宿主正常 EOF/SIGTERM 会取消活动请求并等待清理。

## UI 生命周期

pointerdown 记录左键与修饰键，pointerup 检查拖动距离和非空选区。只接受真实用户事件；输入框、可编辑区域、浮层内部忽略。最大选区 8,000 字符，题目容器 16,000 字符；过大的容器退回完整选区并提示。

优先识别 `.question`、常见 question data attribute、fieldset；保留段落/代码/表格文本分隔，移除表单值、脚本与明显隐藏内容。识别容器不等于保证新 Canvas 版本的全部选项都已渲染；无法识别或存在图片/公式时明确提示。脚本只读题目 DOM，写入仅限自己的自定义浮层元素。

浮层使用 closed Shadow DOM 隔离子树样式，宿主关键布局为 inline important，内部只使用安全文本节点。默认色彩跟随系统，允许手动选择明暗。无法抵御宿主页面主动移除浮层或所有浏览器扩展的干扰，因此不是对任意网站绝对隔离。

坐标来自 Range，按 visualViewport 约束；优先下方/上方，再尝试侧面或题目容器外侧，尽量避开当前选区和答案控件。空间过小的 iframe 会限制浮层宽高，内部滚动；无法承诺在极小 frame 中完全不遮挡。每个获授权 frame 独立注入、独立取选区、独立显示，不越过跨域 DOM 边界。

背景为各 frame 保存当前请求，切题取消旧请求；content script 同时按 request ID、URL 和 Range 节点有效性丢弃迟到结果。滚动/缩放通过 requestAnimationFrame 合并定位更新，保留浮层。用户左键从浮层外点击或拖选后，若原选区已取消或被替换才关闭；右键、中键、Esc 和单独 selectionchange 不关闭。答案为可选中文本，独立右下角箭头负责展开收起。pagehide、路由轮询、原节点被移除、课程变化清理过期浮层。当前版本不同标签/frame 可以独立显示结果，宿主限制活动请求数量以避免误触发风暴。

## 已知技术边界

- 不支持 Safari 的原生消息宿主、Firefox、全系统划词、截图或 OCR。
- `about:blank` / `srcdoc` / sandbox opaque-origin iframe 未自动申请权限或注入；需单独设计与验证。
- New Quizzes 真实域名、DOM 及学校定制未知；只能声称模拟 DOM 与获授权跨域 frame 通过。
- 扫描 PDF、复杂公式、CSS 生成的选项标签、Canvas 绘图和虚拟化未渲染内容不能可靠提取。
- CSS 125% 缩放已自动验证；真实浏览器菜单缩放、系统显示缩放、复杂页面主题及其他扩展共存仍需手工验收。
- 没有语义准确率估计、免费调用承诺、自动答题或提交功能。

Codex 的 `codex_effort` 设置默认空字符串（自动），持久化在 SQLite。非空值经过枚举校验后作为 TOML 配置参数 `model_reasoning_effort` 传递；不改动全局配置。目录返回支持档位与默认档位，前端联动模型选择并阻止保存已知不支持的组合。目录失败时保留用户选择。备用 Claude 不继承 Codex 强度。诊断只记录请求值，不将其描述为服务端确认值。
