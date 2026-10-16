"""Central capability registry. Configuration never implies a live connector."""
from copy import deepcopy


def entry(name, phase, configurable=True, fixture_label=None, blocker=None):
    return {'name': name, 'phase': phase, 'configurable': configurable,
            'fixture_label': fixture_label, 'local_ready': phase == 'synthetic',
            'live_ready': False,
            'start_blocker': blocker or 'Live connector is not implemented or authorized; configuration only.'}


PLATFORMS = {
    'simulator': entry('Synthetic sandbox', 'synthetic'),
    'minnit': entry('Minnit', 'diagnostic_connector', fixture_label='Minnit · message batch',
                    blocker='Fleet start stays disabled. Use Minnit diagnostics for a server-configured, operator-approved single-room test; live validation is pending.'),
    'deadsimplechat': entry('DeadSimpleChat', 'shadow_intake', fixture_label='DeadSimpleChat · button action',
                    blocker='Shadow intake is implemented but disabled until private setup; provider auth/sender/peer delivery remain unverified. Fleet Start stays disabled.'),
    'rumbletalk': entry('RumbleTalk', 'offline_contract', fixture_label='RumbleTalk · REST history snapshot'),
    'chatwee': entry('Chatwee', 'offline_identity', fixture_label='Chatwee · redacted SSO result'),
    'chatblink': entry('Chatblink', 'needs_contract'),
    'strangermeetup': entry('StrangerMeetup', 'needs_contract'),
    'chatango': entry('Chatango', 'needs_contract'),
    'chatiw': entry('Chatiw', 'needs_contract'),
    'chatzy': entry('Chatzy', 'restricted', configurable=False,
                    blocker='Behavior-modifying scripts are restricted; operator-approved alternative required.'),
    'chitchat': entry('Chitchat reference', 'reference', configurable=False,
                      blocker='Historical baseline only; no current supported integration established.'),
    'joingy': entry('Joingy source reference', 'reference', configurable=False,
                    blocker='Static upstream source reference only; no verified supported integration.'),
    'isexychat': entry('Isexychat source reference', 'reference', configurable=False,
                       blocker='Static upstream source reference only; no verified supported integration.')
}


def registry():
    return [{'id': key, **deepcopy(value)} for key, value in PLATFORMS.items()]
