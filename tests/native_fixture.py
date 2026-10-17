"""Create a unique host registration; never replace the user's production host."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'bridge'))
from native_setup import create_launcher, write_manifest, register_windows, unregister_windows

operation, profile, name, eid, mode = sys.argv[1:]
profile = Path(profile)
manifest = profile/'NativeMessagingHosts'/f'{name}.json'
if operation == 'install':
    entry = profile/'runtime'/('bridge/host.py' if mode == 'live' else 'tests/mock_host.py')
    launcher = create_launcher(profile/'launcher', sys.executable, entry, profile/'data')
    write_manifest(manifest, launcher, eid, name)
    if sys.platform == 'win32':
        register_windows(manifest, name)
elif sys.platform == 'win32':
    unregister_windows(manifest, name)
