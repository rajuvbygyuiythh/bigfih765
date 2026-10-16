"""Pure, local contract checks for documented integration shapes. No network I/O."""
import re
from urllib.parse import quote

from core import APIError


def mapping(value, label):
    if not isinstance(value, dict):
        raise APIError(400, label + ' must be an object')
    return value


def identity(value, label):
    if isinstance(value, bool) or not isinstance(value, (str, int)):
        raise APIError(400, label + ' must be a string or integer ID')
    value = str(value)
    if not re.fullmatch(r'[A-Za-z0-9_.:-]{1,128}', value):
        raise APIError(400, label + ' has an invalid ID format')
    return value


def content(value, label, limit=1000):
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise APIError(400, label + ' must contain 1–' + str(limit) + ' characters')
    return value


def inspect_minnit(payload, room_id):
    payload = mapping(payload, 'Webhook')
    room = identity(room_id, 'Expected room ID')
    if payload.get('type') != 'chat_message':
        return []  # Join/leave and moderation events do not generate messages.
    batch = payload.get('data')
    if not isinstance(batch, list) or len(batch) > 100:
        raise APIError(400, 'data must be an array of at most 100 items (local limit)')
    result = []
    for item in batch:
        item = mapping(item, 'Message')
        incoming_room = identity(item.get('chat_id'), 'chat_id')
        if incoming_room != room:
            raise APIError(400, 'Unexpected room ID')
        edited = item.get('edited', False)
        if not isinstance(edited, bool):
            raise APIError(400, 'edited must be a boolean')
        event = {'platform': 'minnit', 'kind': 'message_edit' if edited else 'message',
                 'event_id': identity(item.get('msg_id'), 'msg_id'), 'room_id': room,
                 'channel_id': identity(item.get('channel'), 'channel'),
                 'sender_id': identity(item.get('user_id'), 'user_id'),
                 'text': content(item.get('message'), 'message', 10000),
                 'automatic_reply_allowed': False}
        result.append(event)
    return result


def inspect_deadsimplechat(payload, room_id):
    payload = mapping(payload, 'Webhook')
    room = identity(room_id, 'Expected room ID')
    if payload.get('triggeredBy') != 'actionButtonPressed':
        raise APIError(400, 'Only the documented actionButtonPressed fixture is supported; other event shapes are not guessed')
    chat = mapping(payload.get('chatRoom'), 'chatRoom')
    if identity(chat.get('roomId'), 'roomId') != room:
        raise APIError(400, 'Unexpected room ID')
    user = mapping(payload.get('user'), 'user')
    action = mapping(payload.get('actionButtonPressed'), 'actionButtonPressed')
    # The enclosing message is the bot question, NOT user-authored incoming text.
    return [{'platform': 'deadsimplechat', 'kind': 'button_action',
             'event_id': identity(action.get('_id'), 'action event ID'), 'room_id': room,
             'sender_id': identity(user.get('_id'), 'user ID'),
             'action_id': identity(action.get('id'), 'action ID'),
             'parent_message_id': identity(action.get('messageId'), 'parent message ID'),
             'automatic_reply_allowed': False}]


def inspect_rumbletalk(payload, room_id):
    payload = mapping(payload, 'History fixture')
    room = identity(room_id, 'Expected room ID')
    if identity(payload.get('route_chat_id'), 'Route chat ID') != room:
        raise APIError(400, 'Unexpected room ID')
    response = mapping(payload.get('response'), 'REST response')
    if response.get('status') is not True:
        raise APIError(400, 'History response must have boolean status:true')
    rows = response.get('data')
    if not isinstance(rows, list) or len(rows) > 100:
        raise APIError(400, 'History data must be an array of at most 100 rows (local limit)')
    result = []
    for row in rows:
        row = mapping(row, 'History row')
        result.append({'platform': 'rumbletalk', 'kind': 'history_record',
                       'event_id': identity(row.get('messageId'), 'messageId'),
                       'room_id': room, 'room_scope_verified': False,
                       'scope_note': 'Room comes from local request-route context; response has no room ID',
                       'sender_id': identity(row.get('userId'), 'userId'),
                       'text': content(row.get('text'), 'text', 10000),
                       'automatic_reply_allowed': False})
    return result


def inspect_chatwee(payload, room_id):
    payload = mapping(payload, 'SSO fixture')
    room = identity(room_id, 'Expected chat ID')
    if identity(payload.get('request_chat_id'), 'Request chat ID') != room:
        raise APIError(400, 'Unexpected room ID')
    if payload.get('operation') != 'sso_login':
        raise APIError(400, 'Only the documented SSO-login result shape is inspected here')
    content(payload.get('response'), 'Session-ID response', 4096)
    # Never echo an SID, clientKey, cookie, user IP or raw response.
    return [{'platform': 'chatwee', 'kind': 'sso_session_shape', 'room_id': room,
             'session_value_present': True, 'session_value_redacted': True,
             'is_chat_message': False, 'room_scope_verified': False,
             'automatic_reply_allowed': False}]


