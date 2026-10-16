"""Approved Europe browser-site worklist; deliberately NOT a live adapter registry.

Public product facts and audience estimates do not establish protocol contracts.
This module has no network, account, chat-join, sender or legacy-unlock operation.
"""
from copy import deepcopy
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
from urllib.parse import urlsplit

from core import APIError

DATA = Path(__file__).resolve().parent / 'data/europe_assessment.json'
SITE_IDS = ('6obcy', 'bazoocam', 'chatroom2000', 'knuddels', 'chaat',
            'tchatche', 'deutscher_chat', 'chat4free')
EUROPE_COUNTRIES = frozenset(('PL', 'FR', 'ES', 'BE', 'IT', 'DE', 'CH', 'AT', 'RO'))
CONTRACT_REQUIREMENTS = {
    'permission': 'Current platform rules and permitted automated diagnostic scope',
    'connection_session': 'Documented or authorized-observed connection, authentication and session expiry',
    'conversation_identity': 'Session, room, partner and conversation identity; rotation boundaries',
    'incoming_events': 'Synthetic/consented event schema, sender attribution and event occurrence ID',
    'send_reply': 'Permitted send operation, payload, bounds and disclosed opt-in reply',
    'ack_failure': 'Rejected vs API accepted vs unknown outcome vs peer-visible delivery',
    'next_close': 'Next/close when applicable; no invented random queue for community rooms',
    'reconnect_cleanup': 'Disconnect, reconnect, stale events, listener disposal and Stop',
    'policy_privacy': 'Consent, age policy, refusal/exit, disclosure, retention and log redaction',
}
TASKS = (
    ('public_recon', 'Public browser-flow and audience assessment', 'documented'),
    ('contract', 'Resolve permitted interface and sanitized lifecycle contract', 'pending'),
    ('adapter', 'Implement site-specific adapter behind the existing core', 'pending'),
    ('regression', 'Test identity, replay, late ACK, next/close and Stop', 'pending'),
    ('live_acceptance', 'Authorized staging with consenting participants', 'blocked'),
    ('handoff', 'Evidence-backed package and run instructions', 'pending'),
)


def _https(value):
    if not isinstance(value, str) or len(value) > 512:
        return False
    try:
        url = urlsplit(value)
        return (url.scheme == 'https' and bool(url.hostname) and url.username is None
                and url.password is None and url.port is None and not url.query
                and not url.fragment)
    except ValueError:
        return False


def _validate(data):
    if (not isinstance(data, dict) or type(data.get('schema_version')) is not int
            or data['schema_version'] != 1):
        raise ValueError('schema')
    approval = data['approval']
    if (approval['reference'] != 'owner-chat-2026-10-16-approve-all-europe-tasks'
            or approval['date'] != '2026-10-16'
            or approval['scope'] != 'all_eight_public_assessment_and_implementation_tasks'
            or approval['repeat_approval_required'] is not False
            or approval['provider_permission_established'] is not False):
        raise ValueError('approval')
    sites = data['sites']
    if not isinstance(sites, list) or tuple(s['id'] for s in sites) != SITE_IDS:
        raise ValueError('sites')
    for site in sites:
        if not _https(site['url']) or not _https(site['browser_source']):
            raise ValueError('browser source')
        if site['mode'] not in ('random_text', 'random_video', 'community'):
            raise ValueError('mode')
        if site['entry'] not in ('guest', 'account_required', 'guest_or_account'):
            raise ValueError('entry')
        if site['browser_evidence'] != 'official_description_not_live_test':
            raise ValueError('browser evidence')
        if not isinstance(site['browser_limit'], str) or len(site['browser_limit']) > 500:
            raise ValueError('browser limitation')
        policy = site['policy']
        if policy['status'] not in ('restricted_client', 'noncommercial_restrictions',
                                    'conditional_bot_tolerance', 'not_reviewed'):
            raise ValueError('policy')
        reviewed = policy['status'] != 'not_reviewed'
        if reviewed and (not _https(policy['source']) or policy['reviewed_on'] != '2026-10-16'):
            raise ValueError('policy source')
        if not reviewed and (policy['source'] is not None or policy['reviewed_on'] is not None):
            raise ValueError('unreviewed policy')
        if not isinstance(policy['summary'], str) or not 1 <= len(policy['summary']) <= 1000:
            raise ValueError('policy summary')
        traffic = site['traffic']
        if not _https(traffic['source']) or traffic['provider'] not in ('Semrush', 'Similarweb'):
            raise ValueError('traffic source')
        if traffic['scope'] not in ('all_devices_web', 'desktop_web'):
            raise ValueError('device scope')
        if traffic['period'] not in ('2026-08', '2026-09'):
            raise ValueError('period')
        if traffic['evidence'] not in ('fetched_profile', 'search_extract'):
            raise ValueError('traffic evidence')
        count = traffic['total_visits_estimate']
        if count is not None and (type(count) is not int or count <= 0):
            raise ValueError('visits')
        countries = traffic['listed_europe_countries']
        if not isinstance(countries, list) or not countries:
            raise ValueError('countries')
        seen, total = set(), Decimal('0')
        for row in countries:
            country, share = row['country'], row['share_percent']
            if country not in EUROPE_COUNTRIES or country in seen or not isinstance(share, str):
                raise ValueError('country share')
            value = Decimal(share)
            if not value.is_finite() or not 0 < value <= 100:
                raise ValueError('country share')
            seen.add(country)
            total += value
        if not 50 < total <= 100:
            raise ValueError('not demonstrated Europe majority in listed scope')
    return data


