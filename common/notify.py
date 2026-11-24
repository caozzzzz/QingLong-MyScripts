"""Shared Bark sender for the three services. No credentials stored here."""
import json
import os
import requests

def _parts(content, budget=2000):
    """Bound JSON-escaped UTF-8 bytes, leaving room for APNs metadata."""
    parts, current, size = [], [], 0
    for char in str(content):
        cost = len(json.dumps(char, ensure_ascii=False)[1:-1].encode('utf-8'))
        if current and size + cost > budget:
            parts.append(''.join(current))
            current, size = [], 0
        current.append(char)
        size += cost
    if current or not parts:
        parts.append(''.join(current))
    return parts


def _send_request(endpoint, title, body, label, group):
    payload = {'title': str(title)[:80], 'body': str(body),
               'isArchive': '1', 'group': group}
    try:
        response = requests.post(endpoint, data=payload, timeout=(10, 30))
        try:
            result = response.json()
        except ValueError:
            result = {}
        if not isinstance(result, dict):
            result = {}
        code = result.get('code')
        if response.status_code == 200 and code == 200:
            return 'ok'
        # Only an explicit size rejection permits a second attempt as chunks.
        reason = str(result.get('message', '')) + ' ' + str(result.get('msg', ''))
        lower = reason.lower()
        oversized = response.status_code == 413 or code == 413 or any(
            marker in lower for marker in
            ('payloadtoolarge', 'payload too large', 'request entity too large',
             'message too large', '消息过大', '消息太大', '消息体过大'))
        if oversized:
            print(f'Bark {label} 明确返回消息过大，尝试分段')
            return 'oversized'
        safe_code = str(code) if isinstance(code, (int, float)) else '未知'
        print(f'Bark {label} 推送失败：HTTP {response.status_code}，业务码 {safe_code}；未重试')
    except Exception as error:
        # A timeout has an uncertain delivery outcome: do not resend automatically.
        print(f'Bark {label} 推送失败：{type(error).__name__}（地址及密钥已隐藏）；未重试')
    return 'failed'


def _endpoint():
    key = os.environ.get('BARK', '').strip()
    if key:
        return 'https://api.day.app/' + key.strip('/')
    return (os.environ.get('BARK_URL', '').strip() or
            os.environ.get('BARK_PUSH', '').strip()).rstrip('/')


def send(title, content, group):
    endpoint = _endpoint()
    if not endpoint:
        return False
    outcome = _send_request(endpoint, title, content, group, group)
    if outcome == 'ok':
        print(f'Bark {group} 推送成功：完整 1 条，已请求保存历史记录')
        return True
    if outcome != 'oversized':
        return False
    parts = _parts(content)
    if len(parts) == 1:
        return False
    succeeded = 0
    for index, body in enumerate(parts, 1):
        chunk_title = str(title)[:60] + f' ({index}/{len(parts)})'
        if _send_request(endpoint, chunk_title, body, group, group) == 'ok':
            succeeded += 1
    print(f'Bark {group} 分段推送完成：{succeeded}/{len(parts)} 条成功')
    return succeeded == len(parts)



def configured():
    return bool(_endpoint())
