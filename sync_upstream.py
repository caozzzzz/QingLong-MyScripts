"""Sync an explicit allowlist; never execute downloaded scripts."""
import ast
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
SOURCES = {
    'GGBondHere/QingLongScripts': {
        'scripts/quark.py': 'quark.py',
        'docs/quark.md': 'upstream/quark.md',
        'LICENSE': 'licenses/QingLongScripts-LICENSE',
    },
    'L0NE-6/WorkBuddy-Daily': {
        'workbuddy_daily.py': 'workbuddy_daily.py',
        'workbuddy_login.py': 'workbuddy_login.py',
        'LICENSE': 'licenses/WorkBuddy-Daily-LICENSE',
        'NOTICE.md': 'upstream/WorkBuddy-NOTICE.md',
    },
}

def get(url):
    with urlopen(Request(url, headers={'User-Agent': 'QingLong-MyScripts-sync'}), timeout=60) as response:
        return response.read()

def main():
    pending, manifest = {}, {}
    for repo, files in SOURCES.items():
        sha = json.loads(get(f'https://api.github.com/repos/{repo}/commits/main'))['sha']
        manifest[repo] = {'commit': sha, 'files': {}}
        for source, target in files.items():
            data = get(f'https://raw.githubusercontent.com/{repo}/{sha}/{source}')
            if not data.strip():
                raise ValueError(f'Empty upstream file: {repo}/{source}')
            if target.endswith('.py'):
                ast.parse(data.decode('utf-8-sig'), filename=target)
            pending[target] = data
            manifest[repo]['files'][target] = {'source': source, 'sha256': hashlib.sha256(data).hexdigest()}
    pending['upstream/manifest.json'] = (json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode()
    pending['requirements.txt'] = b'requests\n'
    pending['.gitignore'] = b'__pycache__/\n*.pyc\n.env\nwb_*.json\nWORKBUDDY_ACCESS_TOKEN.txt\nworkbuddy_*state*.json\nworkbuddy_sign_retry.json\n'
    for target, data in pending.items():
        path = ROOT / target
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    print('Synced Quark and WorkBuddy domestic scripts. Upstream commits recorded.')

if __name__ == '__main__':
    main()
