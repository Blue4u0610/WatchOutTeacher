"""Build a tagged source bundle and checksum from committed files only."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def build(tag, ref, output):
    if not re.fullmatch(r'v\d+\.\d+\.\d+', tag):
        raise ValueError('Use a release tag such as v0.2.3.')
    commit = git('rev-parse', '--verify', ref+'^{commit}').decode().strip()
    version = tag[1:]
    for name in ['extension/manifest.json', 'package.json', 'package-lock.json']:
        data = json.loads(git('show', commit+':'+name))
        if data['version'] != version:
            raise ValueError(f'{name}: version does not match {tag}')
        if name == 'package-lock.json' and data['packages']['']['version'] != version:
            raise ValueError('Lockfile root package version does not match tag.')
    notes = ROOT/'docs/releases'/f'{tag}.md'
    if not notes.is_file() or not all(x in notes.read_text(encoding='utf-8') for x in ['## 中文', '## English']):
        raise ValueError(f'Missing bilingual release notes: {notes.name}')
    output.mkdir(parents=True, exist_ok=True)
    archive = output/f'WatchOutTeacher-{tag}.zip'
    prefix = f'WatchOutTeacher-{tag}/'
    subprocess.run(['git', 'archive', '--format=zip', '--prefix='+prefix, '-o', str(archive.resolve()), commit], cwd=ROOT, check=True)
    with zipfile.ZipFile(archive) as bundle:
        if bundle.testzip():
            raise ValueError('Archive integrity check failed.')
        for name in ['extension/manifest.json', 'scripts/install.py', 'bridge/host.py', 'requirements.txt']:
            if prefix+name not in bundle.namelist():
                raise ValueError(f'Missing install file: {name}')
        forbidden = {'.venv', 'node_modules', 'test-results', '.git', '.env'}
        if any(forbidden.intersection(Path(name).parts) or name.endswith(('.sqlite3', '.pem', '.key')) for name in bundle.namelist()):
            raise ValueError('Archive contains local runtime or private data.')
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    (output/'SHA256SUMS.txt').write_text(f'{digest}  {archive.name}\n', encoding='utf-8')
    (output/'release-notes.md').write_text(notes.read_text(encoding='utf-8'), encoding='utf-8')
    print(json.dumps({'tag': tag, 'commit': commit, 'archive': archive.name, 'sha256': digest}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tag', required=True)
    parser.add_argument('--ref', default='HEAD')
    parser.add_argument('--output', type=Path, default=ROOT/'dist')
    args = parser.parse_args()
    try:
        build(args.tag, args.ref, args.output)
    except (ValueError, subprocess.CalledProcessError) as exc:
        parser.exit(1, f'Release build failed: {exc}\n')
