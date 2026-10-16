import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core import APIError
from contracts import FIXTURES, classify_deadsimplechat_result, describe_send, inspect
from research import ROOT, catalog, source_fingerprint


class ContractTests(unittest.TestCase):
    def check(self, site, fixture=None):
        value = copy.deepcopy(FIXTURES[site] if fixture is None else fixture)
        return inspect(site, value['payload'], value['expected_room_id'])

    def test_minnit_message_shape_and_no_send(self):
        result = self.check('minnit')
        self.assertEqual(result['events'][0]['kind'], 'message')
        self.assertFalse(result['events'][0]['automatic_reply_allowed'])
        self.assertFalse(result['authenticated_webhook'])
        self.assertEqual(result['external_requests'], 0)
        self.assertEqual(result['messages_sent'], 0)

    def test_batch_keeps_repeated_text_with_distinct_ids(self):
        f = copy.deepcopy(FIXTURES['minnit'])
        message = copy.deepcopy(f['payload']['data'][0])
        message['msg_id'] = 'different-id'
        f['payload']['data'].append(message)
        result = self.check('minnit', f)['events']
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['text'], result[1]['text'])
        self.assertNotEqual(result[0]['event_id'], result[1]['event_id'])

    def test_minnit_non_message_and_empty_batch(self):
        self.assertEqual(inspect('minnit', {'type':'user_joined'}, 'demo-room')['events'], [])
        self.assertEqual(inspect('minnit', {'type':'chat_message','data':[]}, 'demo-room')['events'], [])

    def test_edits_are_not_new_messages(self):
        f = copy.deepcopy(FIXTURES['minnit'])
        f['payload']['data'][0]['edited'] = True
        self.assertEqual(self.check('minnit', f)['events'][0]['kind'], 'message_edit')
        f['payload']['data'][0]['edited'] = 'false'
        with self.assertRaises(APIError):
            self.check('minnit', f)

    def test_sensitive_extra_fields_are_not_propagated(self):
        f = copy.deepcopy(FIXTURES['minnit'])
        f['payload']['data'][0].update(ip='synthetic-ip', cookie='synthetic-cookie', token='synthetic-token')
        output = json.dumps(self.check('minnit', f))
        for value in ('synthetic-ip','synthetic-cookie','synthetic-token'):
            self.assertNotIn(value, output)

    def test_room_isolation_both_platforms(self):
        for platform in FIXTURES:
            f = copy.deepcopy(FIXTURES[platform])
            f['expected_room_id'] = 'wrong-room'
            with self.subTest(platform=platform), self.assertRaises(APIError):
                self.check(platform, f)

    def test_malformed_batches_and_members(self):
        for data in (None, {}, 'text', [None], [{}], [True], [{}]*101):
            with self.subTest(data_type=type(data).__name__), self.assertRaises(APIError):
                inspect('minnit', {'type':'chat_message','data':data}, 'demo-room')

    def test_invalid_identity_types(self):
        for value in (True, None, 1.5, '', '../secret', ['x'], 'x'*129):
            f = copy.deepcopy(FIXTURES['minnit'])
            f['payload']['data'][0]['user_id'] = value
            with self.subTest(value=value), self.assertRaises(APIError):
                self.check('minnit', f)

    def test_numeric_ids_are_normalized_without_bool_coercion(self):
        f = copy.deepcopy(FIXTURES['minnit'])
        f['payload']['data'][0]['user_id'] = 12
        self.assertEqual(self.check('minnit', f)['events'][0]['sender_id'], '12')

    def test_blank_and_oversized_text(self):
        for message in ('', ' ', 'x'*10001, None, {}):
            f = copy.deepcopy(FIXTURES['minnit'])
            f['payload']['data'][0]['message'] = message
            with self.assertRaises(APIError):
                self.check('minnit', f)

    def test_dsc_button_is_not_bot_question_as_user_text(self):
        result = self.check('deadsimplechat')['events'][0]
        self.assertEqual(result['kind'], 'button_action')
        self.assertEqual(result['parent_message_id'], 'bot-question')
        self.assertNotIn('text', result)
        self.assertFalse(result['automatic_reply_allowed'])

    def test_dsc_missing_action_and_unguessed_trigger(self):
        for key in ('user','chatRoom','actionButtonPressed'):
            f = copy.deepcopy(FIXTURES['deadsimplechat'])
            f['payload'].pop(key)
            with self.assertRaises(APIError):
                self.check('deadsimplechat', f)
        f = copy.deepcopy(FIXTURES['deadsimplechat'])
        f['payload']['triggeredBy'] = 'guessedNewMessage'
        with self.assertRaises(APIError):
            self.check('deadsimplechat', f)

    def test_minnit_send_specification(self):
        result = describe_send('minnit', {'chatname':'OwnedRoom','channel':'main','message':'Synthetic reply'})
        self.assertFalse(result['transmitted'])
        self.assertEqual(result['fields']['action'], 'sendmessage')
        self.assertIn('X-Key', result['auth_location'])
        self.assertIn('DASHBOARD', result['endpoint'])

    def test_dsc_send_specification_and_boundaries(self):
        for count in (1,1000):
            result = describe_send('deadsimplechat', {'room_id':'room','bot_id':'bot','message':'x'*count})
            self.assertFalse(result['transmitted'])
            self.assertNotIn('?auth=', result['endpoint'])
            self.assertEqual(result['content_type'], 'application/json')
        with self.assertRaises(APIError):
            describe_send('deadsimplechat', {'room_id':'room','bot_id':'bot','message':'x'*1001})
        with self.assertRaises(APIError):
            describe_send('deadsimplechat', {'room_id':'../elsewhere','bot_id':'bot','message':'x'})

    def test_unsupported_platform_and_non_objects(self):
        with self.assertRaises(APIError):
            inspect('unknown', {}, 'room')
        with self.assertRaises(APIError):
            describe_send('unknown', {'message':'x'})
        for platform in FIXTURES:
            with self.assertRaises(APIError):
                inspect(platform, [], 'room')

    def test_api_acceptance_never_means_peer_delivery(self):
        outcome = classify_deadsimplechat_result(200, {'success':True})
        self.assertEqual(outcome['submission'], 'api_accepted')
        self.assertEqual(outcome['peer_delivery'], 'unverified')
        self.assertFalse(outcome['safe_to_blind_retry'])

    def test_timeouts_and_ambiguous_results_no_blind_retry(self):
        for outcome in (classify_deadsimplechat_result(None, None, timed_out=True),
                        classify_deadsimplechat_result(200, {}),
                        classify_deadsimplechat_result(500, {}),
                        classify_deadsimplechat_result(200, {'success':'true'})):
            self.assertEqual(outcome['submission'], 'unknown')
            self.assertFalse(outcome['safe_to_blind_retry'])
        with self.assertRaises(APIError):
            classify_deadsimplechat_result(True, {})

    def test_explicit_http_rejections(self):
        for status in (400,401,403,404,429):
            self.assertEqual(classify_deadsimplechat_result(status, {})['submission'], 'rejected')


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root/'data').mkdir()
        self.data = json.loads((ROOT/'data/site_catalog.json').read_text())
        self.save()

    def tearDown(self):
        self.temp.cleanup()

    def save(self):
        (self.root/'data/site_catalog.json').write_text(json.dumps(self.data))

    def receipt(self, passed=True, exit_code=0):
        receipt = {'passed':passed,'source_sha256':source_fingerprint(self.root),
                   'checks':[{'id':'python_suite','exit_code':exit_code,'tests_ran':1}], 'covered_contracts':sorted(FIXTURES)}
        (self.root/'data/test_results.json').write_text(json.dumps(receipt))

    def test_missing_proof_does_not_fake_test_completion(self):
        result = catalog(self.root)
        self.assertFalse(result['local_test_receipt']['fresh_and_passed'])
        for site in result['sites'][:4]:
            self.assertEqual(site['progress']['completed'], 6)
            self.assertEqual(site['progress']['percent'], 50)
            self.assertFalse(site['can_start_live'])

    def test_fresh_proof_unlocks_only_local_test_gates(self):
        self.receipt()
        result = catalog(self.root)
        for site in result['sites'][:4]:
            self.assertEqual(site['progress']['completed'], 8)
            self.assertEqual(site['progress']['percent'], 67)
            self.assertEqual(len(site['remaining']), 4)
            self.assertFalse(site['can_start_live'])

    def test_changed_source_invalidates_proof(self):
        self.receipt()
        (self.root/'changed.py').write_text('changed = True')
        self.assertFalse(catalog(self.root)['local_test_receipt']['fresh_and_passed'])

    def test_failed_proof_does_not_unlock_gates(self):
        self.receipt(False, 1)
        self.assertEqual(catalog(self.root)['sites'][0]['progress']['completed'], 6)

    def test_malformed_proof_safe_fallback(self):
        (self.root/'data/test_results.json').write_text('{bad')
        self.assertFalse(catalog(self.root)['local_test_receipt']['fresh_and_passed'])

    def test_catalog_schema_and_source_validation(self):
        for change in ('duplicate','count','status','url'):
            data = copy.deepcopy(self.data)
            if change == 'duplicate':data['sites'][1]['id'] = data['sites'][0]['id']
            elif change == 'count':data['sites'][0]['gates'].pop()
            elif change == 'status':data['sites'][0]['gates'][0]['status'] = 'maybe'
            else:data['sites'][0]['sources'][0]['url'] = 'javascript:bad'
            (self.root/'data/site_catalog.json').write_text(json.dumps(data))
            with self.subTest(change=change), self.assertRaises(APIError):
                catalog(self.root)

    def test_manual_live_flag_cannot_enable_start(self):
        self.data['sites'][0]['can_start_live'] = True
        self.save()
        self.assertFalse(catalog(self.root)['sites'][0]['can_start_live'])

    def test_missing_catalog_is_service_error(self):
        (self.root/'data/site_catalog.json').unlink()
        with self.assertRaises(APIError) as caught:
            catalog(self.root)
        self.assertEqual(caught.exception.status, 503)


