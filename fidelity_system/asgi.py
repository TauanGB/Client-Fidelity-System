"""ASGI config for the fidelity system project."""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fidelity_system.settings")

application = get_asgi_application()
