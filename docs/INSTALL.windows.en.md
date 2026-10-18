# Install on Windows

[Home](../README.en.md) · [macOS](INSTALL.macos.en.md) · [中文](INSTALL.windows.md)

Recommended: **Windows 11, Chrome or Edge, and Python 3.12 (64-bit)**. Open **PowerShell** from the Start menu for the commands below. No administrator session or WSL needed.

## 1. Install and sign in to an AI client

Choose one. You need the command-line tool; the ChatGPT or Claude desktop app alone is not sufficient.

### ChatGPT account → Codex CLI

Use the [official native Codex installer](https://learn.chatgpt.com/docs/codex/cli):

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://chatgpt.com/codex/install.ps1 | iex"
```

Close and reopen PowerShell, then run:

```powershell
codex --version
codex login
codex login status
```

Complete ChatGPT sign-in in your browser. The final command should confirm authentication. Model access and usage limits depend on the account.

### Or: Claude Code

Use the [official native Claude Code installer](https://code.claude.com/docs/en/setup):

```powershell
irm https://claude.ai/install.ps1 | iex
```

Open a new PowerShell window:

```powershell
claude --version
claude
```

Complete the first-run sign-in. If Claude Code is your only CLI, select it as the preferred provider in the extension settings. The adapter has argument/output contract tests; real Claude account calls are not yet verified.

**For Codex and Claude, use a native Windows `.exe` installation.** The bridge does not enter WSL or execute npm `.cmd` / `.ps1` wrappers through a shell. If you previously used npm, install the official native version as well. The detection panel shows the executable actually selected. Signing in inside WSL does not sign in to the native Windows CLI.

After installing or updating a CLI, fully quit and reopen Chrome / Edge so it receives the new executable paths. The extension needs no API key and does not change any desktop chat's model selection.

### Or: Google account → Gemini CLI

Install [Node.js 22 LTS](https://nodejs.org/en/download) (Gemini CLI requires Node 20+), reopen your terminal, then run:

```sh
npm install -g @google/gemini-cli@0.64.0
gemini --version
gemini
```

Choose **Login with Google** and complete the browser sign-in yourself. Version 0.64.0 is the release-tested baseline. The Gemini website or mobile app alone cannot provide the local command. On Windows, if PowerShell blocks `npm.ps1`, run `npm.cmd install -g @google/gemini-cli@0.64.0` and `gemini.cmd` for installation/sign-in; the bridge itself launches Node and the package entry point directly, without a shell.

Reload the extension, open settings, select **Gemini CLI**, choose Auto / Pro / Flash / Flash-Lite (or a custom model ID), then save. The presets are CLI aliases, not an account entitlement list. Select only the fallback providers whose quota you want to use. Upgrades do not automatically enable Gemini as a fallback.

This adapter uses **Google OAuth only**; API keys, Vertex AI and service-account authentication are not supported. It reuses CLI authentication without reading or copying tokens. Account eligibility, regions, model access and quota depend on Google. See the [login guide](https://geminicli.com/docs/get-started/authentication/) and [quota documentation](https://geminicli.com/docs/resources/quota-and-pricing/). Real-account Gemini answers are not part of the automated release tests.

## 2. Install a browser and Python

Install [Chrome](https://www.google.com/chrome/) or [Edge](https://www.microsoft.com/edge).

Install **Python 3.12 (64-bit)** from [python.org](https://www.python.org/downloads/windows/), keep the Python Launcher, and check **Add python.exe to PATH**. In a new PowerShell window:

```powershell
py -3.12 --version
```

If `py` is unavailable but `python --version` identifies the Python you just installed, substitute `python` for `py -3.12` in this guide. Python 3.9+ with SQLite FTS5 is required; 3.12 is recommended for the pinned dependencies' prebuilt packages. Codex / Claude use needs no Node.js, Visual Studio or compiler; Gemini CLI requires Node.js.

## 3. Download the project

For a tested release, download `WatchOutTeacher-vVERSION.zip` from **Assets** on the [latest release](https://github.com/Blue4u0610/WatchOutTeacher/releases/latest) page. The repository’s **Code → Download ZIP** button and a default Git clone track ongoing development on `main`.

Right-click the downloaded release ZIP, choose **Extract All**, and keep the extracted project somewhere permanent, such as `C:\Users\YourName\Projects\WatchOutTeacher`. Do not work inside the ZIP preview.

Right-click inside the extracted project folder and choose **Open in Terminal**. Confirm that the directory contains `README.md`, `scripts` and `extension`. Or navigate from PowerShell:

```powershell
cd "C:\Users\YourName\Projects\WatchOutTeacher"
```

Replace that example with the real path and keep the quotes for spaces. If you have Git:

```powershell
git clone https://github.com/Blue4u0610/WatchOutTeacher.git
cd WatchOutTeacher
```

## 4. Install the local bridge

From the project root:

```powershell
py -3.12 scripts/install.py
```

The installer downloads Python dependencies, creates a native `.exe` launcher and registers Chrome / Edge / Chromium in your user registry. On completion it prints the extension ID and **Load unpacked extension** path.

The runtime and course index live in `%LOCALAPPDATA%\WatchOutTeacher`. No manual registry editing is needed. The browser starts the bridge on demand; do not leave a terminal server running or launch `bridge/host.py` directly.

Continue with [step 5: load the extension](../README.en.md#5-load-the-extension). On Windows, hold **left Alt** while selecting text. Avoid the right Alt / AltGr composition key. If a webpage shortcut conflicts, choose **Alt + Shift** in settings.

See the README for [updates and removal](../README.en.md#update-or-uninstall). Windows automation covers registration, installation, reinstall, uninstall, real browser messaging and mock answers. Complete the sample question with your own account to verify live AI access.
