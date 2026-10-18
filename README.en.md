<p align="center">
  <img src="extension/icons/icon-128.png" width="88" alt="WatchOutTeacher">
</p>

<h1 align="center">WatchOutTeacher</h1>
<p align="center">One less tab. One more look at the source.</p>
<p align="center"><a href="README.md">中文</a> · <strong>English</strong></p>

<p align="center">
  <a href="https://github.com/Blue4u0610/WatchOutTeacher/releases/latest"><img src="https://img.shields.io/github/v/release/Blue4u0610/WatchOutTeacher" alt="Latest release"></a>
  <a href="https://github.com/Blue4u0610/WatchOutTeacher/actions/workflows/test.yml"><img src="https://github.com/Blue4u0610/WatchOutTeacher/actions/workflows/test.yml/badge.svg" alt="Tests"></a>
</p>

Hold **Alt (Windows) or Option ⌥ (macOS)**, select a question on a webpage, and read the answer beside it. Click **⌄** for the explanation and sources. Select the answer text to copy it.

WatchOutTeacher is a course companion for **Windows / macOS + Chrome / Edge / Chromium**. It calls your local **Codex CLI**, **Claude Code** or **Gemini via Antigravity CLI** and can use documents from the course you select. It never clicks an answer or submits an assignment. The final click is still yours.

