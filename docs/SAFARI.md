# Safari support

WatchOutTeacher currently ships a Chromium Manifest V3 extension and a Windows / macOS Native Messaging host for Chrome, Edge and Chromium. There is no installable Safari app yet.

A manifest conversion alone is not enough: Safari sends native messages through a containing macOS app, rather than Chrome's `NativeMessagingHosts` registration.

## What a port needs

1. Package the web extension in an Xcode macOS app.
2. Implement the native message handler and a controlled path to the local Python/CLI runtime.
3. Resolve App Sandbox, process-launch permissions, signing and data-directory access.
4. Adapt site permissions and dynamic content-script registration.
5. Test Option selection, cross-origin frames, scrolling, zoom and themes on Safari.

The selection UI, document parser, course index and provider adapters can be reused. The transport and installer need platform-specific work.

Start with Apple's [web extension packaging guide](https://developer.apple.com/documentation/safariservices/packaging-a-web-extension-for-safari) and [native app messaging guide](https://developer.apple.com/documentation/safariservices/messaging-a-web-extension-s-native-app). Command names and packaging flags depend on the installed Xcode version.
