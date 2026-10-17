#!/usr/bin/env python3
"""Install the per-user bridge on macOS or native Windows. No administrator needed."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT/'bridge'))
from common import data_directory
from native_setup import NAME, create_launcher, register_windows, unregister_windows, write_manifest


def extension_id():
    manifest = json.loads((ROOT/'extension/manifest.json').read_text(encoding='utf-8'))
    digest = hashlib.sha256(base64.b64decode(manifest['key'])).hexdigest()[:32]
    return ''.join(chr(97+int(c,16)) for c in digest)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--uninstall', action='store_true')
    parser.add_argument('--profile', type=Path, help='macOS: register in a separate Chromium test profile')
    parser.add_argument('--data-dir', type=Path, help='Override the per-user runtime/data directory (for testing)')
    args = parser.parse_args()
    if sys.platform not in ('darwin', 'win32'):
        sys.exit('This installer supports macOS and native Windows.')
    if sys.platform == 'win32' and args.profile:
        parser.error('Windows uses per-user registry entries, not --profile.')
    data = (args.data_dir or data_directory()).expanduser().resolve()
    runtime = data/'runtime'
    if sys.platform == 'win32':
        paths = [data/f'{NAME}.json']
    else:
        bases = [args.profile] if args.profile else [Path.home()/'Library/Application Support'/p
                 for p in ['Google/Chrome', 'Microsoft Edge', 'Chromium', 'Google/ChromeForTesting']]
        paths = [p/'NativeMessagingHosts'/f'{NAME}.json' for p in bases]
    if args.uninstall:
        if sys.platform == 'win32':
            unregister_windows(paths[0])
        for path in paths:
            path.unlink(missing_ok=True)
            print('Unregistered:', path)
        print('Course data kept at:', data)
        return
    if sys.version_info < (3, 9):
        sys.exit('Python 3.9+ required. On Windows, Python 3.12 (64-bit) is recommended.')
    try:
        with sqlite3.connect(':memory:') as db:
            db.execute('CREATE VIRTUAL TABLE test USING fts5(text)')
    except sqlite3.OperationalError:
        sys.exit('Python must include SQLite FTS5. Install Python from python.org.')
    data.mkdir(parents=True, exist_ok=True, mode=0o700)
    runtime.mkdir(exist_ok=True, mode=0o700)
    shutil.copytree(ROOT/'bridge', runtime/'bridge', dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns('__pycache__', 'launch.sh', 'launcher.py', 'launcher.exe'))
    (runtime/'extension').mkdir(exist_ok=True)
    shutil.copy2(ROOT/'extension/manifest.json', runtime/'extension/manifest.json')
    python = runtime/('.venv/Scripts/python.exe' if sys.platform == 'win32' else '.venv/bin/python')
    if not python.exists():
        subprocess.run([sys.executable, '-m', 'venv', str(runtime/'.venv')], check=True)
    subprocess.run([str(python), '-m', 'pip', 'install', '-r', str(ROOT/'requirements.txt')], check=True)
    # Run using the installed interpreter so Windows distlib is available on a fresh machine.
    command = ('import sys; from pathlib import Path; sys.path.insert(0, sys.argv[1]); '
               'from native_setup import create_launcher; '
               'create_launcher(Path(sys.argv[1]), sys.executable, Path(sys.argv[2]), Path(sys.argv[3]))')
    subprocess.run([str(python), '-c', command, str(runtime/'bridge'), str(runtime/'bridge/host.py'), str(data)], check=True)
    launcher = runtime/'bridge'/('launcher.exe' if sys.platform == 'win32' else 'launch.sh')
    eid = extension_id()
    for path in paths:
        write_manifest(path, launcher, eid)
    if sys.platform == 'win32':
        register_windows(paths[0])
    for path in paths:
        print('Registered:', path)
    print('Extension ID:', eid)
    print('Load unpacked extension:', ROOT/'extension')
    print('Bridge installed. The browser starts it on demand; no background server needed.')


if __name__ == '__main__':
    try:
        main()
    except (OSError, subprocess.CalledProcessError) as error:
        sys.exit(f'Installation failed: {error}\nClose extension pages, disable the extension, and retry.')
