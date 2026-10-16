"""Synthetic shadow intake/env-loader tests. No provider API call or live send."""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
import json
from pathlib import Path
import tempfile
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from app import make_server
from core import APIError, Controller
from deadsimplechat import ACTION, INTENT_TTL, PLAN_WINDOW, Settings, ShadowIntake
from server_env import load_private_env
from site_workflow import SiteWorkflow, initial_state, render

TOKEN='synthetic-operator-'+'a'*32
HOOK='synthetic-webhook-'+'b'*32
KEY='SYNTHETIC-PRIVATE-API-KEY'


class EnvTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.path=Path(self.tmp.name)/'.env.local'
    def tearDown(self):self.tmp.cleanup()
    def write(self,text):
        self.path.write_text(text);self.path.chmod(0o600)
    def test_explicit_allowlist_literal_values_and_process_precedence(self):
        self.write('# secret file\nCONTROL_PLANE_TOKEN="literal-token"\nDS_API_KEY=literal-$(not-executed)\nDS_ROOM_ID=room\n')
        env={'CONTROL_PLANE_TOKEN':'process-wins'}
        self.assertEqual(load_private_env(self.path,env),['CONTROL_PLANE_TOKEN','DS_API_KEY','DS_ROOM_ID'])
        self.assertEqual(env['CONTROL_PLANE_TOKEN'],'process-wins')
        self.assertEqual(env['DS_API_KEY'],'literal-$(not-executed)')
    def test_invalid_unknown_duplicate_and_quote_do_not_mutate_or_echo(self):
        for text in ('DS_API_KEY=PRIVATE\nUNKNOWN=PRIVATE','DS_API_KEY=PRIVATE\nDS_API_KEY=PRIVATE',"DS_API_KEY='PRIVATE",'export DS_API_KEY=PRIVATE','DS_API_KEY=PRIVATE\x00'):
            self.write(text);env={}
            with self.assertRaises(ValueError) as caught:load_private_env(self.path,env)
            self.assertEqual(env,{})
            self.assertNotIn('PRIVATE',str(caught.exception))
    def test_permissions_symlinks_and_size_fail_closed(self):
        self.write('DS_API_KEY=PRIVATE')
        self.path.chmod(0o644)
        with self.assertRaises(ValueError):load_private_env(self.path,{})
        self.path.chmod(0o600)
        link=Path(self.tmp.name)/'linked';link.symlink_to(self.path)
        with self.assertRaises(ValueError):load_private_env(link,{})
        self.write('DS_API_KEY='+'x'*16385)
        with self.assertRaises(ValueError):load_private_env(self.path,{})


class ShadowTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.db_path=self.root/'test.db';self.controller=Controller(self.db_path)
        self.instance=self.controller.create('Authorized synthetic DS room','deadsimplechat')
        self.now=1800000000.0
        self.settings=Settings(True,True,self.instance['id'],'room','bot',HOOK,KEY)
        self.shadow=ShadowIntake(self.controller,self.settings,TOKEN,lambda:self.now)
    def tearDown(self):self.controller.close();self.tmp.cleanup()
    def payload(self):
        return {'triggeredBy':'actionButtonPressed','chatRoom':{'roomId':'room'},'bot':{'_id':'bot'},
                'user':{'_id':'private-test-user'},'message':{'_id':'question','message':'PRIVATE ORIGINAL BOT QUESTION'},
                'actionButtonPressed':{'_id':'button-definition','type':'action','id':ACTION,'messageId':'question'},
                'messageHistory':['PRIVATE HISTORY'],'ip':'PRIVATE IP'}
    def arm_register(self):
        self.shadow.arm()
        return self.shadow.register('question','private-test-user',self.shadow.run_id)
    def assert_api(self,code,operation,*args):
        with self.assertRaises(APIError) as caught:operation(*args)
        self.assertEqual(caught.exception.status,code)
    def test_default_disabled_and_missing_configuration(self):
        status=ShadowIntake(self.controller,token=TOKEN).status()
        self.assertFalse(status['configured']);self.assertFalse(status['outbound_enabled'])
        self.assertFalse(status['provider_connected']);self.assertFalse(status['vendor_signature_verified'])
        self.shadow.settings=replace(self.settings,authorized=False)
        self.assert_api(409,self.shadow.arm)
    def test_env_mapping_and_independent_secrets(self):
        env={'DS_SHADOW_ENABLED':'1','DS_AUTHORIZED_ROOM':'1','DS_INSTANCE_ID':self.instance['id'],
             'DS_ROOM_ID':'room','DS_BOT_ID':'bot','DS_WEBHOOK_SECRET':HOOK,'DS_API_KEY':KEY}
        self.assertEqual(Settings.from_env(env),self.settings)
        self.shadow.settings=replace(self.settings,webhook_secret=TOKEN)
        self.assertFalse(self.shadow.status()['configured'])
        self.assertNotIn(KEY,repr(self.settings))
        self.assertNotIn(HOOK,repr(self.settings))
    def test_one_registered_intent_matches_once_never_sends(self):
        self.arm_register()
        first=self.shadow.receive(self.payload());second=self.shadow.receive(self.payload())
        self.assertTrue(first['matched']);self.assertFalse(first['duplicate']);self.assertTrue(second['duplicate'])
        self.assertEqual(first['external_messages_sent'],0)
        self.assertFalse(first['provider_identity_verified'])
        self.assertEqual(self.shadow.status()['counts']['matched'],1)
    def test_unregistered_and_cross_binding_rejected_without_partial_mutation(self):
        self.shadow.arm()
        self.assertFalse(self.shadow.receive(self.payload())['matched'])
        self.arm_register()
        for group,key,value in [('bot','_id','other'),('chatRoom','roomId','other'),('message','_id','wrong'),('actionButtonPressed','id','wrong'),('actionButtonPressed','type','link')]:
            payload=self.payload();payload[group][key]=value
            self.assert_api(400,self.shadow.receive,payload)
        self.assertEqual(self.shadow.status()['counts']['registered'],1)
    def test_intent_expiry_cannot_be_reset_with_same_binding(self):
        self.arm_register();self.now+=INTENT_TTL+1
        self.assertFalse(self.shadow.receive(self.payload())['matched'])
        self.assert_api(409,self.shadow.register,'question','private-test-user',self.shadow.run_id)
        self.assertEqual(self.shadow.status()['counts']['expired'],1)
    def test_stop_rearm_stale_work_and_window_expiry(self):
        self.arm_register();old=self.shadow.run_id
        self.shadow.disarm();self.assert_api(409,self.shadow.receive,self.payload())
        self.shadow.arm()
        self.assert_api(409,self.shadow.register,'other','private-test-user',old)
        self.assertFalse(self.shadow.receive(self.payload())['matched'])
        self.assert_api(409,self.shadow.register,'question','private-test-user',self.shadow.run_id)
        self.now+=PLAN_WINDOW
        self.assertFalse(self.shadow.status()['armed'])
    def test_restart_disarms_and_retains_registration_tombstones(self):
        self.arm_register();self.controller.close();self.controller=Controller(self.db_path)
        self.shadow=ShadowIntake(self.controller,self.settings,TOKEN,lambda:self.now)
        self.assertFalse(self.shadow.status()['armed']);self.shadow.arm()
        self.assert_api(409,self.shadow.register,'question','private-test-user',self.shadow.run_id)
        self.assertEqual(self.shadow.status()['counts']['cancelled'],1)
    def test_concurrent_repeats_cannot_create_multiple_matches(self):
        self.arm_register()
        with ThreadPoolExecutor(max_workers=6) as pool:
            rows=list(pool.map(lambda _:self.shadow.receive(self.payload()),range(20)))
        self.assertEqual(sum(not row['duplicate'] for row in rows),1)
        self.assertEqual(self.shadow.status()['intents'][0]['duplicates'],19)
    def test_private_fields_are_not_retained_or_echoed(self):
        self.arm_register();self.shadow.receive(self.payload())
        output=json.dumps(self.shadow.status())+'\n'.join(self.controller.db.iterdump())
        for value in (TOKEN,HOOK,KEY,'private-test-user','PRIVATE ORIGINAL BOT QUESTION','PRIVATE HISTORY','PRIVATE IP'):
            self.assertNotIn(value,output)
        self.assert_api(401,self.shadow.authenticate,'wrong')
    def test_real_local_http_auth_before_body_queue_gate_and_stop_all(self):
        plan=self.root/'research/test/PLAN.md';plan.parent.mkdir(parents=True);plan.write_text('Synthetic approved shadow test')
        state=initial_state();state['sites']['deadsimplechat'].update(completed_steps=[1,2],evidence={'1':'research/test/PLAN.md','2':'research/test/PLAN.md'},plan_path='research/test/PLAN.md')
        source=self.root/'SITES.md';source.write_text(render(state));workflow=SiteWorkflow(source,self.root)
        workflow.approve_plan('deadsimplechat',workflow.read_plan()['plan_sha256'],'synthetic-only',0)
        server=make_server('127.0.0.1',0,self.controller,TOKEN,workflow=workflow,shadow=self.shadow)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        base='http://127.0.0.1:'+str(server.server_port)
        def call(path,data=None,token=TOKEN,raw=None,origin=None):
            headers={'Content-Type':'application/json','Authorization':'Bearer '+token}
            if origin:headers['Origin']=origin
            req=Request(base+path,data=raw if raw is not None else json.dumps(data).encode() if data is not None else None,headers=headers)
            try:response=urlopen(req,timeout=5)
            except HTTPError as exc:response=exc
            with response:return response.code,json.load(response)
        try:
            self.assertEqual(call('/api/deadsimplechat/setup',token='wrong')[0],401)
            self.assertEqual(call('/api/deadsimplechat/shadow/arm',{})[0],200)
            self.assertEqual(call('/hooks/deadsimplechat/wrong',raw=b'invalid-json')[0],401)
            self.assertEqual(call('/hooks/deadsimplechat/'+HOOK,self.payload(),origin='https://evil.test')[0],403)
            local=call('/api/reply-test/sessions',{'script':'Local only'})[1]
            local_route='/api/reply-test/sessions/'+local['id']
            call(local_route+'/start',{})
            self.assertEqual(call('/api/deadsimplechat/shadow/register',{'question_id':'question','test_user_id':'private-test-user','run_id':self.shadow.run_id})[0],201)
            code,result=call('/hooks/deadsimplechat/'+HOOK,self.payload(),token='')
            self.assertEqual(code,200);self.assertEqual(result['status'],'shadow_matched_no_send')
            self.assertEqual(call(local_route)[1]['cursor'],0)
            with self.assertRaises(ValueError):
                make_server('127.0.0.1',0,self.controller,'',workflow=workflow,shadow=self.shadow)
            self.assertEqual(call('/api/stop-all',{})[0],200)
            self.assertFalse(self.shadow.status()['armed'])
            self.assertEqual(call('/hooks/deadsimplechat/'+HOOK,self.payload(),token='')[0],409)
        finally:
            server.shutdown();server.server_close();thread.join(timeout=2)


if __name__=='__main__':unittest.main()