class ExpandedContractTests(unittest.TestCase):
    def fixture(self, platform):
        return copy.deepcopy(FIXTURES[platform])

    def inspect_fixture(self, platform, fixture):
        return inspect(platform, fixture['payload'], fixture['expected_room_id'])

    def test_rumble_history_is_not_live_webhook(self):
        result=self.inspect_fixture('rumbletalk',self.fixture('rumbletalk'))
        event=result['events'][0]
        self.assertEqual(event['kind'],'history_record')
        self.assertEqual(event['event_id'],'101')
        self.assertFalse(event['room_scope_verified'])
        self.assertFalse(result['authenticated_webhook'])
        self.assertEqual(result['external_requests'],0)

    def test_rumble_snapshot_filters_extra_secrets(self):
        f=self.fixture('rumbletalk')
        f['payload']['response']['token']='not-a-real-token'
        f['payload']['response']['data'][0]['ip']='not-a-real-ip'
        result=json.dumps(self.inspect_fixture('rumbletalk',f))
        self.assertNotIn('not-a-real-token',result)
        self.assertNotIn('not-a-real-ip',result)

    def test_rumble_rejects_false_or_wrong_typed_status(self):
        for status in (False,'true',1,None):
            f=self.fixture('rumbletalk');f['payload']['response']['status']=status
            with self.subTest(status=status),self.assertRaises(APIError):self.inspect_fixture('rumbletalk',f)

    def test_rumble_invalid_and_bounded_history(self):
        for rows in (None,{},[{}],['bad'],[{}]*101):
            f=self.fixture('rumbletalk');f['payload']['response']['data']=rows
            with self.assertRaises(APIError):self.inspect_fixture('rumbletalk',f)
        f=self.fixture('rumbletalk');f['payload']['response']['data']=[]
        self.assertEqual(self.inspect_fixture('rumbletalk',f)['events'],[])

    def test_rumble_system_send_limit_is_bytes(self):
        for message in ('x'*2000,'é'*1000,'🙂'*500):
            spec=describe_send('rumbletalk',{'room_id':'room','message':message})
            self.assertFalse(spec['transmitted']);self.assertEqual(spec['message_type'],'system')
        for message in ('x'*2001,'é'*1001,'🙂'*501):
            with self.assertRaises(APIError):describe_send('rumbletalk',{'room_id':'room','message':message})

    def test_rumble_spec_rejects_path_injection(self):
        with self.assertRaises(APIError):describe_send('rumbletalk',{'room_id':'../other','message':'x'})

    def test_chatwee_session_value_never_echoed(self):
        f=self.fixture('chatwee');f['payload']['response']='SYNTHETIC-UNIQUE-SECRET-MARKER'
        f['payload']['clientKey']='SYNTHETIC-CLIENT-KEY'
        result=self.inspect_fixture('chatwee',f)
        self.assertNotIn('SYNTHETIC-UNIQUE-SECRET-MARKER',json.dumps(result))
        self.assertNotIn('SYNTHETIC-CLIENT-KEY',json.dumps(result))
        event=result['events'][0]
        self.assertTrue(event['session_value_redacted']);self.assertFalse(event['is_chat_message'])
        self.assertNotIn('text',event);self.assertFalse(event['automatic_reply_allowed'])

    def test_chatwee_invalid_login_shapes(self):
        for response in (None,{},True,'',' ','x'*4097):
            f=self.fixture('chatwee');f['payload']['response']=response
            with self.assertRaises(APIError):self.inspect_fixture('chatwee',f)
        f=self.fixture('chatwee');f['payload']['operation']='guessed_send_message'
        with self.assertRaises(APIError):self.inspect_fixture('chatwee',f)

    def test_chatwee_sso_does_not_unlock_send(self):
        with self.assertRaises(APIError) as caught:describe_send('chatwee',{'message':'x'})
        self.assertEqual(caught.exception.status,409)

    def test_unknown_site_cannot_borrow_existing_fixture(self):
        for platform in ('chatblink','strangermeetup','chatango','chatiw','chatzy','joingy','isexychat'):
            with self.subTest(platform=platform),self.assertRaises(APIError):inspect(platform,{},'room')


