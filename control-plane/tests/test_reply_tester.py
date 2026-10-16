"""Self-test only: synthetic scripts/messages, no provider request or send."""
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import tempfile
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from app import make_server
from core import APIError, Controller
from reply_tester import ReplyTester, parse_script
from site_workflow import SiteWorkflow, initial_state, render


class ReplyTesterTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / 'test.db'
        self.controller = Controller(self.path)
        self.tester = ReplyTester(self.controller)

    def tearDown(self):
        self.controller.close()
        self.tmp.cleanup()

    def script(self, text='First reply\nSecond reply\nFinal reply'):
        state = self.tester.create(text)
        return self.tester.action(state['id'], 'start')

    def assert_api(self, code, func, *args):
        with self.assertRaises(APIError) as caught:
            func(*args)
        self.assertEqual(caught.exception.status, code)

    def test_utf8_bom_crlf_blank_lines_and_order(self):
        self.assertEqual(parse_script('\ufeff Hello \r\n\r\n বাংলা\rLast\n'), ['Hello','বাংলা','Last'])

    def test_limits_and_invalid_script(self):
        for text in ('', ' \n', None, '\x00bad', '\x7fbad', 'x'*1001, '\n'.join(['line']*201), '\ud800'):
            with self.subTest(text=repr(text)), self.assertRaises(APIError):
                parse_script(text)
        self.assert_api(413, parse_script, 'x'*8193)

    def test_upload_and_start_do_not_consume_lines(self):
        state = self.tester.create('A\nB')
        self.assertEqual((state['cursor'], state['status']), (0,'ready'))
        started = self.tester.action(state['id'], 'start')
        self.assertEqual(started['cursor'], 0)
        self.assertEqual(started['events'], [])
        self.assertEqual(started['external_messages_sent'], 0)
        self.assertFalse(started['provider_connected'])

    def test_user_messages_advance_exactly_one_reply_and_stop_at_end(self):
        state = self.script()
        for i, reply in enumerate(['First reply','Second reply','Final reply']):
            result = self.tester.message(state['id'], state['run_id'], 'event-'+str(i), 'Repeated legitimate text')
            self.assertEqual(result['reply'], reply)
            self.assertEqual(result['state']['cursor'], i+1)
            self.assertEqual(result['state']['peer_delivery'], 'not_tested')
        self.assertEqual(result['state']['status'], 'complete')
        self.assert_api(409, self.tester.message, state['id'],state['run_id'],'event-extra','More')

    def test_duplicate_retry_returns_same_reply_even_after_last_line(self):
        state = self.script('Only reply')
        first = self.tester.message(state['id'],state['run_id'],'event','user input')
        second = self.tester.message(state['id'],state['run_id'],'event','user input')
        self.assertEqual(first['reply'], second['reply'])
        self.assertTrue(second['duplicate'])
        self.assertEqual(second['state']['cursor'],1)
        self.assertEqual(second['state']['duplicates'],1)
        self.assert_api(409,self.tester.message,state['id'],state['run_id'],'event','Changed input')

    def test_concurrent_duplicate_advances_once(self):
        state = self.script()
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(lambda _: self.tester.message(state['id'],state['run_id'],'same','hello'), range(20)))
        self.assertEqual(sum(not r['duplicate'] for r in results),1)
        self.assertEqual(self.tester.state(state['id'])['cursor'],1)

    def test_isolation_stop_resume_and_reset(self):
        first, second = self.script(), self.script('Different script')
        self.tester.message(first['id'],first['run_id'],'event','hello')
        self.assertEqual(self.tester.state(second['id'])['cursor'],0)
        self.tester.action(first['id'],'stop')
        self.assert_api(409,self.tester.message,first['id'],first['run_id'],'late','hello')
        resumed = self.tester.action(first['id'],'start')
        self.assertNotEqual(resumed['run_id'],first['run_id'])
        self.assertEqual(self.tester.message(first['id'],resumed['run_id'],'new','hello')['reply'],'Second reply')
        self.tester.action(first['id'],'reset')
        fresh = self.tester.action(first['id'],'start')
        self.assertEqual(self.tester.message(first['id'],fresh['run_id'],'new','hello')['reply'],'First reply')

    def test_restart_restores_scripts_but_disarms(self):
        state = self.script()
        self.tester.message(state['id'],state['run_id'],'event','hello')
        self.controller.close()
        self.controller = Controller(self.path)
        self.tester = ReplyTester(self.controller)
        restored = self.tester.state(state['id'])
        self.assertEqual((restored['status'],restored['cursor']),('stopped',1))
        self.assert_api(409,self.tester.message,state['id'],state['run_id'],'late','hello')

    def test_no_user_input_or_filename_in_db_or_report(self):
        state = self.script()
        private = 'PRIVATE-SYNTHETIC-USER-INPUT-DO-NOT-STORE'
        result = self.tester.message(state['id'],state['run_id'],'event',private)
        self.assertNotIn(private,json.dumps(result))
        self.assertNotIn(private,'\n'.join(self.controller.db.iterdump()))
        self.assertNotIn('filename',json.dumps(result))

    def test_global_stop_and_invalid_event_input(self):
        first, second = self.script(), self.script()
        self.tester.stop_all()
        self.assertEqual(self.tester.state(first['id'])['status'],'stopped')
        self.assertEqual(self.tester.state(second['id'])['status'],'stopped')
        self.assert_api(400,self.tester.message,first['id'],first['run_id'],'event','')
        self.assert_api(400,self.tester.message,first['id'],first['run_id'],'bad/id','hello')
        self.assert_api(404,self.tester.state,'missing')


class TesterHTTPTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        plan = self.root/'research/test/PLAN.md'
        plan.parent.mkdir(parents=True)
        plan.write_text('Synthetic owner-approved local tester fixture')
        state = initial_state()
        state['sites']['deadsimplechat'].update(completed_steps=[1,2], evidence={'1':'research/test/PLAN.md','2':'research/test/PLAN.md'}, plan_path='research/test/PLAN.md')
        source = self.root/'SITES.md'
        source.write_text(render(state))
        self.workflow = SiteWorkflow(source,self.root)
        self.workflow.approve_plan('deadsimplechat',self.workflow.read_plan()['plan_sha256'],'synthetic-test-only',0)
        self.controller = Controller(self.root/'test.db')
        self.token = 'tester-operator-'+'x'*32
        self.server = make_server('127.0.0.1',0,self.controller,self.token,workflow=self.workflow,home='tester')
        self.thread = threading.Thread(target=self.server.serve_forever,daemon=True)
        self.thread.start()
        self.base = 'http://127.0.0.1:'+str(self.server.server_port)

    def tearDown(self):
        self.server.shutdown();self.server.server_close();self.thread.join(timeout=2)
        self.controller.close();self.tmp.cleanup()

    def request(self,path,data=None,token=None,origin=None):
        headers={'Authorization':'Bearer '+(self.token if token is None else token),'Content-Type':'application/json'}
        if origin:headers['Origin']=origin
        req=Request(self.base+path,data=json.dumps(data).encode() if data is not None else None,headers=headers)
        try:response=urlopen(req,timeout=5)
        except HTTPError as exc:response=exc
        with response:return response.code,json.load(response)

    def test_full_local_http_flow_and_live_report(self):
        code,state=self.request('/api/reply-test/sessions',{'script':'One\nTwo'})
        self.assertEqual(code,201)
        base='/api/reply-test/sessions/'+state['id']
        state=self.request(base+'/start',{})[1]
        body={'text':'my user message','run_id':state['run_id'],'event_id':'test-event'}
        result=self.request(base+'/message',body)[1]
        self.assertEqual(result['reply'],'One')
        self.assertEqual(self.request(base)[1]['cursor'],1)
        self.assertTrue(self.request(base+'/message',body)[1]['duplicate'])
        self.assertEqual(self.request('/api/stop-all',{})[0],200)
        self.assertEqual(self.request(base+'/message',{**body,'event_id':'late'})[0],409)

    def test_auth_origin_approval_and_no_live_transport(self):
        self.assertEqual(self.request('/api/reply-test/sessions',{'script':'One'},token='wrong')[0],401)
        self.assertEqual(self.request('/api/reply-test/sessions',{'script':'One'},origin='https://evil.test')[0],403)
        (self.root/'research/test/PLAN.md').write_text('Changed: no longer approved')
        self.assertEqual(self.request('/api/reply-test/sessions',{'script':'One'})[0],409)

    def test_small_dashboard_static_allowlist_and_home(self):
        with urlopen(self.base,timeout=5) as response:
            html=response.read().decode()
            self.assertIn('TXT Reply Lab',html)
            self.assertIn('NO PROVIDER SEND',html)
        for path in ('/test','/test.js','/test.css','/operations'):
            with urlopen(self.base+path,timeout=5) as response:self.assertEqual(response.code,200)
        self.assertEqual(self.request('/api/reply-test/sessions',{'script':'\x00binary'})[0],400)


if __name__=='__main__':unittest.main()
