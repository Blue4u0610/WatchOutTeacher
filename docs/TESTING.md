# Testing

Version **0.2.1** includes native Windows support and configurable answer instructions. The suite contains **37 Python tests** (two Windows-only tests are skipped on macOS), **38 browser checks per platform**, and a separate install/reinstall/uninstall smoke test. Browser checks run the real extension and Native Messaging host with a mock answer provider; they do not call paid AI services.

## Run locally

Create `.venv` from the repository root:

- Windows / PowerShell: `py -3.12 -m venv .venv`
- macOS / Terminal: `python3 -m venv .venv`

Then, on either system:

```sh
node scripts/python.mjs -m pip install -r requirements.txt
npm ci
npx playwright install chromium
npm test
npm run test:browser
```

The Node wrapper chooses `.venv/Scripts/python.exe` on Windows or `.venv/bin/python` on macOS. The macOS browser runner prefers the installed bridge interpreter when present, avoiding Documents privacy restrictions; install current requirements into that interpreter too when dependencies change. `COURSE_ASSIST_TEST_PYTHON` can select an explicit absolute interpreter path.

The browser runner creates a temporary profile, a unique Native Messaging host name, a free local fixture port and a course database. On Windows, its per-user test registry keys are removed afterward; the production host registration is never replaced. Results and screenshots go to the ignored `test-results/` directory.

[GitHub Actions](https://github.com/Blue4u0610/WatchOutTeacher/actions/workflows/test.yml) runs Python 3.12 and Node 22 on `macos-latest` and `windows-latest`. The Windows runner is Windows Server, so it verifies native Windows code and Chromium integration rather than every Windows 11 desktop configuration. Each run uploads screenshots/results as platform-specific artifacts. The installer lifecycle smoke test is restricted to disposable CI machines and checks Unicode/space paths, data preservation across reinstall and registration removal on uninstall. No AI credentials are supplied to CI.

## Coverage

| Area | Checks |
| --- | --- |
| Local bridge | Binary message framing, caller identity, Unicode paths/stdio, chunked imports, CLI argument quoting, cancellation/timeouts and descendant cleanup |
| Windows | Native `.exe` launcher, per-user registry lifecycle, native-only CLI lookup and Job Object memory limits |
| Documents | PDF pages, PPTX slides, text parsing, encrypted/scanned/corrupt files, course isolation and index deletion |
| Providers | Output schema, citation allowlist, error classification, fallback isolation and reasoning-effort arguments |
| Settings | Persistent model/effort choices, answer instructions/default reset, catalog filtering and unsupported combinations |
| Browser | Alt / Option selection, platform-specific labels, editable-field exclusion, independent expand button, selectable answer text and outside-click dismissal |
| Lifecycle | Scroll/resize retention, stale-result suppression, navigation, course changes, disconnect/reconnect and reload |
| Layout | Viewport edges, light/dark themes, CSS zoom, same-origin and cross-origin frames |

Headless tests pre-grant only the two local fixture origins in a temporary extension copy. The shipped manifest grants no website access by default. Native permission dialogs require a manual check.

[Local macOS mock browser record](evidence/browser-results.json) · For Windows results, open the corresponding CI run.

## Real Codex checks

Earlier integration runs used Codex CLI **0.153.4**, signed in with ChatGPT, on macOS 27 / Apple Silicon. Python was 3.9.6; browser automation used Node 22 and Playwright 1.56.1 / Chromium 141.

- A full browser → native host → Codex run answered the bundled arithmetic question.
- Imported PDF and PPTX fixtures changed the answer to the fictional Lumen question; the displayed source identified a supplied document and page.
- A separate call passed explicit `high` effort to GPT-6-Astra and returned the expected arithmetic answer. The recorded effort is the requested value, not a server-side configuration receipt.

[Historical live browser record](evidence/live-results.json) · [Explicit-effort record](evidence/effort-live-result.json)

To run the current live suite, sign in to Codex and run `npm run test:live`. It makes real requests and uses the account's allowance. Historical screenshots may show an older interface.

## Answer-instruction smoke check

A real Codex call on macOS used the 0.2.1 default instructions, an unrelated handout and a question about an undefined fictional protocol. It returned `basis: insufficient`, requested the missing definition and supplied no citations. This checks one controlled case, not a general hallucination guarantee. [Recorded result](evidence/prompt-live-result.json).

## Manual checks still needed

Windows real-account Codex / Claude login and inference have not been exercised in CI. Historical live Codex evidence below is macOS-only.

- Real website permission dialogs, Chrome / Edge installation variants and unusual browser/extension combinations.
- A school's actual Canvas Classic / New Quizzes markup and iframe domains.
- Real Claude Code authentication, responses and fallback; the adapter currently has contract tests only.
- Browser menu zoom, operating-system shortcut conflicts and very small embedded frames.

For a useful bug report, include the version, browser, provider, reproduction steps and error category. Use the bundled fixture where possible. Do not include account tokens, private course files or your local course database.
