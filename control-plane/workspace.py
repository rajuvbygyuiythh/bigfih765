"""Repeatable local configuration bootstrap; never starts a worker."""
from platforms import PLATFORMS


def seed_inactive_configurations(controller):
    existing = {item['adapter'] for item in controller.snapshot()['instances']}
    added = []
    for ident, platform in PLATFORMS.items():
        if ident == 'simulator' or not platform['configurable'] or ident in existing:
            continue
        added.append(controller.create(platform['name'] + ' workspace', ident))
        existing.add(ident)
    return {'added': len(added), 'instances': added, 'workers_started': 0}
