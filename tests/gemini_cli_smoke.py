"""Offline native CLI contract check. --install downloads the pinned official release in CI."""
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
import zipfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'bridge'))
from gemini import TESTED_VERSION, command

with tempfile.TemporaryDirectory(prefix='watchoutteacher-cli-check-') as d:
    if '--install' in sys.argv:
        system={'Darwin':'mac','Windows':'windows'}[platform.system()]
        arch='arm64' if platform.machine().lower() in ['arm64','aarch64'] else 'x64'
        suffix='zip' if system=='windows' else 'tar.gz'
        asset=f'agy_cli_{system}_{arch}.{suffix}'
        url=f'https://github.com/google-antigravity/antigravity-cli/releases/download/{TESTED_VERSION}/{asset}'
        data=urllib.request.urlopen(url,timeout=120).read()
        executable=Path(d)/('agy.exe' if system=='windows' else 'agy')
        if suffix=='zip':
            with zipfile.ZipFile(io.BytesIO(data)) as archive:
                names=[n for n in archive.namelist() if Path(n).name=='antigravity.exe']
                assert len(names)==1,names
                executable.write_bytes(archive.read(names[0]))
        else:
            with tarfile.open(fileobj=io.BytesIO(data),mode='r:gz') as archive:
                members=[m for m in archive.getmembers() if m.isfile() and Path(m.name).name=='antigravity']
                assert len(members)==1
                executable.write_bytes(archive.extractfile(members[0]).read())
        executable.chmod(0o700)
        cmd=[str(executable)]
        digest=hashlib.sha256(data).hexdigest()
    else:
        cmd=command();digest=None
    assert cmd,'Install Antigravity CLI 1.4.2 first'
    def run(args):
        result=subprocess.run(cmd+args,cwd=d,capture_output=True,text=True,check=True,timeout=15)
        return result.stdout+result.stderr
    assert run(['--version']).strip()==TESTED_VERSION
    helptext=run(['--help'])
    for flag in ['--agent','--input-format','--output-format','--disable-slash-commands','--model','--log-file']:
        assert flag in helptext,flag
    evidence={'cli':TESTED_VERSION,'platform':platform.system(),'archive_sha256':digest,'flags_verified':True,'uses_account':False}
    target=Path('test-results/gemini-cli-smoke.json');target.parent.mkdir(exist_ok=True)
    target.write_text(json.dumps(evidence,indent=2),encoding='utf-8');print(json.dumps(evidence))
