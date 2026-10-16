import concurrent.futures
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core import APIError, Controller
from workspace import seed_inactive_configurations
from app import make_server


class CoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / 'test.db'
        self.c = Controller(self.path)

    def tearDown(self):
        self.c.close()
        self.temp.cleanup()

    def instance(self, name='Sandbox'):
        return self.c.create(name, 'simulator')

    def test_config_persistence_without_auto_resume(self):
        item = self.instance()
        self.c.start(item['id'])
        self.c.close()
        self.c = Controller(self.path)
        saved = self.c.snapshot()['instances'][0]
        self.assertEqual(saved['name'], 'Sandbox')
        self.assertEqual(saved['status'], 'stopped')
        self.assertIsNone(saved['run_id'])

    def test_start_idempotent_stop_and_heartbeat(self):
        item = self.instance()
        first = self.c.start(item['id'])
        self.assertEqual(self.c.start(item['id'])['run_id'], first['run_id'])
        self.c.tick()
        self.assertIsNotNone(self.c.snapshot()['instances'][0]['heartbeat_at'])
        self.c.stop(item['id'])
        self.c.tick()
        stopped = self.c.stop(item['id'])
        self.assertEqual(stopped['status'], 'stopped')
        self.assertIsNone(stopped['heartbeat_at'])

    def test_run_isolation_and_stale_check(self):
        item = self.instance()
        first = self.c.start(item['id'])
        self.c.check(item['id'], 'same', first['run_id'])
        self.c.stop(item['id'])
        second = self.c.start(item['id'])
        self.assertNotEqual(first['run_id'], second['run_id'])
        with self.assertRaises(APIError):
            self.c.check(item['id'], 'late', first['run_id'])
        self.assertFalse(self.c.check(item['id'], 'same', second['run_id'])['duplicate'])

    def test_deduplication_and_instance_isolation(self):
        a, b = self.instance('A'), self.instance('B')
        ra, rb = self.c.start(a['id']), self.c.start(b['id'])
        self.assertFalse(self.c.check(a['id'], 'event-1', ra['run_id'])['duplicate'])
        self.assertTrue(self.c.check(a['id'], 'event-1', ra['run_id'])['duplicate'])
        self.assertFalse(self.c.check(b['id'], 'event-1', rb['run_id'])['duplicate'])
        self.c.check(a['id'], 'event-2', ra['run_id'])
        self.assertEqual(self.c.snapshot()['summary']['checks_passed'], 3)
        self.assertEqual(self.c.snapshot()['summary']['duplicates'], 1)
        self.c.stop(a['id'])
        self.assertEqual(self.c.snapshot()['summary']['running'], 1)

    def test_log_and_dedup_bounds(self):
        item = self.instance()
        running = self.c.start(item['id'])
        for i in range(1050):
            self.c.check(item['id'], f'event-{i}', running['run_id'])
        self.assertEqual(len(self.c.logs(item['id'])), 100)
        self.assertEqual(len(self.c.runtime[item['id']]['seen']), 1000)
        self.assertEqual(len(self.c.audit), 200)

    def test_real_platforms_fail_closed(self):
        for adapter in ('minnit', 'deadsimplechat'):
            item = self.c.create(adapter, adapter)
            with self.assertRaises(APIError) as caught:
                self.c.start(item['id'])
            self.assertEqual(caught.exception.status, 409)
        self.assertEqual(self.c.snapshot()['summary']['running'], 0)
        self.assertEqual(self.c.snapshot()['live_connections'], 0)
        self.assertIsNone(self.c.snapshot()['acquisitions'])

    def test_delete_running_rejected_and_global_stop(self):
        items = [self.instance(str(i)) for i in range(3)]
        for item in items:
            self.c.start(item['id'])
        with self.assertRaises(APIError):
            self.c.delete(items[0]['id'])
        self.assertEqual(self.c.stop_all()['summary']['running'], 0)
        self.c.delete(items[0]['id'])
        with self.assertRaises(APIError):
            self.c.logs(items[0]['id'])

    def test_bootstrap_adds_only_missing_inactive_configs(self):
        result=seed_inactive_configurations(self.c)
        self.assertEqual(result['added'],8)
        self.assertEqual(result['workers_started'],0)
        self.assertTrue(all(i['status']=='stopped' and not i['ready'] for i in result['instances']))
        self.assertEqual(seed_inactive_configurations(self.c)['added'],0)
        self.c.close();self.c=Controller(self.path)
        self.assertEqual(len(self.c.snapshot()['instances']),8)
        self.assertEqual(self.c.snapshot()['summary']['running'],0)

    def test_bootstrap_preserves_existing_configuration(self):
        existing=self.c.create('My existing room','minnit')
        self.assertEqual(seed_inactive_configurations(self.c)['added'],7)
        saved=next(i for i in self.c.snapshot()['instances'] if i['id']==existing['id'])
        self.assertEqual(saved['name'],'My existing room')

    def test_invalid_configuration(self):
        for name in ('', 'x'*65, None, ['x'], 'bad\nname'):
            with self.assertRaises(APIError):
                self.c.create(name, 'simulator')
        with self.assertRaises(APIError):
            self.c.create('X', 'unknown')
        item = self.instance()
        for event_id in ('', '<script>', None, 'x'*129):
            with self.assertRaises(APIError):
                self.c.check(item['id'], event_id, None)

    def test_100_configurations_not_load_capacity(self):
        for i in range(100):
            self.instance(str(i))
        self.assertEqual(self.c.snapshot()['summary']['configured'], 100)
        with self.assertRaises(APIError) as caught:
            self.instance('overflow')
        self.assertEqual(caught.exception.status, 409)

    def test_concurrent_duplicate_checks_are_atomic(self):
        item = self.instance()
        running = self.c.start(item['id'])
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(lambda _: self.c.check(item['id'], 'shared', running['run_id']), range(40)))
        self.assertEqual(sum(not r['duplicate'] for r in results), 1)
        self.assertEqual(self.c.snapshot()['summary']['duplicates'], 39)

    def test_stopped_check_and_closed_controller(self):
        item = self.instance()
        with self.assertRaises(APIError):
            self.c.check(item['id'], 'event', 'run')
        self.c.close()
        self.c.close()
        with self.assertRaises(APIError):
            self.c.snapshot()


class HTTPTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.c = Controller(Path(self.temp.name) / 'http.db')
        self.server = make_server('127.0.0.1', 0, self.c, 'test-operator-token')
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.start()
        self.base = f'http://127.0.0.1:{self.server.server_port}'

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(3)
        self.c.close()
        self.temp.cleanup()

    def request(self, path, method='GET', body=None, headers=None, auth=True):
        h = {'Content-Type':'application/json'}
        if auth:
            h['Authorization'] = 'Bearer test-operator-token'
        h.update(headers or {})
        payload = None if method == 'GET' else json.dumps(body or {}).encode()
        try:
            response = urlopen(Request(self.base+path, data=payload, method=method, headers=h), timeout=5)
        except HTTPError as error:
            response = error
        with response:
            raw = response.read()
            content = json.loads(raw) if 'application/json' in response.headers['Content-Type'] else raw
            return response.status, content, response.headers

    def test_auth_and_public_shell(self):
        self.assertEqual(self.request('/api/state', auth=False)[0], 401)
        self.assertEqual(self.request('/api/state', headers={'Authorization':'Bearer wrong'})[0], 401)
        self.assertTrue(self.request('/api/info', auth=False)[1]['auth_required'])
        for path in ('/', '/app.js', '/style.css'):
            status, body, headers = self.request(path, auth=False)
            self.assertEqual(status, 200)
            self.assertGreater(len(body), 100)
            self.assertEqual(headers['X-Content-Type-Options'], 'nosniff')
            self.assertIn("script-src 'self'", headers['Content-Security-Policy'])

    def test_full_lifecycle_over_http(self):
        status, item, _ = self.request('/api/instances','POST',{'name':'HTTP sandbox','adapter':'simulator'})
        self.assertEqual(status, 201)
        path = '/api/instances/'+item['id']
        started = self.request(path+'/start','POST')[1]
        event = {'event_id':'http-event', 'run_id':started['run_id']}
        self.assertFalse(self.request(path+'/check','POST',event)[1]['duplicate'])
        self.assertTrue(self.request(path+'/check','POST',event)[1]['duplicate'])
        self.assertGreater(len(self.request(path+'/logs')[1]['logs']), 0)
        self.assertEqual(self.request(path,'DELETE')[0], 409)
        self.assertEqual(self.request('/api/stop-all','POST')[1]['summary']['running'], 0)
        self.assertEqual(self.request(path,'DELETE')[0], 200)
        self.assertEqual(self.request(path+'/logs')[0], 404)

    def test_origin_protection_preview_host_and_no_cors(self):
        body={'name':'preview','adapter':'simulator'}
        self.assertEqual(self.request('/api/instances','POST',body,{'Origin':'https://evil.example'})[0],403)
        self.assertEqual(self.request('/api/instances','POST',body,{'Sec-Fetch-Site':'cross-site'})[0],403)
        headers={'Host':'8080-example.e2b.app','Origin':'https://8080-example.e2b.app'}
        self.assertEqual(self.request('/api/instances','POST',body,headers)[0],201)
        self.assertIsNone(self.request('/api/state')[2].get('Access-Control-Allow-Origin'))

    def test_research_and_contract_api_auth_and_local_only(self):
        self.assertEqual(self.request('/api/research', auth=False)[0], 401)
        status, research, _ = self.request('/api/research')
        self.assertEqual(status, 200)
        self.assertEqual(len(research['sites']), 12)
        for site in research['sites']:
            self.assertFalse(site['can_start_live'])
        fixtures = self.request('/api/contracts')[1]['fixtures']
        for platform, fixture in fixtures.items():
            path = '/api/contracts/' + platform + '/inspect'
            self.assertEqual(self.request(path, 'POST', fixture, auth=False)[0], 401)
            self.assertEqual(self.request(path, 'POST', fixture, {'Origin':'https://evil.example'})[0], 403)
            status, result, _ = self.request(path, 'POST', fixture)
            self.assertEqual(status, 200)
            self.assertEqual(result['external_requests'], 0)
            self.assertEqual(result['messages_sent'], 0)
        self.assertEqual(self.request('/api/contracts/unknown/inspect', 'POST', {})[0], 404)

    def test_registry_and_configuration_only_sites(self):
        self.assertEqual(self.request('/api/platforms',auth=False)[0],401)
        status,result,_=self.request('/api/platforms')
        self.assertEqual(status,200);self.assertEqual(len(result['platforms']),13)
        self.assertEqual(result['live_ready'],0)
        for platform in result['platforms']:
            status,item,_=self.request('/api/instances','POST',{'name':platform['name'],'adapter':platform['id']})
            if platform['configurable']:
                self.assertEqual(status,201)
                if platform['id']!='simulator':
                    self.assertFalse(item['ready']);self.assertEqual(self.request('/api/instances/'+item['id']+'/start','POST')[0],409)
            else:self.assertEqual(status,409)

    def test_secret_free_specification_endpoint(self):
        body = {'bot_id':'bot','room_id':'room','message':'Synthetic only'}
        status, spec, _ = self.request('/api/contracts/deadsimplechat/describe-send', 'POST', body)
        self.assertEqual(status, 200)
        self.assertFalse(spec['transmitted'])
        self.assertNotIn('?auth=', spec['endpoint'])

    def test_payload_validation_and_static_allowlist(self):
        self.assertEqual(self.request('/api/instances','POST',{'name':None,'adapter':'simulator'})[0],400)
        self.assertEqual(self.request('/api/instances','POST',{'name':'X','adapter':'simulator'},{'Content-Type':'text/plain'})[0],415)
        self.assertEqual(self.request('/api/instances','POST',{'name':'x'*17000})[0],413)
        self.assertEqual(self.request('/api/instances','POST',[])[0],400)  # {} after helper normalization still invalid
        for path in ('/app.py','/../core.py','/api/unknown'):
            self.assertEqual(self.request(path)[0],404)
        request = Request(self.base+'/api/instances',data=b'{broken',method='POST',headers={'Authorization':'Bearer test-operator-token','Content-Type':'application/json'})
        with self.assertRaises(HTTPError) as caught:
            urlopen(request,timeout=5)
        self.assertEqual(caught.exception.code,400)
        caught.exception.close()
        request = Request(self.base+'/api/instances',data=b'[]',method='POST',headers={'Authorization':'Bearer test-operator-token','Content-Type':'application/json'})
        with self.assertRaises(HTTPError) as caught:
            urlopen(request,timeout=5)
        self.assertEqual(caught.exception.code,400)
        caught.exception.close()


if __name__ == '__main__':
    unittest.main()
