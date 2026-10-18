"""Cross-platform regressions, with real Windows jobs and launchers in Windows CI."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch
import psutil
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'bridge'))
from common import AppError, data_directory
from host import encode_frame, read_frame, extension_origin
from native_setup import create_launcher, write_manifest, register_windows, unregister_windows, WINDOWS_BROWSERS, registry_key
from providers import environment, locate, run, CLIProvider

ROOT = Path(__file__).resolve().parents[1]


class PlatformTests(unittest.TestCase):
    def test_environment_preserves_auth_location_but_not_billing_or_python_overrides(self):
        with patch.dict(os.environ, {'OPENAI_API_KEY':'secret', 'ANTHROPIC_API_KEY':'secret',
                                    'PYTHONPATH':'untrusted', 'PYTHONHOME':'untrusted'}):
            env = environment()
        for key in ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'PYTHONPATH', 'PYTHONHOME']:
            self.assertNotIn(key, env)
        self.assertEqual(env['PYTHONUTF8'], '1')
        if sys.platform == 'win32':
            self.assertEqual(env['USERPROFILE'], os.environ['USERPROFILE'])
            self.assertEqual(env['SystemRoot'], os.environ['SystemRoot'])
            self.assertEqual(data_directory().parent, Path(os.environ['LOCALAPPDATA']))

    def test_mac_desktop_claude_discovery_prefers_path_then_newest_native_version(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            root = home/'Library/Application Support/Claude/claude-code'
            for version in ['2.1.9','2.1.299','preview']:
                exe = root/version/'hash/claude.app/Contents/MacOS/claude'
                exe.parent.mkdir(parents=True); exe.write_text('test'); exe.chmod(0o700)
            with patch('providers.sys.platform','darwin'), patch('providers.Path.home',return_value=home), patch('providers.shutil.which',return_value=None):
                self.assertIn('2.1.299',Path(locate('claude')).parts)
                self.assertIsNone(locate('codex'))
                with patch('providers.shutil.which',return_value='/trusted/claude'):
                    self.assertEqual(locate('claude'),'/trusted/claude')

    def test_claude_detection_reports_authentication_without_account_details(self):
        flags = '--print --output-format --json-schema --tools --no-session-persistence --strict-mcp-config --setting-sources --settings --model --disable-slash-commands --no-chrome --safe-mode'
        for logged_in in [True,False]:
            with patch('providers.locate',return_value='/trusted/claude'), patch('providers.run',side_effect=['2.1.299',flags,json.dumps({'loggedIn':logged_in,'email':'private@example.com'})]):
                status = CLIProvider('claude').detect()
                self.assertEqual(status['available'],logged_in)
                self.assertEqual(status['code'],'ready' if logged_in else 'auth')
                self.assertEqual(status['version'],'2.1.299')
                self.assertNotIn('private@example.com',json.dumps(status))

    def test_unicode_stdin_stdout_and_path_with_spaces(self):
        with tempfile.TemporaryDirectory(prefix='课程 space ') as directory:
            prompt = '中文\nline two\r\nemoji: 🙂'
            output = run([sys.executable, '-c', 'import sys; sys.stdout.buffer.write(sys.stdin.buffer.read())'], directory, prompt)
            self.assertEqual(output, prompt)
            file = Path(directory)/'讲义.md'
            file.write_text('Lumen 就绪颜色是 Violet。', encoding='utf-8')
            result = json.loads(run([sys.executable, str(ROOT/'bridge/parser.py'), str(file), '.md'], directory, memory_limit=1024**3))
            self.assertTrue(result['ok'])
            self.assertIn('就绪', result['data']['units'][0]['text'])

    def test_cli_arguments_are_not_shell_interpreted(self):
        with tempfile.TemporaryDirectory() as directory:
            arguments = ['', '{"mcpServers":{}}', 'a path with spaces', '中文', 'x&echo bad', '%TEMP%']
            output = run([sys.executable, '-c', 'import json,sys; print(json.dumps(sys.argv[1:]))', *arguments], directory)
            self.assertEqual(json.loads(output), arguments)

    def test_parent_exit_also_cleans_descendants(self):
        with tempfile.TemporaryDirectory() as directory:
            pidfile = Path(directory)/'child.pid'
            child = 'import time; time.sleep(30)'
            script = ('import subprocess, sys; from pathlib import Path; '
                      f'p=subprocess.Popen([sys.executable,"-c",{child!r}]); '
                      f'Path({str(pidfile)!r}).write_text(str(p.pid)); print("ready")')
            self.assertIn('ready', run([sys.executable, '-c', script], directory))
            pid = int(pidfile.read_text())
            def alive():
                try:
                    return psutil.Process(pid).status() != psutil.STATUS_ZOMBIE
                except psutil.NoSuchProcess:
                    return False
            try:
                deadline = time.monotonic()+3
                while alive() and time.monotonic()<deadline:
                    time.sleep(.05)
                self.assertFalse(alive(), 'descendant survived process cleanup')
            finally:
                try: psutil.Process(pid).kill()
                except psutil.NoSuchProcess: pass

    def test_native_launcher_roundtrip_and_origin_rejection(self):
        with tempfile.TemporaryDirectory(prefix='桥接 space ') as directory:
            directory = Path(directory)
            launcher = create_launcher(directory/'启动器', sys.executable, ROOT/'bridge/host.py', directory/'资料')
            messages = b''.join(encode_frame(m) for m in [
                {'id':'1','op':'course_create','payload':{'name':'课程\nViolet 🙂'}},
                {'id':'2','op':'state','payload':{}}])
            result = subprocess.run([str(launcher), extension_origin()], input=messages, capture_output=True, timeout=15)
            self.assertEqual(result.returncode, 0, result.stderr.decode('utf-8','replace'))
            import io
            output = io.BytesIO(result.stdout)
            replies = [read_frame(output), read_frame(output)]
            self.assertTrue(all(r['ok'] for r in replies), replies)
            self.assertTrue(all(r['data']['courses'][0]['name']=='课程\nViolet 🙂' for r in replies))
            self.assertIsNone(read_frame(output))
            bad = subprocess.run([str(launcher), 'chrome-extension://wrong/'], capture_output=True, timeout=15)
            self.assertNotEqual(bad.returncode, 0)
            self.assertEqual(bad.stdout, b'')

    @unittest.skipUnless(sys.platform == 'win32', 'Windows registry and native executables')
    def test_windows_registry_lifecycle_and_native_only_discovery(self):
        import uuid
        import winreg
        name = 'com.courseassist.test.h'+uuid.uuid4().hex
        with tempfile.TemporaryDirectory(prefix='中文 tools ') as directory:
            directory = Path(directory)
            manifest = directory/'host.json'
            write_manifest(manifest, directory/'launcher.exe', 'a'*32, name)
            try:
                register_windows(manifest, name)
                for browser in WINDOWS_BROWSERS:
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, registry_key(browser,name), 0,
                                        winreg.KEY_READ | winreg.KEY_WOW64_64KEY) as key:
                        self.assertEqual(winreg.QueryValueEx(key, '')[0], str(manifest.resolve()))
            finally:
                unregister_windows(manifest, name)
            for browser in WINDOWS_BROWSERS:
                with self.assertRaises(FileNotFoundError):
                    winreg.OpenKey(winreg.HKEY_CURRENT_USER, registry_key(browser,name), 0,
                                   winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
            (directory/'codex.cmd').write_text('@echo should never execute')
            with patch('providers.environment', return_value={'PATH':str(directory)}):
                self.assertIsNone(locate('codex'))
                (directory/'codex.exe').touch()
                self.assertEqual(locate('codex'), str(directory/'codex.exe'))

    @unittest.skipUnless(sys.platform == 'win32', 'Windows job memory limit')
    def test_windows_parser_memory_limit(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(AppError):
                run([sys.executable, '-c', 'data=bytearray(256*1024*1024)'], directory,
                    memory_limit=128*1024*1024, timeout=5)


if __name__ == '__main__':
    unittest.main()
