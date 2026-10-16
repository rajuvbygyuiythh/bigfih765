"""Approved dashboard shell + metadata index; synthetic local HTTP only."""
import json
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from app import make_server
from core import Controller
from reply_tester import ReplyTester, MAX_SESSIONS


class SessionIndexTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.controller=Controller(Path(self.tmp.name)/'index.db')
        self.tester=ReplyTester(self.controller)
    def tearDown(self):self.controller.close();self.tmp.cleanup()
    def test_empty_index_never_invents_a_session(self):
        self.assertEqual(self.tester.sessions(),{'mode':'local_self_test','sessions':[]})
    def test_index_is_bounded_and_contains_no_script_user_input_or_event_hash(self):
        for _ in range(MAX_SESSIONS):self.tester.create('PRIVATE SCRIPT')
        rows=self.tester.sessions()['sessions'];self.assertEqual(len(rows),MAX_SESSIONS)
        for row in rows:
            self.assertNotIn('script',row);self.assertNotIn('events',row);self.assertNotIn('input_hash',row)
            self.assertEqual(row['external_messages_sent'],0)
        self.assertNotIn('PRIVATE',json.dumps(rows))
    def test_metadata_tracks_start_message_stop_and_preserves_script_privately(self):
        session=self.tester.create('PRIVATE REPLY\nNEXT')
        current=self.tester.action(session['id'],'start')
        self.tester.message(session['id'],current['run_id'],'event','PRIVATE USER INPUT')
        self.tester.action(session['id'],'stop');row=self.tester.sessions()['sessions'][0]
        self.assertEqual((row['cursor'],row['status'],row['run_id']),(1,'stopped',None))
        self.assertNotIn('PRIVATE',json.dumps(row));self.assertNotIn('input_hash',json.dumps(row))
        self.assertEqual(self.tester.state(session['id'])['script_preview'][0],'PRIVATE REPLY')
    def test_restart_index_is_stopped_not_auto_resumed(self):
        session=self.tester.create('TEST');self.tester.action(session['id'],'start')
        restored=ReplyTester(self.controller).sessions()['sessions'][0]
        self.assertEqual(restored['status'],'stopped');self.assertIsNone(restored['run_id'])


class OperatorWorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.controller=Controller(Path(self.tmp.name)/'http.db')
        self.server=make_server('127.0.0.1',0,self.controller,'workspace-test-token')
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
        self.base='http://127.0.0.1:'+str(self.server.server_port)
    def tearDown(self):
        self.server.shutdown();self.server.server_close();self.thread.join(timeout=2)
        self.controller.close();self.tmp.cleanup()
    def call(self,path,auth=False):
        request=Request(self.base+path,headers={'Authorization':'Bearer workspace-test-token'} if auth else {})
        try:response=urlopen(request,timeout=5)
        except HTTPError as exc:response=exc
        with response:return response.status,response.read().decode()
    def test_default_workspace_and_aliases_replace_the_retired_dashboard(self):
        for path in ('/','/workspace','/test','/operations'):
            code,html=self.call(path);self.assertEqual(code,200)
            self.assertIn('Orbit · Operator workspace',html)
            self.assertIn('id="stop-all"',html);self.assertNotIn('<title>TXT Reply Lab',html)
            self.assertEqual(html.count('data-page='),7)
    def test_plan_and_legacy_routes_preserved_and_assets_allowlisted(self):
        self.assertIn('One site. One finished delivery.',self.call('/plan')[1])
        self.assertIn('TXT Reply Lab',self.call('/legacy/test')[1])
        for path in ('/workspace.css','/workspace.js','/OFL-NotoSansBengali.txt'):self.assertEqual(self.call(path)[0],200)
        for path in ('/.env.local','/reply_tester.py','/static/../app.py','/docs/DASHBOARD_APPROVAL.json'):
            self.assertEqual(self.call(path)[0],404)
    def test_session_metadata_requires_auth_and_never_returns_scripts(self):
        self.server.reply_tester.create('PRIVATE SCRIPT')
        self.assertEqual(self.call('/api/reply-test/sessions')[0],401)
        code,body=self.call('/api/reply-test/sessions',True);self.assertEqual(code,200)
        self.assertEqual(len(json.loads(body)['sessions']),1);self.assertNotIn('PRIVATE',body)
    def test_workspace_does_not_mutate_queue_or_enable_provider(self):
        before=self.call('/api/workflow',True)[1]
        self.call('/');self.call('/workspace.js');self.call('/api/reply-test/sessions',True)
        self.assertEqual(before,self.call('/api/workflow',True)[1])
        workflow=json.loads(before);self.assertEqual(workflow['active_site'],'deadsimplechat')
        self.assertEqual(workflow['sites']['deadsimplechat']['percent'],25)
        self.assertEqual(sum(workflow['sites'][key]['locked'] for key in workflow['order']),7)
        setup=json.loads(self.call('/api/deadsimplechat/setup',True)[1])
        self.assertFalse(setup['armed']);self.assertFalse(setup['outbound_enabled']);self.assertEqual(setup['external_messages_sent'],0)
    def test_browser_code_has_no_credential_storage_raw_html_or_unlock_shortcut(self):
        js=self.call('/workspace.js')[1]
        for forbidden in ('localStorage','sessionStorage','innerHTML','/complete-and-next','/approve-plan','DS_API_KEY=',"method:'DELETE'"):
            self.assertNotIn(forbidden,js)


if __name__=='__main__':unittest.main()
