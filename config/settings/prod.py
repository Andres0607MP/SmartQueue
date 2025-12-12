from .base import *  # noqa
import os
import dj_database_url
import urllib.parse

DEBUG = False
ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', '*').split(',')

SKIP_MIGRATIONS = os.getenv('SKIP_MIGRATIONS', 'false') == 'true'

if SKIP_MIGRATIONS:
    # fallback DB to avoid connection errors
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
elif os.getenv('DATABASE_URL'):
    # Normalize known alternate schemes (e.g. Render may provide a mariadb:// URL)
    db_url = os.getenv('DATABASE_URL') or ''
    if db_url.startswith('mariadb://'):
        # dj_database_url expects mysql:// for MySQL-compatible backends
        db_url = 'mysql://' + db_url[len('mariadb://'):]
    # Parse the URL
    parsed = dj_database_url.parse(db_url, conn_max_age=600)

    # If parsing produced an unexpectedly short or empty DB name, try to
    # fall back to explicit env var `DJANGO_DB_NAME` (helps when the
    # provider UI truncated the value or an export issue happened).
    db_name = parsed.get('NAME') or ''
    if not db_name or len(db_name) < 4:
        fallback_name = os.getenv('DJANGO_DB_NAME')
        if fallback_name:
            parsed['NAME'] = fallback_name

    # Robustly try to recover the DB name if dj_database_url produced
    # an unexpectedly short value (some provider UIs / exports can
    # introduce truncation or formatting differences). We prefer the
    # explicit path component from urlparse if it appears longer.
    try:
        url_parts = urllib.parse.urlparse(db_url)
        path_name = (url_parts.path or '').lstrip('/')
        parsed_name = parsed.get('NAME') or ''
        if path_name and len(path_name) > len(parsed_name):
            parsed['NAME'] = path_name
    except Exception:
        # keep the original parsed value if anything goes wrong
        pass

    # Mask password for safer logging using urlparse (handles scheme://user:pwd@host)
    def _mask_url(purl: str) -> str:
        try:
            up = urllib.parse.urlparse(purl)
            if up.username:
                netloc = f"{up.username}:***@{up.hostname or ''}"
                if up.port:
                    netloc += f":{up.port}"
                return urllib.parse.urlunparse((up.scheme, netloc, up.path or '', up.params or '', up.query or '', up.fragment or ''))
        except Exception:
            pass
        return purl

    # Emit a small diagnostic to the process stdout so the deploy logs
    # show what DB name Django will use. This helps debugging deploys.
    try:
        masked = _mask_url(db_url)
        print(f"[prod settings] DATABASE_URL (masked): {masked}")
        print(f"[prod settings] Parsed DB NAME: {parsed.get('NAME')}")
    except Exception:
        pass

    DATABASES = {
        'default': parsed
    }
