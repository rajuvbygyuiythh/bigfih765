"""Explicit, non-executing, allowlisted server-only environment-file loader."""
import os
from pathlib import Path
import stat

ALLOWED = frozenset({'CONTROL_PLANE_TOKEN', 'DS_SHADOW_ENABLED', 'DS_AUTHORIZED_ROOM',
                     'DS_INSTANCE_ID', 'DS_ROOM_ID', 'DS_BOT_ID', 'DS_WEBHOOK_SECRET', 'DS_API_KEY'})


def load_private_env(path, env=None):
    env = os.environ if env is None else env
    try:
        source = Path(path)
        before = source.lstat()
        if not stat.S_ISREG(before.st_mode):
            raise ValueError()
        flags = os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0)
        with os.fdopen(os.open(source, flags), 'rb') as handle:
            info = os.fstat(handle.fileno())
            if ((before.st_dev,before.st_ino) != (info.st_dev,info.st_ino)
                    or not stat.S_ISREG(info.st_mode) or info.st_mode & 0o077
                    or (hasattr(os, 'getuid') and info.st_uid != os.getuid())):
                raise ValueError()
            raw = handle.read(16385)
        if len(raw) > 16384:
            raise ValueError()
        parsed = {}
        for line in raw.decode('utf-8-sig').splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            key, separator, value = line.partition('=')
            key, value = key.strip(), value.strip()
            if separator != '=' or key not in ALLOWED or key in parsed:
                raise ValueError()
            if value.startswith(('"', "'")):
                if len(value) < 2 or value[-1] != value[0]:
                    raise ValueError()
                value = value[1:-1]
            if any(ord(c) < 32 or ord(c) == 127 for c in value):
                raise ValueError()
            parsed[key] = value  # Literal only: never source/eval/interpolate.
        for key, value in parsed.items():
            env.setdefault(key, value)  # Existing process values always win.
        return sorted(parsed)  # Names only; never return values or file content.
    except (OSError, ValueError, UnicodeError):
        raise ValueError('Private env file rejected; use owner-only mode 600, UTF-8, unique allowlisted KEY=value lines. No values exposed.') from None
