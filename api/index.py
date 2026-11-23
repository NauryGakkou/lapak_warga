import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

from django.core.wsgi import get_wsgi_application

_django_app = get_wsgi_application()


def app(environ, start_response):
    path = environ.get("PATH_INFO", "")
    for prefix in ("/api/index.py", "/api"):
        if path == prefix:
            environ["PATH_INFO"] = "/"
            break
        if path.startswith(prefix + "/"):
            environ["PATH_INFO"] = path[len(prefix):]
            break
    return _django_app(environ, start_response)