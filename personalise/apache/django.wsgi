import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

path = '/home/ad10g08/personal'
if path not in sys.path:
    sys.path.append(path)

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

