"""Installer lifecycle on disposable CI machines only (uses production registration)."""
import io
import os
from pathlib import Path
import subprocess
import sys
import tempfile
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'bridge'))
from host import encode_frame, read_frame, extension_origin
from native_setup import NAME, WINDOWS_BROWSERS, registry_key

if os.environ.get('CI') != 'true':
    sys.exit('This installer test is only for disposable CI machines.')
ROOT = Path(__file__).resolve().parents[1]
if sys.platform == 'win32':
    import winreg
    for browser in WINDOWS_BROWSERS:
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, registry_key(browser, NAME))
        except FileNotFoundError:
            continue
        key.Close()
        sys.exit('Refusing to replace an existing host registration.')
with tempfile.TemporaryDirectory(prefix='安装 test ') as folder:
    folder = Path(folder)
    data = folder/'数据 space'
    command = [sys.executable, str(ROOT/'scripts/install.py'), '--data-dir', str(data)]
    if sys.platform != 'win32':
        command += ['--profile', str(folder/'profile')]
    try:
        subprocess.run(command, check=True)
        launcher = data/'runtime/bridge'/('launcher.exe' if sys.platform=='win32' else 'launch.sh')
        def rpc(op, payload):
            result = subprocess.run([str(launcher), extension_origin()], input=encode_frame({'id':'t','op':op,'payload':payload}), capture_output=True, timeout=15, check=True)
            reply = read_frame(io.BytesIO(result.stdout))
            assert reply['ok'], reply
            return reply['data']
        rpc('course_create', {'name':'更新后保留'})
        rpc('settings', {'codex_effort':'high'})
        subprocess.run(command, check=True)
        state = rpc('state', {})
        assert state['courses'][0]['name']=='更新后保留'
        assert state['settings']['codex_effort']=='high'
    finally:
        subprocess.run(command+['--uninstall'], check=True)
    assert (data/'courses.sqlite3').exists(), 'Uninstall must preserve courses'
    if sys.platform == 'win32':
        assert not (data/f'{NAME}.json').exists()
        for browser in WINDOWS_BROWSERS:
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, registry_key(browser, NAME))
            except FileNotFoundError:
                continue
            key.Close()
            raise AssertionError('Registry entry survived uninstall')
print('PASS installer / Unicode paths / reinstall preserves data / uninstall')
