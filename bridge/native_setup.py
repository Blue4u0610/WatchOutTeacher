"""Native host registration shared by the installer and isolated integration tests."""
import json
import os
from pathlib import Path
import shlex
import sys

NAME = 'com.courseassist.bridge'
WINDOWS_BROWSERS = ('Google\\Chrome', 'Microsoft\\Edge', 'Chromium', 'Google\\ChromeForTesting')


def create_launcher(directory, python, entry_script, data):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    if sys.platform == 'win32':
        from distlib.scripts import ScriptMaker
        source = directory/'launcher.py'
        source.write_text(
            '#!python\nimport os, runpy, sys\n'
            + f'os.environ["COURSE_ASSIST_DATA"] = {str(data)!r}\n'
            + 'os.environ["PYTHONUTF8"] = "1"\n'
            + f'sys.path.insert(0, {str(Path(entry_script).parent)!r})\n'
            + f'runpy.run_path({str(entry_script)!r}, run_name="__main__")\n', encoding='utf-8')
        maker = ScriptMaker(str(directory), str(directory))
        maker.executable = str(python)
        maker.clobber = True
        maker.force = True
        maker.make('launcher.py')
        return directory/'launcher.exe'
    launcher = directory/'launch.sh'
    launcher.write_text('#!/bin/sh\nexport COURSE_ASSIST_DATA='+shlex.quote(str(data))+
                        '\nexec '+shlex.quote(str(python))+' '+shlex.quote(str(entry_script))+' "$@"\n', encoding='utf-8')
    launcher.chmod(0o700)
    return launcher


def registry_key(browser, name):
    return 'Software\\'+browser+'\\NativeMessagingHosts\\'+name


def register_windows(manifest, name=NAME):
    import winreg
    for browser in WINDOWS_BROWSERS:
        with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, registry_key(browser, name), 0,
                               winreg.KEY_SET_VALUE | winreg.KEY_WOW64_64KEY) as key:
            winreg.SetValueEx(key, '', 0, winreg.REG_SZ, str(Path(manifest).resolve()))


def unregister_windows(manifest, name=NAME):
    import winreg
    for browser in WINDOWS_BROWSERS:
        key_path = registry_key(browser, name)
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0,
                                winreg.KEY_READ | winreg.KEY_WOW64_64KEY) as key:
                value, _ = winreg.QueryValueEx(key, '')
            # Do not unregister an entry now owned by a different installation.
            if os.path.normcase(value) == os.path.normcase(str(Path(manifest).resolve())):
                winreg.DeleteKeyEx(winreg.HKEY_CURRENT_USER, key_path, winreg.KEY_WOW64_64KEY)
        except FileNotFoundError:
            pass


def write_manifest(path, launcher, extension_id, name=NAME):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({'name':name, 'description':'WatchOutTeacher local CLI bridge',
        'path':str(Path(launcher).resolve()), 'type':'stdio',
        'allowed_origins':[f'chrome-extension://{extension_id}/']}, indent=2), encoding='utf-8')
    path.chmod(0o600)
