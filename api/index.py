import sys
import os

# Make the Django project importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gridquiz.settings')

from django.core.wsgi import get_wsgi_application
app = get_wsgi_application()

# Run migrations on cold start — idempotent, safe to repeat
from django.core.management import call_command
import logging
logger = logging.getLogger(__name__)
try:
    call_command('migrate', '--noinput', verbosity=0)
    call_command('loaddata', 'questions', verbosity=0)
except Exception as e:
    logger.error(f'Startup setup failed: {e}')
