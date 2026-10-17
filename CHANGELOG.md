# Changelog

## 0.2.0

- Add native Windows installation, per-user Chrome/Edge/Chromium registration and an executable bridge launcher.
- Handle Windows CLI discovery, Unicode paths, binary messaging and document parsing.
- Clean up Windows process trees with Job Objects and bound parser memory/CPU usage.
- Show Alt on Windows and Option on macOS; keep the existing selection behavior.
- Split bilingual installation guides into Windows and macOS paths.
- Run installer, backend and browser checks on both operating systems in CI.

## 0.1.5

- Keep answers visible while scrolling or resizing.
- Make answer text selectable; use a separate lower-right chevron to expand explanations.
- Dismiss on an outside left-click that clears or replaces the selection. Right-click, middle-click and Esc leave the card open.
- Fix repeated selection of the same text and a navigation race after mouse release.

## 0.1.4

- Rename the extension to WatchOutTeacher and add its icon.
- Keep the existing extension ID and data directory for compatible updates.

## 0.1.3

- Add explicit Codex reasoning-effort selection, model-aware choices and request diagnostics.

## 0.1.2

- Add a CLI-backed model dropdown and retain custom model IDs.

## 0.1.1

- Add optional access to all HTTP / HTTPS sites, with revocation controls.

## 0.1.0

- Initial macOS / Chromium extension and local Native Messaging bridge.
- Course imports, SQLite retrieval, Codex adapter, optional Claude adapter and source references.
