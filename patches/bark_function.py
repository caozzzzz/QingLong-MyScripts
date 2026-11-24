# Local Bark adaptation for China Mobile Cloud; inserted by sync_upstream.py.
def _bark_parts(content, budget=2000):
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


def bark(title, content):
    endpoints = []
    if BARK:
        endpoints.append(('官方', 'https://api.day.app/' + BARK.strip().strip('/')))
    if BARK_PUSH:
        endpoints.append(('自建', BARK_PUSH.strip().rstrip('/')))
    if not endpoints:
        print('Bark 未配置，跳过推送')
        return
    parts = _bark_parts(content)
    for label, endpoint in endpoints:
        succeeded = 0
        for index, body in enumerate(parts, 1):
            suffix = f' ({index}/{len(parts)})' if len(parts) > 1 else ''
            payload = {
                'title': str(title)[:80] + suffix, 'body': body,
                'isArchive': '1', 'group': '移动云盘',
            }
            try:
                response = requests.post(endpoint, data=payload, timeout=(10, 30))
                try:
                    result = response.json()
                except ValueError:
                    print(f'Bark {label} 第{index}条失败：HTTP {response.status_code}，响应非 JSON')
                    continue
                if response.status_code == 200 and result.get('code') == 200:
                    succeeded += 1
                    continue
                # Do not log request URLs, keys, raw responses, or exception text.
                code = result.get('code')
                safe_code = str(code) if isinstance(code, (int, float)) else '未知'
                print(f'Bark {label} 第{index}条失败：HTTP {response.status_code}，业务码 {safe_code}')
            except Exception as error:
                print(f'Bark {label} 第{index}条失败：{type(error).__name__}（地址及密钥已隐藏）')
        print(f'Bark {label} 推送完成：{succeeded}/{len(parts)} 条成功，已请求保存历史记录')