def worklist(path=DATA):
    """Return read-only, sanitized task packets. Approval never enables runtime."""
    try:
        source = Path(path)
        if source.stat().st_size > 65536:
            raise ValueError('size')
        data = _validate(json.loads(source.read_text(encoding='utf-8')))
    except (OSError, ValueError, InvalidOperation, KeyError, TypeError, AttributeError):
        raise APIError(503, 'Europe assessment manifest is missing or invalid') from None
    result = {'schema_version': 1, 'scope': 'Europe browser assessment backlog',
              'approval': {key: data['approval'][key] for key in (
                  'reference', 'date', 'scope', 'repeat_approval_required',
                  'provider_permission_established')}, 'sites': [],
              'external_requests': 0, 'messages_sent': 0, 'live_enabled': False,
              'legacy_delivery_queue_modified': False}
    # Project a closed set of public fields; arbitrary input fields never echo.
    for item in data['sites']:
        site = {key: deepcopy(item[key]) for key in (
            'id', 'url', 'mode', 'entry', 'browser_source', 'browser_evidence', 'browser_limit')}
        traffic = item['traffic']
        site['traffic'] = {key: deepcopy(traffic[key]) for key in (
            'source', 'provider', 'period', 'scope', 'evidence',
            'total_visits_estimate', 'listed_europe_countries')}
        site['traffic']['listed_europe_countries'] = [
            {key: row[key] for key in ('country', 'share_percent')}
            for row in traffic['listed_europe_countries']]
        site['traffic']['listed_europe_share_percent'] = str(sum(
            (Decimal(row['share_percent']) for row in traffic['listed_europe_countries']), Decimal('0')))
        site['traffic']['meaning'] = 'Estimated website visits, not active/unique chat users or matching probability'
        site['work_unlocked'] = True
        site['live_enabled'] = False
        site['adapter_implemented'] = False
        site['policy'] = {key: item['policy'][key] for key in (
            'status', 'source', 'summary', 'reviewed_on')}
        policy_status = site['policy']['status']
        site['next_task'] = ('contract' if policy_status == 'conditional_bot_tolerance' else
                             'policy_review' if policy_status == 'not_reviewed' else 'permission')
        site['random_next'] = ('advertised' if site['mode'].startswith('random_') else 'not_established')
        site['tasks'] = [{'id': key, 'label': label, 'state': state,
                          'owner_approved': True} for key, label, state in TASKS]
        site['core_contract'] = {key: {'state': 'unknown', 'required_evidence': value}
                                 for key, value in CONTRACT_REQUIREMENTS.items()}
        if policy_status != 'not_reviewed':
            site['core_contract']['permission']['state'] = 'policy_reviewed_not_live_authorized'
            site['core_contract']['permission']['source'] = site['policy']['source']
        result['sites'].append(site)
    result['summary'] = {'approved_sites': len(result['sites']),
                         'work_unlocked': len(result['sites']),
                         'adapters_implemented': 0, 'live_connected': 0,
                         'policy_pages_reviewed': sum(s['policy']['status'] != 'not_reviewed' for s in result['sites']),
                         'next_site': next((s['id'] for s in result['sites']
                                            if s['policy']['status'] == 'conditional_bot_tolerance'), None),
                         'next_task': 'contract'}
    return result
