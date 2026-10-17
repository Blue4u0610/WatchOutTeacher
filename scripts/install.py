#!/usr/bin/env python3
"""Register the bridge only for this extension's pinned public-key identity."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parent.parent
NAME='com.courseassist.bridge'

def extension_id():
    manifest=json.loads((ROOT/'extension/manifest.json').read_text())
    digest=hashlib.sha256(base64.b64decode(manifest['key'])).hexdigest()[:32]
    return ''.join(chr(97+int(c,16)) for c in digest)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--uninstall',action='store_true')
    parser.add_argument('--profile',type=Path,help='Register in a separate Chromium test profile only')
    args=parser.parse_args()
    if sys.platform!='darwin': sys.exit('此安装器面向 macOS。')
    data=Path.home()/'Library/Application Support/CourseAssist'
    bases=[args.profile] if args.profile else [Path.home()/'Library/Application Support'/p for p in ['Google/Chrome','Microsoft Edge','Chromium','Google/ChromeForTesting']]
    paths=[p/'NativeMessagingHosts'/f'{NAME}.json' for p in bases]
    if args.uninstall:
        for p in paths:
            if p.exists(): p.unlink(); print('已注销',p)
        print('课程资料仍保留在',data)
        return
    data.mkdir(parents=True,exist_ok=True,mode=0o700)
    runtime=data/'runtime'
    runtime.mkdir(exist_ok=True,mode=0o700)
    shutil.copytree(ROOT/'bridge',runtime/'bridge',dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','launch.sh'))
    (runtime/'extension').mkdir(exist_ok=True)
    shutil.copy2(ROOT/'extension/manifest.json',runtime/'extension/manifest.json')
    py=runtime/'.venv/bin/python'
    if not py.exists(): subprocess.run([sys.executable,'-m','venv',str(runtime/'.venv')],check=True)
    subprocess.run([str(py),'-m','pip','install','-r',str(ROOT/'requirements.txt')],check=True)
    launcher=runtime/'bridge/launch.sh'
    path=os.pathsep.join([str(Path.home()/'.local/bin'),'/opt/homebrew/bin','/usr/local/bin','/usr/bin','/bin'])
    launcher.write_text('#!/bin/sh\nexport PATH='+shlex.quote(path)+'\nexec '+shlex.quote(str(py))+' '+shlex.quote(str(runtime/'bridge/host.py'))+' "$@"\n')
    launcher.chmod(0o700)
    eid=extension_id()
    manifest={'name':NAME,'description':'WatchOutTeacher local CLI bridge','path':str(launcher),'type':'stdio','allowed_origins':[f'chrome-extension://{eid}/']}
    for p in paths:
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(json.dumps(manifest,indent=2)); p.chmod(0o600); print('已注册',p)
    print('扩展 ID:',eid)
    print('加载扩展目录:',ROOT/'extension')
    print('浏览器将按需启动桥接，无需常驻服务。')

if __name__=='__main__': main()