def describe_send(platform, request):
    """Return a secret-free specification; never transmit or infer delivery."""
    request = mapping(request, 'Request')
    message = content(request.get('message'), 'message', 2000 if platform == 'rumbletalk' else 1000)
    if platform == 'minnit':
        chatname = content(request.get('chatname'), 'chatname', 50)
        channel = identity(request.get('channel'), 'channel')
        return {'method': 'POST', 'endpoint': 'DASHBOARD_PROVIDED_ORGANIZATION_ENDPOINT',
                'content_type': 'application/x-www-form-urlencoded',
                'auth_location': 'X-Key header (server-side secret; omitted)',
                'fields': {'action': 'sendmessage', 'chatname': chatname, 'channel': channel,
                           'username': 'Orbit Bot', 'message': message},
                'limit_note': '1000-character cap here is our local policy, not a verified Minnit vendor limit',
                'transmitted': False}
    if platform == 'deadsimplechat':
        bot = quote(identity(request.get('bot_id'), 'bot_id'), safe='')
        room = quote(identity(request.get('room_id'), 'room_id'), safe='')
        return {'method': 'POST',
                'endpoint': 'https://api.deadsimplechat.com/consumer/api/v2/bot/' + bot + '/chatroom/' + room + '/message',
                'content_type': 'application/json', 'auth_location': 'auth query parameter (server-side secret; omitted)',
                'fields': {'message': message},
                'limit_note': 'Documented message maximum: 1000. Optional per-user targeting not implemented here.',
                'transmitted': False}
    if platform == 'rumbletalk':
        room = quote(identity(request.get('room_id'), 'room_id'), safe='')
        if len(message.encode('utf-8')) > 2000:
            raise APIError(400, 'System message exceeds the documented 2000 UTF-8 byte limit')
        return {'method': 'POST', 'endpoint': 'https://api.rumbletalk.com/chats/' + room + '/messages',
                'content_type': 'application/json', 'auth_location': 'Authorization Bearer token (omitted)',
                'fields': {'text': message}, 'message_type': 'system',
                'limit_note': '2000 bytes, not characters; no private-DM parity claimed', 'transmitted': False}
    if platform == 'chatwee':
        raise APIError(409, 'SSO is not a message-send API; no documented chat-send route implemented')
    raise APIError(404, 'Unsupported contract')


def inspect(platform, payload, room_id):
    parsers = {'minnit': inspect_minnit, 'deadsimplechat': inspect_deadsimplechat,
               'rumbletalk': inspect_rumbletalk, 'chatwee': inspect_chatwee}
    if platform not in parsers:
        raise APIError(404, 'Unsupported contract')
    return {'mode': 'offline_contract_check', 'events': parsers[platform](payload, room_id),
            'external_requests': 0, 'messages_sent': 0, 'authenticated_webhook': False}


def classify_deadsimplechat_result(http_status, payload, timed_out=False):
    """Transport outcome is distinct from recipient-visible delivery."""
    if timed_out:
        return {'submission': 'unknown', 'peer_delivery': 'unverified', 'safe_to_blind_retry': False}
    if isinstance(http_status, bool) or not isinstance(http_status, int) or not 100 <= http_status <= 599:
        raise APIError(400, 'Invalid HTTP status')
    if http_status == 200 and isinstance(payload, dict) and payload.get('success') is True:
        return {'submission': 'api_accepted', 'peer_delivery': 'unverified', 'safe_to_blind_retry': False}
    if http_status in (400, 401, 403, 404, 429):
        return {'submission': 'rejected', 'peer_delivery': 'unverified', 'safe_to_blind_retry': False}
    return {'submission': 'unknown', 'peer_delivery': 'unverified', 'safe_to_blind_retry': False}


FIXTURES = {
    'minnit': {'expected_room_id': 'demo-room', 'payload': {'type': 'chat_message', 'data': [
        {'msg_id': 'demo-event-1', 'chat_id': 'demo-room', 'channel': 'main',
         'user_id': 'demo-user', 'message': 'Synthetic fixture only', 'edited': False}]}},
    'deadsimplechat': {'expected_room_id': 'demo-room', 'payload': {
        'triggeredBy': 'actionButtonPressed', 'chatRoom': {'roomId': 'demo-room'},
        'user': {'_id': 'demo-user'}, 'message': {'_id': 'bot-question', 'message': 'Bot-authored question'},
        'actionButtonPressed': {'_id': 'demo-action-event', 'id': 'answer-1', 'messageId': 'bot-question'}}},
    'rumbletalk': {'expected_room_id': 'demo-room', 'payload': {'route_chat_id': 'demo-room',
        'response': {'status': True, 'count': 1, 'data': [
            {'messageId': 101, 'userId': 7, 'text': 'Synthetic history record'}]}}},
    'chatwee': {'expected_room_id': 'demo-room', 'payload': {'request_chat_id': 'demo-room',
        'operation': 'sso_login', 'response': 'SYNTHETIC-SESSION-NOT-A-REAL-CREDENTIAL'}}
}