[Install](#installation-from-zero) · [Use](#everyday-use) · [Documents and privacy](#documents-and-privacy) · [Troubleshoot](#troubleshooting) · [Develop](#development)

[Download latest release](https://github.com/Blue4u0610/WatchOutTeacher/releases/latest) · [Version history](docs/VERSIONS.md) · [Changelog](CHANGELOG.md)

Releases include a versioned source bundle and SHA-256 checksum. One bundle supports both Windows and macOS; use the matching installation guide. `main` is the development branch.

## What it does

- **Answers in place.** The card stays visible while you scroll. Explanations expand separately, so answer text remains selectable.
- **Course-aware references.** Import PDF, PPTX, TXT and Markdown; citations identify the document and page, slide or text chunk.
- **Your choice of model and effort.** Fetch the Codex model list from your CLI and select automatic or explicit reasoning effort.
- **Optional fallback.** Choose which providers may be tried after the preferred one fails, or leave fallback off. Upgrading does not automatically enable Gemini.
- **Website permissions you choose.** Enable one course site or grant access to all HTTP / HTTPS sites.

<details>
<summary>See the interface</summary>

![Answer, explanation and document reference](docs/evidence/mock-source.png)

This screenshot uses a bundled fixture and a mock answer provider. See [testing](docs/TESTING.md) for real Codex runs and their limits. The extension UI is currently in Chinese; explanations are in English.

</details>

## Installation, from zero

Choose your operating system, complete **steps 1–4** in its guide, then return here for step 5.

| System | Installation guide | Ask a question |
| --- | --- | --- |
| Windows 11 (native) | [Windows / PowerShell](docs/INSTALL.windows.en.md) | Left Alt + drag |
| macOS | [macOS / Terminal](docs/INSTALL.macos.en.md) | Option ⌥ + drag |

Both guides start with **installing and signing in to Codex CLI, Claude Code or Gemini via Antigravity CLI**, then cover Python, the download and the local bridge. Installing the ChatGPT or Claude desktop app alone is not enough. Use native installers for all three providers on Windows; this extension does not call CLIs installed only inside WSL.

No server needed: GitHub hosts the source and your computer runs the bridge. Safari and Firefox are not supported. The UI is currently in Chinese. Automated tests cover macOS and Windows; see [testing](docs/TESTING.md) for the scope of real-account AI checks.

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

On macOS, detection also checks the Claude Code bundled with Claude Desktop. Desktop sign-in may not authenticate the CLI. Check **检测 CLI**; if it reports signed out, run the detected executable in Terminal with `auth login`.

### 7. Ask a question, then add your notes

On an authorized webpage, hold **left Alt (Windows) or Option ⌥ (macOS)**, press the left mouse button over text, and drag across the question and its options. Release the mouse and wait for the answer.

For a predictable first test, run this in the project directory:

**Windows / PowerShell:**

```powershell
py -3.12 -m http.server 8765 --bind 127.0.0.1 --directory tests
```

**macOS / Terminal:**

```sh
python3 -m http.server 8765 --bind 127.0.0.1 --directory tests
```

Authorize `http://localhost:8765`, open the [local demo](http://localhost:8765/fixture.html), and select the first `2 + 2` question. **This makes a real CLI request and uses your account's allowance.** Press `Ctrl+C` when finished; the demo server is not needed for everyday use.

Next, create a course in settings and drag PDF, PPTX, TXT or MD files into the import area, or use the file picker. Multiple files are supported. Wait for **已导入** (“Imported”). To test references, import `tests/material.md` and select the second demo question. The file defines Violet as the fictional Lumen protocol's ready color; the reference should point to that file.

For a Zotero batch drop, check the received-file count shown in the import area. If it is lower than the selected attachment count, first drag the attachments to a folder in Finder / File Explorer, then drag those files into the extension. The queue lists every file the browser actually provides, with progress and individual results; further drops can be added while importing.

## Everyday use

| Action | Gesture |
| --- | --- |
| Ask | Hold Alt / Option and left-drag text; ordinary selection does nothing |
| Read the explanation and sources | Click ⌄ at the card's lower-right corner; click again to collapse |
| Copy | Select text and press Ctrl+C (Windows) or ⌘C (macOS); an additional copy button appears in the expanded card |
| Scroll or resize | The card stays visible and repositions |
| Dismiss | Left-click outside the card and clear or replace the original selection |
| Ask another question | Make a new Alt / Option selection; the previous request is cancelled |
| Resolve a shortcut conflict | Switch to Alt + Shift / Option + Shift in settings |
| Change course | Choose it in settings; subsequent requests use that course |

Right-click, middle-click and Esc do not dismiss the card. Navigation, reloads, removal of the original text node, and course changes clear outdated answers.

### Models and reasoning effort

Select the model and effort **in this extension's settings**. Save to apply them to the next question. Changing the model in another Codex chat does not change this extension.

- **Automatic:** omit the effort parameter and use the CLI / service default.
- **Explicit:** choose a supported ordinary level such as Low, Medium, High, XHigh or Max; the adapter sends that value to the CLI.
- **Custom model:** enter a full model ID; the CLI checks whether it can use it.

Higher effort usually takes longer and uses more resources; it does not guarantee a better answer. Ultra includes automatic task delegation and is not offered here. Claude keeps its default effort; Gemini effort variants are selected in its model list. Refresh the model list in settings instead of relying on a model list frozen in a README.

### Answer instructions

In settings, open **回答要求** (“Answer instructions”) under **模型和操作**. Edit the text and save. The same instructions apply to future questions in all courses and to both providers. You can set language, length and how the answer should use course material; the limit is 2,000 characters. **恢复默认回答要求** fills the default text; save to apply it. Saving an empty field also restores the default.

The default asks the model to prefer relevant PPT/PDF material, paraphrase instead of copying passages, cite only supporting sources, and clearly say when the retrieved excerpts are insufficient. Reliable general knowledge must be labelled separately; uncertain answers should ask for the missing information. These instructions travel with each question and are stored locally, not in diagnostic logs. They guide the model but do not guarantee factual accuracy; references still need checking.

Gemini uses Antigravity CLI 1.4.2 and reads the account’s model catalog. High / Medium / Low variants appear as model choices when available. Auto picks the first Gemini entry in that catalog.

## Documents and privacy

```text
Selected text + question context
                ↓
Local course index → relevant excerpts
                ↓
Codex CLI / Claude Code / Gemini via Antigravity CLI → corresponding AI service
                ↓
Answer + explanation + references → page overlay
```

Files are parsed into text when imported and stored in a local SQLite index. Each question retrieves at most **12 chunks** to send to the model. The extension does not reopen every original file for each question or train a model on your course. Every request starts a separate session.

| Format | Extracted content | Limits |
| --- | --- | --- |
| PDF | Extractable text and file page numbers | Scans need OCR first; encrypted PDFs are rejected |
| PPTX | Text boxes, grouped text and tables | No image/chart interpretation or speaker notes |
| TXT / Markdown | UTF-8 text | References identify chunks, not line numbers |

The per-file limit is **100 MB**. Legacy `.ppt`, Word files, images and automatic screenshots are not supported. Keyword retrieval has limits with synonyms, Chinese tokenization and cross-language questions. If nothing matches, the tool reports that it used opening chunks instead. A valid reference identifies supplied material; it does not prove the model's interpretation is correct.

The local index lives at:

- Windows: `%LOCALAPPDATA%\WatchOutTeacher\courses.sqlite3`
- macOS: `~/Library/Application Support/CourseAssist/courses.sqlite3` (retained for existing installations)

 Selected text, question context and retrieved excerpts go to your chosen AI service through its CLI: **this is not offline inference**. Removing a document deletes its index, not the original file.

Gemini uses Antigravity CLI and the signed-in Google account. The CLI retains local conversation records. The adapter rejects global hooks, MCP, plugins and rules rather than executing them. Provider-side retention follows the account terms.

Question and answer bodies are not kept in diagnostic logs. Diagnostics record the provider, requested model and effort, error category, duration and retrieval counts. Model access, subscriptions and service charges follow the account signed in to the CLI.

## Update or uninstall

For a Git installation, close question/settings pages and disable WatchOutTeacher in the browser's extension manager. In the project directory, run:

**Windows:**

```powershell
git pull --ff-only
py -3.12 scripts/install.py
```

**macOS:**

```sh
git pull --ff-only
python3 scripts/install.py
```

Enable and **Reload** the extension, then refresh your question page. For ZIP installations, download and replace the source. If the directory moved, load the new `extension` path. Do not delete the source directory while the browser is using it.

To uninstall:

Windows: `py -3.12 scripts/install.py --uninstall`. macOS: `python3 scripts/install.py --uninstall`.

Remove the extension from the browser. Course data is retained. To remove it too, quit the browser and delete the data folder listed above for your system. Windows registration is per-user and requires no administrator access.

## Troubleshooting

| Symptom | First check |
| --- | --- |
| Missing manifest | Load the project's `extension` subfolder |
| Native host missing or exited | Rerun the installer for your system and reload the extension; keep its generated runtime path |
| Bridge disconnected | Use the reconnect button in settings, refresh the page and select again |
| No response to selection | Check site access, refresh, hold Alt / Option before pressing the mouse; editable fields are excluded and selections are limited to 8,000 characters |
| Canvas embedded questions do not respond | Authorize the question iframe's own domain or choose all-site access |
| Authentication or quota error | Run `codex login status`, or open `claude` and follow the account prompts |
| Windows cannot find the CLI | Use native installers, verify the agy command for Gemini, then restart the browser |
| Unsupported CLI flags | Update the CLI and check again; see [tested versions](docs/TESTING.md) |
| Missing options or formulas | Select the complete question; images and unreadable formulas are not sent |
| No course reference | Check import warnings, the selected course and retrieval counts; insufficient material may lead to a general-knowledge answer |
| Safari installation | Not available yet; see the [porting notes](docs/SAFARI.md) |

## Development

Python is required to run the bridge. Browser tests additionally need **Node.js 22+**. Tests use temporary browser profiles and course databases, not your everyday browser account.

Create the environment with `py -3.12 -m venv .venv` on Windows or `python3 -m venv .venv` on macOS. Then, on either system:

```sh
node scripts/python.mjs -m pip install -r requirements.txt
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

Use this for course reading and revision within your course's AI rules. WatchOutTeacher is not affiliated with OpenAI, Anthropic, Google or Canvas.
