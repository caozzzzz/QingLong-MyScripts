import ast
import contextlib
import importlib.util
import io
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('shared_notification_test', ROOT / 'common/notify.py')
notify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(notify)


class CommonNotificationTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {'BARK': 'dummy-key', 'BARK_URL': '', 'BARK_PUSH': ''})
        self.env.start()
        self.addCleanup(self.env.stop)

    @staticmethod
    def response(status=200, code=200, message=''):
        result = Mock(status_code=status)
        result.json.return_value = {'code': code, 'message': message}
        return result

    def test_long_report_is_one_complete_archived_message(self):
        content = '中文😀\n' * 1500
        with patch('requests.post', return_value=self.response()) as post:
            self.assertTrue(notify.send('签到', content, 'WorkBuddy'))
        post.assert_called_once()
        data = post.call_args.kwargs['data']
        self.assertEqual(data['body'], content)
        self.assertEqual(data['isArchive'], '1')
        self.assertEqual(data['group'], 'WorkBuddy')

    def test_split_only_after_explicit_size_rejection(self):
        content = '中文😀\n' * 1500
        parts = notify._parts(content)
        responses = [self.response(413, 413)] + [self.response() for _ in parts]
        with patch('requests.post', side_effect=responses) as post:
            self.assertTrue(notify.send('签到', content, '移动云盘'))
        self.assertEqual(post.call_count, 1 + len(parts))
        self.assertEqual(''.join(c.kwargs['data']['body'] for c in post.call_args_list[1:]), content)

    def test_uncertain_failure_not_resent_and_secret_not_logged(self):
        output = io.StringIO()
        with patch('requests.post', side_effect=TimeoutError('https://api.day.app/dummy-key')) as post, contextlib.redirect_stdout(output):
            self.assertFalse(notify.send('签到', '正文', '夸克网盘'))
        post.assert_called_once()
        self.assertNotIn('dummy-key', output.getvalue())
        with patch('requests.post', return_value=self.response(403, 403)) as post:
            self.assertFalse(notify.send('签到', '正文', '夸克网盘'))
        post.assert_called_once()

    def service_namespace(self, relative):
        path = ROOT / relative
        tree = ast.parse(path.read_bytes())
        functions = {'_load_common_notify', '_bark_notify', '_ql_notify', 'system_notify', 'send_notification_message_collection'}
        nodes = [n for n in tree.body if (isinstance(n, ast.FunctionDef) and n.name in functions) or
                 (isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == '_common_notify_cache' for t in n.targets))]
        fallback = Mock(return_value='panel')
        ns = {'__file__': str(path), '_ql_notify_legacy': fallback, '_system_notify_legacy': fallback,
              'QLAPI': Mock(), 'log': Mock(all_print_list=['第一行\n', '第二行'])}
        exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), 'exec'), ns)
        return ns, fallback

    def test_all_services_use_same_physical_module_from_other_cwd(self):
        cases = [('WorkBuddy/workbuddy_daily.py', 'WorkBuddy'), ('Quark/quark.py', '夸克网盘'),
                 ('ChinaMobile/中国移动云盘.py', '移动云盘')]
        old_cwd = Path.cwd()
        temp_dir = tempfile.TemporaryDirectory()
        try:
            os.chdir(temp_dir.name)
            for relative, group in cases:
                with self.subTest(service=group):
                    ns, fallback = self.service_namespace(relative)
                    with patch('requests.post', return_value=self.response()) as post:
                        if group == 'WorkBuddy':
                            self.assertTrue(ns['_bark_notify']('签到', '正文'))
                            self.assertFalse(ns['_ql_notify']('签到', '正文'))
                        elif group == '夸克网盘':
                            self.assertIn('已发送', ns['system_notify']('签到', '正文', False))
                            self.assertEqual(ns['system_notify']('签到', '正文', True), '由合集统一发送')
                        else:
                            self.assertTrue(ns['send_notification_message_collection']('签到'))
                            self.assertEqual(post.call_args.kwargs['data']['body'], '第一行\n第二行')
                    post.assert_called_once()
                    self.assertEqual(post.call_args.kwargs['data']['group'], group)
                    self.assertEqual(Path(ns['_load_common_notify']().__file__), ROOT / 'common/notify.py')
                    fallback.assert_not_called()
                    ns['QLAPI'].systemNotify.assert_not_called()
        finally:
            os.chdir(old_cwd)
            temp_dir.cleanup()

    def test_panel_fallback_without_bark(self):
        with patch.dict(os.environ, {'BARK': '', 'BARK_URL': '', 'BARK_PUSH': ''}):
            ns, fallback = self.service_namespace('WorkBuddy/workbuddy_daily.py')
            self.assertEqual(ns['_ql_notify']('title', 'body'), 'panel')
            ns, fallback = self.service_namespace('Quark/quark.py')
            self.assertEqual(ns['system_notify']('title', 'body', False), 'panel')

    def test_missing_common_module_has_actionable_message(self):
        ns, _ = self.service_namespace('Quark/quark.py')
        with tempfile.TemporaryDirectory() as temp:
            ns['__file__'] = str(Path(temp) / 'Quark/quark.py')
            with self.assertRaisesRegex(RuntimeError, 'common/notify.py'):
                ns['_load_common_notify']()


if __name__ == '__main__':
    unittest.main()
