"""Synthetic one-site recon; zero network calls or real captures."""
import copy
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from core import APIError
from recon_deadsimplechat import documented_recon, summarize_har

SECRET = 'SYNTHETIC-PRIVATE-DO-NOT-RETAIN'


def sample():
    return {'log': {'entries': [{
        'request': {'method': 'POST',
                    'url': 'https://api.deadsimplechat.com/consumer/api/v2/bot/' + SECRET + '/chatroom/' + SECRET + '/message?auth=' + SECRET,
                    'headers': [{'name': 'Authorization', 'value': SECRET}, {'name': 'Cookie', 'value': SECRET}],
                    'postData': {'text': SECRET}, 'cookies': [{'value': SECRET}]},
        'response': {'status': 200, 'headers': [{'name': 'Set-Cookie', 'value': SECRET}],
                     'content': {'text': SECRET}, 'cookies': [{'value': SECRET}]},
        '_webSocketMessages': [{'data': SECRET}]}]}}


class ReconTests(unittest.TestCase):
    def test_documented_contract_separates_ambiguity_and_live_readiness(self):
        data = documented_recon()
        self.assertEqual(data['site'], 'deadsimplechat')
        self.assertEqual(data['documented']['send']['message_max_characters'], 1000)
        self.assertFalse(data['documented']['receive']['unique_click_occurrence_id_established'])
        self.assertTrue(data['unresolved'])
        self.assertEqual(data['external_requests'], 0)
        self.assertFalse(data['live_ready'])

    def test_saved_documented_recon_matches_runnable_output(self):
        source = Path(__file__).resolve().parents[1] / 'data/deadsimplechat_recon.json'
        self.assertEqual(json.loads(source.read_text()), documented_recon())

    def test_private_values_never_echoed_and_http200_not_acceptance(self):
        data = summarize_har(sample())
        self.assertNotIn(SECRET, json.dumps(data))
        row = data['records'][0]
        self.assertTrue(row['auth_query_present'])
        self.assertTrue(row['authorization_header_present'])
        self.assertEqual(row['api_acceptance'], 'unverified')
        self.assertFalse(data['auth_requirement_resolved'])
        self.assertEqual(data['messages_sent'], 0)

    def test_querystring_metadata_and_case_insensitive_header_names(self):
        value = sample()
        req = value['log']['entries'][0]['request']
        req['url'] = req['url'].split('?')[0]
        req['queryString'] = [{'name': 'auth', 'value': SECRET}]
        req['headers'][0]['name'] = 'aUtHoRiZaTiOn'
        result = summarize_har(value)['records'][0]
        self.assertTrue(result['auth_query_present'])
        self.assertTrue(result['authorization_header_present'])

    def test_missing_auth_is_absence_in_capture_not_permission(self):
        value = sample()
        req = value['log']['entries'][0]['request']
        req['url'] = req['url'].split('?')[0]
        req['headers'] = []
        row = summarize_har(value)['records'][0]
        self.assertFalse(row['auth_query_present'])
        self.assertFalse(row['authorization_header_present'])
        self.assertEqual(row['peer_delivery'], 'unverified')

    def test_strict_origin_path_method_no_arbitrary_capture_export(self):
        original = sample()['log']['entries'][0]
        urls = ['http://api.deadsimplechat.com/consumer/api/v2/bot/a/chatroom/b/message',
                'https://api.deadsimplechat.com.evil.test/consumer/api/v2/bot/a/chatroom/b/message',
                'https://secret@api.deadsimplechat.com/consumer/api/v2/bot/a/chatroom/b/message',
                'https://api.deadsimplechat.com:443/consumer/api/v2/bot/a/chatroom/b/message',
                'https://api.deadsimplechat.com/private/' + SECRET,
                'wss://api.deadsimplechat.com/socket.io/?token=' + SECRET]
        for url in urls:
            with self.subTest(url=url):
                row = copy.deepcopy(original)
                row['request']['url'] = url
                result = summarize_har({'log': {'entries': [row]}})
                self.assertEqual(result['records'], [])
                self.assertNotIn(SECRET, json.dumps(result))
        row = copy.deepcopy(original)
        row['request']['method'] = 'GET'
        self.assertEqual(summarize_har({'log': {'entries': [row]}})['records'], [])

    def test_schema_and_status_rejected_without_raw_input_errors(self):
        for value in (None, {}, {'log': []}, {'log': {'entries': SECRET}}, {'log': {'entries': [None]}}):
            with self.subTest(value=value), self.assertRaises(APIError):
                summarize_har(value)
        for status in (True, '200', -1, 600):
            value = sample()
            value['log']['entries'][0]['response']['status'] = status
            with self.assertRaises(APIError):
                summarize_har(value)
        value = sample()
        value['log']['entries'][0]['response']['status'] = 0
        self.assertEqual(summarize_har(value)['records'][0]['http_status'], 0)

    def test_metadata_bounds_and_invalid_url_fail_closed(self):
        for field in ('headers', 'queryString'):
            value = sample()
            value['log']['entries'][0]['request'][field] = 'invalid'
            with self.assertRaises(APIError):
                summarize_har(value)
        for url in ('https://[invalid', 'https://api.deadsimplechat.com:invalid/a'):
            value = sample()
            value['log']['entries'][0]['request']['url'] = url
            with self.assertRaises(APIError):
                summarize_har(value)
        value = sample()
        value['log']['entries'][0]['request']['headers'] = [{'name': [SECRET], 'value': SECRET}]
        with self.assertRaises(APIError):
            summarize_har(value)
        with patch('recon_deadsimplechat.MAX_MATCHES', 0), self.assertRaises(APIError):
            summarize_har(sample())
        with patch('recon_deadsimplechat.MAX_ENTRIES', 0), self.assertRaises(APIError):
            summarize_har(sample())

    def test_cli_documented_mode_is_runnable(self):
        tool = Path(__file__).resolve().parents[1] / 'tools/recon_site.py'
        result = subprocess.run([sys.executable, '-B', str(tool), 'deadsimplechat'], capture_output=True, text=True, timeout=5)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)['evidence_kind'], 'official_documentation_review')

    def test_cli_rejects_private_invalid_file_without_path_or_content(self):
        tool = Path(__file__).resolve().parents[1] / 'tools/recon_site.py'
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / (SECRET + '.har')
            source.write_text('{"secret":"' + SECRET + '",broken}')
            result = subprocess.run([sys.executable, '-B', str(tool), 'deadsimplechat', '--har', str(source)],
                                    capture_output=True, text=True, timeout=5)
            self.assertEqual(result.returncode, 2)
            self.assertNotIn(SECRET, result.stdout + result.stderr)

    def test_cli_size_limit_does_not_output_raw_bytes(self):
        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
        import recon_site
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'synthetic.har'
            source.write_text(json.dumps(sample()))
            with patch.object(recon_site, 'MAX_HAR_BYTES', 1), patch('sys.stderr', new_callable=io.StringIO) as errors:
                self.assertEqual(recon_site.main(['deadsimplechat', '--har', str(source)]), 2)
                self.assertNotIn(SECRET, errors.getvalue())


if __name__ == '__main__':
    unittest.main()
