"""Sync an explicit allowlist; never execute downloaded scripts."""
import ast
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
SOURCES = {
    'GGBondHere/QingLongScripts': {
        'scripts/quark.py': 'Quark/quark.py',
        'docs/quark.md': 'upstream/quark.md',
        'LICENSE': 'licenses/QingLongScripts-LICENSE',
    },
    'L0NE-6/WorkBuddy-Daily': {
        'workbuddy_daily.py': 'WorkBuddy/workbuddy_daily.py',
        'workbuddy_login.py': 'WorkBuddy/workbuddy_login.py',
        'LICENSE': 'licenses/WorkBuddy-Daily-LICENSE',
        'NOTICE.md': 'upstream/WorkBuddy-NOTICE.md',
    },
}

GITEE_REPO = 'https://gitee.com/liu-long068/QL_TimingScript.git'
GITEE_FILES = {
    '中国移动云盘.py': 'ChinaMobile/中国移动云盘.py',
    'log.py': 'ChinaMobile/log.py',
    'get_env.py': 'ChinaMobile/get_env.py',
    'sendNotify.py': 'ChinaMobile/sendNotify.py',
    'README.md': 'upstream/QL_TimingScript-README.md',
}

def collect_gitee(pending, manifest, checkout=None):
    def collect(folder):
        sha = subprocess.check_output(['git', '-C', str(folder), 'rev-parse', 'HEAD'], text=True).strip()
        record = {'url': GITEE_REPO, 'branch': 'master', 'commit': sha, 'files': {}}
        for source, target in GITEE_FILES.items():
            data = subprocess.check_output(['git', '-C', str(folder), 'show', f'{sha}:{source}'])
            if not data.strip():
                raise ValueError(f'Empty upstream file: {source}')
            if target.endswith('.py'):
                ast.parse(data.decode('utf-8-sig'), filename=target)
            pending[target] = data
            record['files'][target] = {'source': source, 'sha256': hashlib.sha256(data).hexdigest()}
        manifest['gitee:liu-long068/QL_TimingScript'] = record
    if checkout is not None:
        collect(checkout)
    else:
        with tempfile.TemporaryDirectory(prefix='ql-mobile-') as temp:
            subprocess.run(['git', 'clone', '--depth', '1', '--branch', 'master', '--single-branch', GITEE_REPO, temp], check=True, timeout=180)
            collect(temp)

def get(url):
    with urlopen(Request(url, headers={'User-Agent': 'QingLong-MyScripts-sync'}), timeout=60) as response:
        return response.read()

def main():
    pending, manifest = {}, {}
    for repo, files in SOURCES.items():
        sha = subprocess.check_output(['git', 'ls-remote', f'https://github.com/{repo}.git', 'refs/heads/main'], text=True, timeout=60).split()[0]
        manifest[repo] = {'commit': sha, 'files': {}}
        for source, target in files.items():
            data = get(f'https://raw.githubusercontent.com/{repo}/{sha}/{source}')
            if not data.strip():
                raise ValueError(f'Empty upstream file: {repo}/{source}')
            if target.endswith('.py'):
                ast.parse(data.decode('utf-8-sig'), filename=target)
            pending[target] = data
            manifest[repo]['files'][target] = {'source': source, 'sha256': hashlib.sha256(data).hexdigest()}
    collect_gitee(pending, manifest)
    pending['upstream/manifest.json'] = (json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode()
    pending['requirements.txt'] = b'requests\nhttpx\npython-dotenv\n'
    pending['.gitignore'] = b'__pycache__/\n*.pyc\n.env\nwb_*.json\nWORKBUDDY_ACCESS_TOKEN.txt\nworkbuddy_*state*.json\nworkbuddy_sign_retry.json\n'
    for target, data in pending.items():
        path = ROOT / target
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    for old, new in [('quark.py', 'Quark/quark.py'), ('workbuddy_daily.py', 'WorkBuddy/workbuddy_daily.py'), ('workbuddy_login.py', 'WorkBuddy/workbuddy_login.py')]:
        if (ROOT / new).is_file():
            (ROOT / old).unlink(missing_ok=True)
    print('Synced Quark, WorkBuddy domestic and China Mobile Cloud. Upstream commits recorded.')

if __name__ == '__main__':
    main()
