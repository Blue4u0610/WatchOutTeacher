# Install on macOS

[Home](../README.en.md) · [Windows](INSTALL.windows.en.md) · [中文](INSTALL.macos.md)

You need Chrome or Edge, Python 3.9+, and an account with access to a supported AI service. Press `⌘ Space` and open Terminal for the commands below.

## 1. Install and sign in to an AI client

Choose one route. You do not need both.

**Route A: a ChatGPT account with Codex CLI — verified with real requests**

Use your existing ChatGPT account if it has Codex access. You need the **Codex command-line tool**; installing the ChatGPT desktop app alone does not complete this step.

Follow the [official Codex installation guide](https://learn.chatgpt.com/docs/codex/cli):

```sh
curl -fsSL https://chatgpt.com/codex/install.sh | sh
```

Open a new Terminal window, then sign in:

```sh
codex --version
codex login
codex login status
```

Choose ChatGPT sign-in and complete the browser flow. The last command should report that you are logged in. Model access and usage limits depend on your account.

**Route B: Claude Code — optional; real-account integration is not yet verified**

Follow the [official Claude Code installation guide](https://code.claude.com/docs/en/setup):

```sh
curl -fsSL https://claude.ai/install.sh | bash
```

Open a new Terminal window and run:

```sh
claude --version
claude
```

Complete the first-run sign-in flow. The Claude desktop app and the `claude` command are separate installations. WatchOutTeacher checks the CLI flags it needs and reports incompatible versions.

All routes reuse the CLI's own sign-in state. There is no API-key field to fill in, and the extension does not drive your desktop chat window. If you install only Claude Code, select it as your preferred provider in step 6.

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

Install [Chrome](https://www.google.com/chrome/) or [Edge](https://www.microsoft.com/edge), then check Python:

```sh
python3 --version
```

You need **Python 3.9+** with SQLite FTS5. If it is missing, use the [macOS installer from python.org](https://www.python.org/downloads/macos/) or run `brew install python` if you already use [Homebrew](https://brew.sh/).

Codex / Claude use needs no Node.js or Xcode; Gemini CLI requires Node.js. The initial dependency installation needs an internet connection.

## 3. Download the project

For a tested release, download `WatchOutTeacher-vVERSION.zip` from **Assets** on the [latest release](https://github.com/Blue4u0610/WatchOutTeacher/releases/latest) page. The repository’s **Code → Download ZIP** button and a default Git clone track ongoing development on `main`.

Extract the downloaded release ZIP somewhere you intend to keep. In Terminal, type `cd ` with a trailing space, drag the extracted folder into the window, and press Return.

If you use Git:

```sh
mkdir -p ~/Projects
cd ~/Projects
git clone https://github.com/Blue4u0610/WatchOutTeacher.git
cd WatchOutTeacher
```

Run subsequent project commands in this directory, which contains `README.md`, `bridge` and `extension`.

## 4. Install the local bridge

```sh
python3 scripts/install.py
```

The installer prints the extension ID and the directory to load. It creates an isolated Python environment and registers the Native Messaging host for your user in Chrome, Edge and Chromium. No `sudo` is needed.

The browser starts the bridge when required. You do not need a terminal left running in the background, and you should not launch `bridge/host.py` yourself.

Continue with [step 5: load the extension](../README.en.md#5-load-the-extension). On macOS, hold **Option ⌥** while selecting a question.
