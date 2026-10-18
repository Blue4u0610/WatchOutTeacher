# 版本历史 · Version history

[最新版本 / Latest](https://github.com/Blue4u0610/WatchOutTeacher/releases/latest) · [全部发布 / All releases](https://github.com/Blue4u0610/WatchOutTeacher/releases) · [更新日志 / Changelog](../CHANGELOG.md)

| 版本 / Version | 代码日期 / Snapshot date¹ | 系统 / Platforms | 主要变化 / Highlights |
| --- | --- | --- | --- |
| [v0.3.0](https://github.com/Blue4u0610/WatchOutTeacher/releases/tag/v0.3.0) | 2026-10-18 | Windows / macOS | Gemini via Antigravity CLI, account models and selected backups / Gemini 账户模型与可选备用列表 |
| [v0.2.3](https://github.com/Blue4u0610/WatchOutTeacher/releases/tag/v0.2.3) | 2026-10-18 | Windows / macOS | 100 MB 文件、批量队列、正式发布 / Larger files, batch queue and formal releases |
| [v0.2.2](https://github.com/Blue4u0610/WatchOutTeacher/releases/tag/v0.2.2) | 2026-10-18 | Windows / macOS | 拖放导入、Claude CLI 检测 / Drag imports and Claude discovery |
| [v0.2.1](https://github.com/Blue4u0610/WatchOutTeacher/releases/tag/v0.2.1) | 2026-10-17 | Windows / macOS | 自定义回答要求 / Custom answer instructions |
| [v0.2.0](https://github.com/Blue4u0610/WatchOutTeacher/releases/tag/v0.2.0) | 2026-10-17 | Windows / macOS | Windows 原生适配 / Native Windows support |
| [v0.1.5](https://github.com/Blue4u0610/WatchOutTeacher/releases/tag/v0.1.5) | 2026-10-17 | macOS | 首个已提交快照系列；划词、课件、模型和强度选择 / Initial committed snapshot series |

¹ 日期按 America/New_York 记录代码快照。v0.1.5–v0.2.2 的 Release 后来补建，因此 GitHub 的发布时间与代码日期可能不同。0.1.0–0.1.4 只有早期开发日志，没有独立 Git 快照，不提供虚构的旧版下载。

Snapshot dates use America/New_York. Releases v0.1.5–v0.2.2 were backfilled later, so publication dates may differ. Versions 0.1.0–0.1.4 are early development notes only; no separate source snapshots exist.

## 下载与升级 / Download and update

每个正式版本的 **Assets** 提供 `WatchOutTeacher-vX.Y.Z.zip` 和 `SHA256SUMS.txt`。一个包包含扩展、本地桥接和安装脚本，适用于该版本声明支持的系统。Python 与 AI CLI 需要另行安装。这不是商店自动更新包。

Each release provides a source bundle and SHA-256 checksum under **Assets**. The bundle includes the extension, bridge and install scripts; Python and AI CLIs are separate prerequisites. This is not a browser-store auto-update package.

- 安装 / Install: [Windows](INSTALL.windows.md) · [macOS](INSTALL.macos.md) · [Windows (English)](INSTALL.windows.en.md) · [macOS (English)](INSTALL.macos.en.md)
- 升级 / Update: 下载并解压新版，运行对应系统安装脚本，再重新加载 `extension`。课程索引保存在独立数据目录中；勿删除该目录。解压目录改变时，需要在浏览器中加载新位置。
- 回退 / Rollback: 旧版下载供排查问题与代码比较；数据库向旧版兼容性没有保证，回退前请关闭浏览器并备份课程数据目录。

For updates, extract the new bundle, rerun the platform installer and reload `extension`. Course data lives separately; keep that data directory. If the extraction path changes, load the new extension location in the browser. Before rolling back, close the browser and back up course data; backward database compatibility is not guaranteed.

核对 ZIP 的 SHA-256，并与同一版本的 `SHA256SUMS.txt` 比较 / Compare the ZIP’s SHA-256 with the checksum from the same release:

```sh
# macOS — replace the filename with your downloaded version
shasum -a 256 WatchOutTeacher-v0.3.0.zip
```

```powershell
# Windows
Get-FileHash .\WatchOutTeacher-v0.3.0.zip -Algorithm SHA256
```

维护发布流程见 [RELEASING.md](RELEASING.md)。
