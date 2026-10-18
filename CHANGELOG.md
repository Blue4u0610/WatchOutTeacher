# Changelog

User-visible changes, newest first. Format inspired by [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

[下载 / Releases](https://github.com/Blue4u0610/WatchOutTeacher/releases) · [版本历史 / Version history](docs/VERSIONS.md)

Dates below identify the code snapshot in America/New_York. GitHub publication dates may be later for backfilled releases. Versions 0.1.0–0.1.4 predate the first committed snapshot and have no separate downloadable release.

## [Unreleased]

## [0.3.0] - 2026-10-18

### Added

- Gemini through native Antigravity CLI 1.4.2 on Windows and macOS, with account-provided model choices including effort variants.
- A fallback-provider checklist; upgrades preserve existing Codex / Claude choices without opting into Gemini.
- Text-only custom-agent requests, streamed answer validation, and rejection of incompatible global customizations.
- Bilingual installation guides and native CLI contract checks in release CI.

### Verified

- Real Gemini arithmetic, course retrieval with a source citation, and a file-access canary on macOS.
- The CLI retains local conversation records. Google account preferences control service-side data use.

## [0.2.3] - 2026-10-18

### Added

- Formal GitHub Releases, bilingual notes, source bundles with SHA-256 checksums and a test-gated tag release workflow.

### Changed

- Raise the per-file upload limit to 100 MB for larger lecture decks.
- Show a batch queue with received counts and per-file progress, success and errors; allow further drops while importing.
- Capture file items synchronously and explain the Finder / Explorer fallback when Zotero supplies fewer files than selected.

## [0.2.2] - 2026-10-18

### Added

- Drag multiple course files into the import area, with per-file validation and upload feedback.
- Detect the native Claude Code bundled with Claude Desktop on macOS and report CLI login status.

## [0.2.1] - 2026-10-17

### Added

- Add editable answer instructions, saved locally and applied to both AI providers.
- Default to course-first paraphrasing, supported citations and explicit uncertainty when evidence is insufficient.
- Add a restore-default control and a 2,000-character limit.

## [0.2.0] - 2026-10-17

### Added

- Add native Windows installation, per-user Chrome/Edge/Chromium registration and an executable bridge launcher.
- Handle Windows CLI discovery, Unicode paths, binary messaging and document parsing.
- Clean up Windows process trees with Job Objects and bound parser memory/CPU usage.
- Show Alt on Windows and Option on macOS; keep the existing selection behavior.
- Split bilingual installation guides into Windows and macOS paths.
- Run installer, backend and browser checks on both operating systems in CI.

## [0.1.5] - 2026-10-17

### Added

- Keep answers visible while scrolling or resizing.
- Make answer text selectable; use a separate lower-right chevron to expand explanations.
- Dismiss on an outside left-click that clears or replaces the selection. Right-click, middle-click and Esc leave the card open.
- Fix repeated selection of the same text and a navigation race after mouse release.

## Early development (no separate Git snapshots)

### 0.1.4

- Rename the extension to WatchOutTeacher and add its icon.
- Keep the existing extension ID and data directory for compatible updates.

### 0.1.3

- Add explicit Codex reasoning-effort selection, model-aware choices and request diagnostics.

### 0.1.2

- Add a CLI-backed model dropdown and retain custom model IDs.

### 0.1.1

- Add optional access to all HTTP / HTTPS sites, with revocation controls.

### 0.1.0

- Initial macOS / Chromium extension and local Native Messaging bridge.
- Course imports, SQLite retrieval, Codex adapter, optional Claude adapter and source references.

[Unreleased]: https://github.com/Blue4u0610/WatchOutTeacher/compare/v0.3.0...HEAD
[0.1.5]: https://github.com/Blue4u0610/WatchOutTeacher/releases/tag/v0.1.5
[0.2.0]: https://github.com/Blue4u0610/WatchOutTeacher/compare/v0.1.5...v0.2.0
[0.2.1]: https://github.com/Blue4u0610/WatchOutTeacher/compare/v0.2.0...v0.2.1
[0.2.2]: https://github.com/Blue4u0610/WatchOutTeacher/compare/v0.2.1...v0.2.2
[0.2.3]: https://github.com/Blue4u0610/WatchOutTeacher/compare/v0.2.2...v0.2.3

[0.3.0]: https://github.com/Blue4u0610/WatchOutTeacher/compare/v0.2.3...v0.3.0
