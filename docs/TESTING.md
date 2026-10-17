# Testing

The current local baseline is **28 Python tests and 35 browser checks**, recorded on 2026-10-17 for version 0.1.5. Browser checks run the real extension and Native Messaging host with a mock answer provider. They do not claim to test every school website or model.

## Run locally

From the repository root:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
npm ci
npx playwright install chromium
npm test
npm run test:browser
```

The browser runner prefers the installed bridge Python when available, avoiding macOS privacy restrictions on Documents checkouts; otherwise it uses `.venv/bin/python`. Set `COURSE_ASSIST_TEST_PYTHON` to an absolute Python executable if your test environment is elsewhere. It creates a temporary browser profile, host registration and course database, then removes them on exit. Results and screenshots go to the ignored `test-results/` directory.

The GitHub Actions workflow runs these same checks on macOS without AI credentials. Live model tests are deliberately excluded from CI.

## Coverage

| Area | Checks |
| --- | --- |
| Local bridge | Message framing and size limits, caller identity, chunked imports, process cancellation and timeouts |
| Documents | PDF pages, PPTX slides, text parsing, encrypted/scanned/corrupt files, course isolation and index deletion |
| Providers | Output schema, citation allowlist, error classification, fallback isolation and reasoning-effort arguments |
| Settings | Persistent model/effort choices, catalog filtering and unsupported combinations |
| Browser | Option selection, editable-field exclusion, independent expand button, selectable answer text and outside-click dismissal |
| Lifecycle | Scroll/resize retention, stale-result suppression, navigation, course changes, disconnect/reconnect and reload |
| Layout | Viewport edges, light/dark themes, CSS zoom, same-origin and cross-origin frames |

Headless tests pre-grant only the two local fixture origins in a temporary extension copy. The shipped manifest grants no website access by default. Native permission dialogs require a manual check.

[Latest mock browser record](evidence/browser-results.json)

## Real Codex checks

Earlier integration runs used Codex CLI **0.153.4**, signed in with ChatGPT, on macOS 27 / Apple Silicon. Python was 3.9.6; browser automation used Node 22 and Playwright 1.56.1 / Chromium 141.

- A full browser → native host → Codex run answered the bundled arithmetic question.
- Imported PDF and PPTX fixtures changed the answer to the fictional Lumen question; the displayed source identified a supplied document and page.
- A separate call passed explicit `high` effort to GPT-6-Astra and returned the expected arithmetic answer. The recorded effort is the requested value, not a server-side configuration receipt.

[Historical live browser record](evidence/live-results.json) · [Explicit-effort record](evidence/effort-live-result.json)

To run the current live suite, sign in to Codex and run `npm run test:live`. It makes real requests and uses the account's allowance. Historical screenshots may show an older interface.

## Manual checks still needed

- Real website permission dialogs and unusual browser/extension combinations.
- A school's actual Canvas Classic / New Quizzes markup and iframe domains.
- Real Claude Code authentication, responses and fallback; the adapter currently has contract tests only.
- Browser menu zoom, operating-system shortcut conflicts and very small embedded frames.

For a useful bug report, include the version, browser, provider, reproduction steps and error category. Use the bundled fixture where possible. Do not include account tokens, private course files or your local course database.