class ExpandedCatalogTests(unittest.TestCase):
    setUp = CatalogTests.setUp
    tearDown = CatalogTests.tearDown
    save = CatalogTests.save
    receipt = CatalogTests.receipt
    def test_reference_and_restricted_percent_not_applicable(self):
        self.receipt();result=catalog(self.root)
        self.assertEqual(result['summary']['tracked'],12)
        self.assertEqual(result['summary']['local_contracts'],4)
        for site in result['sites']:
            if site['phase'] in ('restricted','reference'):
                self.assertIsNone(site['progress']['percent'])
                self.assertFalse(site['progress']['applicable'])
                self.assertFalse(site['configurable'])

    def test_unknown_contracts_do_not_inherit_global_suite(self):
        self.receipt();result=catalog(self.root)
        for site in result['sites']:
            if not site['has_local_contract']:
                for gate in site['gates']:
                    if gate['id'] in ('parser_tests','failure_tests'):self.assertEqual(gate['status'],'pending')

    def test_proof_requires_specific_platform_coverage(self):
        self.receipt();p=self.root/'data/test_results.json';receipt=json.loads(p.read_text());receipt['covered_contracts']=['minnit'];p.write_text(json.dumps(receipt))
        result=catalog(self.root)
        self.assertEqual(result['sites'][0]['progress']['completed'],8)
        self.assertEqual(result['sites'][1]['progress']['completed'],6)

    def test_missing_or_malformed_coverage_cannot_complete_tests(self):
        for value in (None,'minnit',{}):
            self.receipt();p=self.root/'data/test_results.json';receipt=json.loads(p.read_text());receipt['covered_contracts']=value;p.write_text(json.dumps(receipt))
            self.assertEqual(catalog(self.root)['sites'][0]['progress']['completed'],6)
