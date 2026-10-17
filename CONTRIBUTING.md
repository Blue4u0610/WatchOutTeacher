# Contributing

Small, focused fixes are welcome. For a larger change, open an issue describing the problem and the proposed behavior first.

## Before opening a pull request

1. Follow the development setup in the README.
2. Run `npm test` for bridge changes and `npm run test:browser` for extension changes.
3. Use the bundled fixtures instead of private course material.
4. Describe what changed and how you checked it. Include a screenshot for visible UI changes.

Keep English and Chinese installation instructions in sync. Do not commit virtual environments, dependency folders, credentials, browser profiles or course databases. Live tests are optional and consume the account's allowance.

The extension must continue to leave page answers and submission controls untouched. Changes to permissions, CLI tools or data handling should explain why the new access is needed.

## Reporting a bug

Include the extension version, macOS/browser versions, provider, reproduction steps and visible error. A short reproduction on `tests/fixture.html` is ideal. Redact private URLs and document contents before posting screenshots.
