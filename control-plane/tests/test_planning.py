"""Default UI retirement and read-only plan routing; no provider access."""
import json
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from app import make_server
from core import Controller


class PlanningTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.controller=Controller(Path(self.tmp.name)/'test.db')
        self.server=make_server('127.0.0.1',0,self.controller,'planning-test-token')
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
        self.base='http://127.0.0.1:'+str(self.server.server_port)
    def tearDown(self):
        self.server.shutdown();self.server.server_close();self.thread.join(timeout=2)
        self.controller.close();self.tmp.cleanup()
    def get(self,path,auth=False):
        req=Request(self.base+path,headers={'Authorization':'Bearer planning-test-token'} if auth else {})
        try:response=urlopen(req,timeout=5)
        except HTTPError as exc:response=exc
        with response:return response.status,response.read().decode()
    def test_default_and_old_aliases_show_plan_not_previous_dashboard(self):
        for path in ('/','/plan','/test','/operations'):
            code,html=self.get(path);self.assertEqual(code,200)
            self.assertIn('One site. One finished delivery.',html)
            self.assertNotIn('id="script-file"',html);self.assertNotIn('id="stop-all"',html)
    def test_previous_sources_preserved_in_explicit_legacy_routes(self):
        self.assertIn('TXT Reply Lab',self.get('/legacy/test')[1])
        self.assertIn('id="stop-all"',self.get('/legacy/operations')[1])
    def test_plan_assets_allowlisted_without_source_or_private_exposure(self):
        for path in ('/planning.css','/planning.js'):self.assertEqual(self.get(path)[0],200)
        for path in ('/server_env.py','/.env.local','/docs/DASHBOARD_MASTER_PLAN.md','/legacy/../app.py'):
            self.assertEqual(self.get(path)[0],404)
    def test_reading_page_does_not_bypass_workflow_auth_or_mutate_queue(self):
        self.assertEqual(self.get('/api/workflow')[0],401)
        before=json.loads(self.get('/api/workflow',True)[1])
        self.get('/');self.get('/planning.js');self.get('/plan')
        after=json.loads(self.get('/api/workflow',True)[1]);self.assertEqual(before,after)
        self.assertEqual(after['active_site'],'deadsimplechat')
        self.assertEqual(after['sites']['deadsimplechat']['completed_steps'],[1,2])
        self.assertEqual(sum(after['sites'][key]['state']=='locked' for key in after['order']),7)
    def test_planning_script_has_no_mutation_or_secret_persistence_path(self):
        script=self.get('/planning.js')[1]
        for forbidden in ('localStorage','sessionStorage','innerHTML',"'POST'","'DELETE'",'/approve-plan','/complete-and-next'):
            self.assertNotIn(forbidden,script)


if __name__=='__main__':unittest.main()
