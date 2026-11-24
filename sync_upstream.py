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


def adapt_bark_history(pending, manifest):
    target = 'ChinaMobile/sendNotify.py'
    raw = pending[target]
    text = raw.decode('utf-8')
    start = text.index('def bark(title, content):')
    end = text.index('def serverJ(', start)
    adapter = (ROOT / 'patches/bark_function.py').read_text(encoding='utf-8')
    text = text[:start] + adapter + text[end:]
    data = text.encode('utf-8')
    ast.parse(text, filename=target)
    pending[target] = data
    info = manifest['gitee:liu-long068/QL_TimingScript']['files'][target]
    info['upstream_sha256'] = info['sha256']
    info['sha256'] = hashlib.sha256(data).hexdigest()
    info['adaptation'] = 'Bark POST form, single full notification first; chunk only on explicit oversize rejection; isArchive=1, group=移动云盘, safe error diagnostics'


def adapt_workbuddy_history(pending, manifest):
    """Embed one Bark implementation without requiring extra QingLong modules."""
    helper = (ROOT / 'patches/unified_bark.py').read_text(encoding='utf-8')
    def replace_function(text, name, replacement):
        nodes = [n for n in ast.parse(text).body if isinstance(n, ast.FunctionDef) and n.name == name]
        if len(nodes) != 1:
            raise ValueError(f'Upstream notification function changed: {name}')
        node = nodes[0]
        lines = text.splitlines(keepends=True)
        return ''.join(lines[:node.lineno - 1]) + replacement + '\n' + ''.join(lines[node.end_lineno:])
    def save(repo, target, raw, text):
        ast.parse(text, filename=target)
        data = text.encode('utf-8')
        pending[target] = data
        info = manifest[repo]['files'][target]
        info['upstream_sha256'] = hashlib.sha256(raw).hexdigest()
        info['sha256'] = hashlib.sha256(data).hexdigest()
        info['adaptation'] = 'Embedded unified Bark: full single message first, history enabled, group per service; no extra dependencies'
    target = 'WorkBuddy/workbuddy_daily.py'
    raw = pending[target]
    text = replace_function(raw.decode('utf-8'), '_bark_notify',
        helper + 'def _bark_notify(title, content):\n    return _unified_bark(title, content, "WorkBuddy")\n')
    text = text.replace('def _ql_notify(title, content):', 'def _ql_notify_legacy(title, content):', 1)
    text += '\n\n' if not text.endswith('\n') else ''
    # Insert before the program entry point so all functions exist at execution time.
    wrapper = ('\ndef _ql_notify(title, content):\n'
               '    if _unified_bark_endpoint():\n'
               '        return False  # Direct Bark handles this report; prevent duplicate panel pushes.\n'
               '    return _ql_notify_legacy(title, content)\n\n')
    marker = 'if __name__ == "__main__":'
    if marker not in text:
        marker = "if __name__ == '__main__':"
    if marker not in text:
        raise ValueError('WorkBuddy entry point changed')
    text = text.replace(marker, wrapper + marker, 1)
    save('L0NE-6/WorkBuddy-Daily', target, raw, text)
    target = 'Quark/quark.py'
    raw = pending[target]
    original = raw.decode('utf-8')
    # Keep the original QingLong channel as fallback when no direct Bark is configured.
    text = original.replace('def system_notify(title: str, content: str, daily_child: bool) -> str:',
                            'def _system_notify_legacy(title: str, content: str, daily_child: bool) -> str:', 1)
    if text == original:
        raise ValueError('Quark notification signature changed')
    wrapper = (helper + 'def system_notify(title: str, content: str, daily_child: bool) -> str:\n'
               '    if daily_child:\n        return "由合集统一发送"\n'
               '    if _unified_bark_endpoint():\n'
               '        return "Bark 已发送并请求保存历史" if _unified_bark(title, content, "夸克网盘") else "Bark 发送失败"\n'
               '    return _system_notify_legacy(title, content, daily_child)\n\n')
    text = text.replace('def _system_notify_legacy(', wrapper + 'def _system_notify_legacy(', 1)
    save('GGBondHere/QingLongScripts', target, raw, text)

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
    adapt_workbuddy_history(pending, manifest)
    collect_gitee(pending, manifest)
    adapt_bark_history(pending, manifest)
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
