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

Both routes reuse the CLI's own sign-in state. There is no API-key field to fill in, and the extension does not drive your desktop chat window. If you install only Claude Code, select it as your preferred provider in step 6.

## 2. Install a browser and Python

Install [Chrome](https://www.google.com/chrome/) or [Edge](https://www.microsoft.com/edge), then check Python:

```sh
python3 --version
```

You need **Python 3.9+** with SQLite FTS5. If it is missing, use the [macOS installer from python.org](https://www.python.org/downloads/macos/) or run `brew install python` if you already use [Homebrew](https://brew.sh/).

Node.js and Xcode are not needed for everyday use. The initial dependency installation needs an internet connection.

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
