"""One-site recon: documented contracts and allowlisted, value-free HAR metadata.

Offline only. Never inspect bodies/cookies/WebSocket frames or reproduce requests.
HAR evidence does not establish auth requirements, webhook identity or delivery.
"""
import re
from urllib.parse import parse_qsl, urlsplit

from core import APIError

MAX_HAR_BYTES = 20 * 1024 * 1024
MAX_ENTRIES = 10000
MAX_MATCHES = 500
SEND_PATH = re.compile(r'/consumer/api/v2/bot/[A-Za-z0-9_-]{1,128}/chatroom/[A-Za-z0-9_-]{1,128}/message')


def documented_recon():
    return {
        'schema_version': 1, 'site': 'deadsimplechat', 'step': 1,
        'scope': 'Authorized single-room bot/action diagnostic; no join-triggered outreach',
        'evidence_kind': 'official_documentation_review', 'reviewed_at': '2026-10-16',
        'sources': [
            'https://deadsimplechat.com/support/rest-api/bots/post-send-message-bot',
            'https://deadsimplechat.com/support/bots/quiz-bot-using-action-buttons'],
        'documented': {
            'plan': 'Business / Advanced API',
            'send': {'method': 'POST', 'origin': 'https://api.deadsimplechat.com',
                     'path': '/consumer/api/v2/bot/{bot_id}/chatroom/{room_id}/message',
                     'content_type': 'application/json', 'message_max_characters': 1000,
                     'required_query_auth': True, 'examples_also_show_authorization_header': True},
            'api_acceptance': {'http_status': 200, 'boolean_success': True,
                               'does_not_prove_peer_delivery': True},
            'receive': {'trigger': 'actionButtonPressed',
                        'enclosing_message_is': 'original bot question, not user input',
                        'unique_click_occurrence_id_established': False}},
        'unresolved': [
            'Query auth is required in the table; send examples also add Authorization, while quiz code uses query only. Exact header requirement unresolved.',
            'Webhook signature/authenticity, replay and retry guarantees are not established.',
            'Button definition ID must not be treated as a unique click occurrence.',
            'Actual plan/room/bot authorization, provider egress, callback and peer delivery are untested.'],
        'capture_guidance': {
            'browser_har_limitation': 'Browser HAR usually cannot contain backend-to-provider bot sends or server-to-server webhooks.',
            'when_needed': 'Only for an authorized staging flow; do not repeat sends just to probe authentication.',
            'safe_input': 'Keep raw traces in ignored runtime storage; never upload keys, cookies or private transcripts.',
            'webhook_evidence': 'Use a separately redacted consenting test fixture; HAR metadata cannot prove click uniqueness or callback authenticity.'},
        'external_requests': 0, 'messages_sent': 0, 'live_ready': False,
    }


def _object(value):
    if not isinstance(value, dict):
        raise APIError(400, 'HAR structure must contain objects')
    return value


def summarize_har(value):
    """Retain only fixed public route template, auth-location booleans and status.

    Does not echo URL, IDs, query names/values, header values, response MIME text,
    bodies, timings, cookies, redirects, usernames, errors or input filenames.
    """
    entries = _object(_object(value).get('log')).get('entries')
    if not isinstance(entries, list) or len(entries) > MAX_ENTRIES:
        raise APIError(400, 'HAR entries must be an array of at most 10000 items')
    records, skipped = [], 0
    for entry in entries:
        request = _object(_object(entry).get('request'))
        url = request.get('url')
        if not isinstance(url, str) or len(url) > 8192:
            raise APIError(400, 'Invalid HAR request URL')
        try:
            parts = urlsplit(url)
            allowed = (parts.scheme == 'https' and parts.hostname == 'api.deadsimplechat.com'
                       and parts.port is None and parts.username is None and parts.password is None
                       and not parts.fragment and SEND_PATH.fullmatch(parts.path)
                       and request.get('method') == 'POST')
            if not allowed:
                skipped += 1
                continue
            query = parse_qsl(parts.query, keep_blank_values=True, max_num_fields=100)
        except ValueError:
            raise APIError(400, 'Invalid HAR URL or excessive query fields')
        headers = request.get('headers', [])
        query_fields = request.get('queryString', [])
        if (not isinstance(headers, list) or len(headers) > 200 or
                not isinstance(query_fields, list) or len(query_fields) > 100):
            raise APIError(400, 'Invalid HAR metadata arrays')
        header_names = set()
        for header in headers:
            name = _object(header).get('name')
            if not isinstance(name, str):
                raise APIError(400, 'Invalid HAR header name')
            header_names.add(name.lower())
        # Values intentionally never accessed; presence != correctness/necessity.
        auth_query = any(name == 'auth' for name, _ in query)
        auth_query |= any(_object(q).get('name') == 'auth' for q in query_fields)
        response = _object(entry.get('response'))
        status = response.get('status')
        if isinstance(status, bool) or not isinstance(status, int) or not (status == 0 or 100 <= status <= 599):
            raise APIError(400, 'Invalid HAR response status')
        records.append({
            'method': 'POST', 'origin': 'https://api.deadsimplechat.com',
            'path': '/consumer/api/v2/bot/{bot_id}/chatroom/{room_id}/message',
            'auth_query_present': auth_query,
            'authorization_header_present': 'authorization' in header_names,
            'http_status': status, 'api_acceptance': 'unverified', 'peer_delivery': 'unverified'})
        if len(records) > MAX_MATCHES:
            raise APIError(400, 'HAR matches exceed the local 500-record limit')
    return {'schema_version': 1, 'site': 'deadsimplechat', 'evidence_kind': 'untrusted_local_har_metadata',
            'records': records, 'skipped_entries': skipped, 'raw_values_retained': False,
            'auth_requirement_resolved': False, 'webhook_auth_verified': False,
            'external_requests': 0, 'messages_sent': 0, 'live_ready': False}
