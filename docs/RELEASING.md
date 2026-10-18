# 发布版本 · Releasing

参考 [GitHub Releases](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases)、[GitHub CLI 的发布页](https://github.com/cli/cli/releases) 和 [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)，本项目使用固定 Git 标签、面向用户的更新说明、下载包和校验值。

## 维护步骤

1. 更新 `extension/manifest.json`、`package.json`、`package-lock.json` 中的版本号（包含 lockfile 的根包版本）。标签格式为 `vX.Y.Z`，三处版本必须一致。
2. 将 `CHANGELOG.md` 的 Unreleased 变更整理到新版本，记录日期、更新比较链接，并更新 `docs/VERSIONS.md`。
3. 新增 `docs/releases/vX.Y.Z.md`，包含 `## 中文` 和 `## English`。说明用户可见变化、支持系统、安装或迁移步骤及已知限制；不要直接粘贴提交列表。
4. 提交并合入 `main`，确认该提交的 Tests 通过。在干净检出目录运行 `python3 scripts/release.py --tag vX.Y.Z`（Windows 可用 `py -3.12`）验证打包。
5. 在已检查的提交创建注解标签并推送。例如版本为 0.2.4 时：

```sh
git tag -a v0.2.4 -m "WatchOutTeacher v0.2.4"
git push origin v0.2.4
```

`Release` 工作流会在标签对应的提交重新执行 Windows/macOS 安装、后端与浏览器测试。通过后校验版本和双语说明，打包已提交的源码，创建草稿、上传 ZIP 和 SHA-256，再公开发布并标记为 Latest。失败时不会发布；草稿可通过重新运行任务继续完成。

已公开版本不能被工作流覆盖。修复发布内容时使用新版本，不移动或重用旧标签。下载包不包含课程数据库、本地依赖环境或账户凭据。ZIP 是源码安装包，并非独立 `.exe` / `.dmg` 安装器。

`0.x` 表示项目仍在演进。未来新增功能使用次版本号（如 `0.3.0`），兼容性修复使用修订号（如 `0.2.4`）；破坏性变更在更新说明中明确标注。既有版本号保留历史原样。

## English

Keep the extension, package and lockfile versions aligned. Write bilingual notes under `docs/releases/`, update the changelog and version table, merge to `main` and check CI. Tag the reviewed commit with an annotated `vX.Y.Z` tag, then push that tag.

The tag workflow reruns both OS test suites, validates metadata, packages committed source, attaches a checksum and publishes the draft only after uploads succeed. Published releases cannot be overwritten by the workflow; use a new version for corrections. Source bundles exclude local runtime and account data. They are not standalone installers.

Use minor bumps for new features and patch bumps for compatible fixes going forward. Existing version numbers remain unchanged. Historical entries were backfilled only where actual Git snapshots exist; see [version history](VERSIONS.md).
