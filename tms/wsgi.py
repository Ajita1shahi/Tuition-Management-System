"""
WSGI config for tms project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

try:
	from django.core.wsgi import get_wsgi_application  # type: ignore
except Exception:
	def get_wsgi_application():
		raise RuntimeError(
			"Django is not installed or cannot be resolved in this environment. "
			"Install Django (e.g. pip install 'django>=5.2') or activate the correct virtual environment."
		)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tms.settings')

application = get_wsgi_application()
