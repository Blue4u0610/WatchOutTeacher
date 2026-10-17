<p align="center">
  <img src="extension/icons/icon-128.png" width="88" alt="WatchOutTeacher">
</p>

<h1 align="center">WatchOutTeacher</h1>
<p align="center">One less tab. One more look at the source.</p>
<p align="center"><a href="README.md">中文</a> · <strong>English</strong></p>

Hold **Option ⌥**, select a question on a webpage, and read the answer beside it. Click **⌄** for the explanation and sources. Select the answer text to copy it.

WatchOutTeacher is a course companion for **macOS + Chrome / Edge / Chromium**. It calls your local **Codex CLI** or **Claude Code** and can use documents from the course you select. It never clicks an answer or submits an assignment. The final click is still yours.

[Install](#installation-from-zero) · [Use](#everyday-use) · [Documents and privacy](#documents-and-privacy) · [Troubleshoot](#troubleshooting) · [Develop](#development)

## What it does

- **Answers in place.** The card stays visible while you scroll. Explanations expand separately, so answer text remains selectable.
- **Course-aware references.** Import PDF, PPTX, TXT and Markdown; citations identify the document and page, slide or text chunk.
- **Your choice of model and effort.** Fetch the Codex model list from your CLI and select automatic or explicit reasoning effort.
- **Optional fallback.** Try the other provider after the preferred one fails, or leave fallback off.
- **Website permissions you choose.** Enable one course site or grant access to all HTTP / HTTPS sites.

<details>
<summary>See the interface</summary>

![Answer, explanation and document reference](docs/evidence/mock-source.png)

This screenshot uses a bundled fixture and a mock answer provider. See [testing](docs/TESTING.md) for real Codex runs and their limits. The extension UI is currently in Chinese; explanations are in English.

</details>

## Installation, from zero

You need a Mac, Chrome or Edge, and an account that can use one of the supported AI tools. Run the commands below in Terminal: press `⌘ Space`, search for “Terminal”, and open it.

> This is a local extension, not a website to host on a server. GitHub hosts the source; your computer runs the CLI. Safari is not supported yet.

### 1. Install and sign in to an AI client

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

### 2. Install a browser and Python

Install [Chrome](https://www.google.com/chrome/) or [Edge](https://www.microsoft.com/edge), then check Python:

```sh
python3 --version
```

You need **Python 3.9+** with SQLite FTS5. If it is missing, use the [macOS installer from python.org](https://www.python.org/downloads/macos/) or run `brew install python` if you already use [Homebrew](https://brew.sh/).

Node.js and Xcode are not needed for everyday use. The initial dependency installation needs an internet connection.

### 3. Download the project

Choose **Code → Download ZIP** on this repository and extract it somewhere you intend to keep. In Terminal, type `cd ` with a trailing space, drag the extracted folder into the window, and press Return.

If you use Git:

```sh
mkdir -p ~/Projects
cd ~/Projects
git clone https://github.com/Blue4u0610/WatchOutTeacher.git
cd WatchOutTeacher
```

Run subsequent project commands in this directory, which contains `README.md`, `bridge` and `extension`.

### 4. Install the local bridge

```sh
python3 scripts/install.py
```

The installer prints the extension ID and the directory to load. It creates an isolated Python environment and registers the Native Messaging host for your user in Chrome, Edge and Chromium. No `sudo` is needed.

The browser starts the bridge when required. You do not need a terminal left running in the background, and you should not launch `bridge/host.py` yourself.

### 5. Load the extension

1. Open `chrome://extensions` in Chrome or `edge://extensions` in Edge.
2. Turn on **Developer mode**.
3. Click **Load unpacked**.
4. Select the **`extension` subfolder** inside this project.
5. Pin WatchOutTeacher to the toolbar and click its icon to open settings.

**Select `extension`, not the project root.** A “Manifest file is missing or unreadable” error usually means you picked the wrong folder.

### 6. Grant access and select a provider

1. Look for **本地桥接已连接** (“Local bridge connected”) on the settings page.
2. Enter your course site, such as `https://school.instructure.com`, then authorize it. **授权所有网站** optionally enables all HTTP / HTTPS sites.
3. Click **检测 CLI** (“Check CLI”) to check installation and sign-in status.
4. Select the preferred provider, model and Codex reasoning effort. Click **保存设置** (“Save”). If you have only one CLI, you can turn fallback off.
5. Refresh the webpage you want to use. Browser internal pages and extension stores cannot be accessed.

The installation check does not generate an answer or prove that the account has remaining quota. Try a small question next.

### 7. Ask a question, then add your notes

On an authorized webpage, hold **⌥**, press the left mouse button over text, and drag across the question and its options. Release the mouse and wait for the answer.

For a predictable first test, run this in the project directory:

```sh
python3 -m http.server 8765 --bind 127.0.0.1 --directory tests
```

Authorize `http://localhost:8765`, open the [local demo](http://localhost:8765/fixture.html), and select the first `2 + 2` question. **This makes a real CLI request and uses your account's allowance.** Press `Ctrl+C` when finished; the demo server is not needed for everyday use.

Next, create a course in settings and import PDF, PPTX, TXT or MD files. Wait for **已导入** (“Imported”). To test references, import `tests/material.md` and select the second demo question. The file defines Violet as the fictional Lumen protocol's ready color; the reference should point to that file.

## Everyday use

| Action | Gesture |
| --- | --- |
| Ask | Hold ⌥ and left-drag text; ordinary selection does nothing |
| Read the explanation and sources | Click ⌄ at the card's lower-right corner; click again to collapse |
| Copy | Select text and press ⌘C; an additional copy button appears in the expanded card |
| Scroll or resize | The card stays visible and repositions |
| Dismiss | Left-click outside the card and clear or replace the original selection |
| Ask another question | Make a new ⌥ selection; the previous request is cancelled |
| Resolve a shortcut conflict | Switch to Option + Shift in settings |
| Change course | Choose it in settings; subsequent requests use that course |

Right-click, middle-click and Esc do not dismiss the card. Navigation, reloads, removal of the original text node, and course changes clear outdated answers.

### Models and reasoning effort

Select the model and effort **in this extension's settings**. Save to apply them to the next question. Changing the model in another Codex chat does not change this extension.

- **Automatic:** omit the effort parameter and use the CLI / service default.
- **Explicit:** choose a supported ordinary level such as Low, Medium, High, XHigh or Max; the adapter sends that value to the CLI.
- **Custom model:** enter a full model ID; the CLI checks whether it can use it.

Higher effort usually takes longer and uses more resources; it does not guarantee a better answer. Ultra includes automatic task delegation and is not offered here. Claude keeps its own default effort. Refresh the model list in settings instead of relying on a model list frozen in a README.

## Documents and privacy

```text
Selected text + question context
                ↓
Local course index → relevant excerpts
                ↓
Codex CLI / Claude Code → corresponding AI service
                ↓
Answer + explanation + references → page overlay
```

Files are parsed into text when imported and stored in a local SQLite index. Each question retrieves at most **12 chunks** to send to the model. The extension does not reopen every original file for each question or train a model on your course. Every request starts a separate session.

| Format | Extracted content | Limits |
| --- | --- | --- |
| PDF | Extractable text and file page numbers | Scans need OCR first; encrypted PDFs are rejected |
| PPTX | Text boxes, grouped text and tables | No image/chart interpretation or speaker notes |
| TXT / Markdown | UTF-8 text | References identify chunks, not line numbers |

The per-file limit is **30 MB**. Legacy `.ppt`, Word files, images and automatic screenshots are not supported. Keyword retrieval has limits with synonyms, Chinese tokenization and cross-language questions. If nothing matches, the tool reports that it used opening chunks instead. A valid reference identifies supplied material; it does not prove the model's interpretation is correct.

The index lives at `~/Library/Application Support/CourseAssist/courses.sqlite3`. The old directory name is retained for existing installations. Selected text, question context and retrieved excerpts go to your chosen AI service through its CLI: **this is not offline inference**. Removing a document deletes its index, not the original file.

Question and answer bodies are not kept in diagnostic logs. Diagnostics record the provider, requested model and effort, error category, duration and retrieval counts. Model access, subscriptions and service charges follow the account signed in to the CLI.

## Update or uninstall

For a Git installation, close question/settings pages and disable WatchOutTeacher in the browser's extension manager. In the project directory, run:

```sh
git pull --ff-only
python3 scripts/install.py
```

Enable and **Reload** the extension, then refresh your question page. For ZIP installations, download and replace the source. If the directory moved, load the new `extension` path. Do not delete the source directory while the browser is using it.

To uninstall:

```sh
python3 scripts/install.py --uninstall
```

Remove the extension from the browser. Course data is retained. To remove it too, quit the browser, use Finder's “Go to Folder” for `~/Library/Application Support/CourseAssist`, and move that folder to Trash.

## Troubleshooting

| Symptom | First check |
| --- | --- |
| Missing manifest | Load the project's `extension` subfolder |
| Native host missing or exited | Rerun the installer and reload the extension; keep the runtime in Application Support |
| Bridge disconnected | Use the reconnect button in settings, refresh the page and select again |
| No response to selection | Check site access, refresh, hold ⌥ before pressing the mouse; editable fields are excluded and selections are limited to 8,000 characters |
| Canvas embedded questions do not respond | Authorize the question iframe's own domain or choose all-site access |
| Authentication or quota error | Run `codex login status`, or open `claude` and follow the account prompts |
| Unsupported CLI flags | Update the CLI and check again; see [tested versions](docs/TESTING.md) |
| Missing options or formulas | Select the complete question; images and unreadable formulas are not sent |
| No course reference | Check import warnings, the selected course and retrieval counts; insufficient material may lead to a general-knowledge answer |
| Safari installation | Not available yet; see the [porting notes](docs/SAFARI.md) |

## Development

Python is required to run the bridge. Browser tests additionally need **Node.js 22+**. Tests use temporary browser profiles and course databases, not your everyday browser account.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
npm ci
npx playwright install chromium
npm test
npm run test:browser
```

For real-model tests, sign in to Codex first. This uses your account's allowance:

```sh
npm run test:live
```

[Architecture](docs/ARCHITECTURE.md) · [Testing](docs/TESTING.md) · [Changelog](CHANGELOG.md) · [Contributing](CONTRIBUTING.md)

Use this for course reading and revision within your course's AI rules. WatchOutTeacher is not affiliated with OpenAI, Anthropic or Canvas.
