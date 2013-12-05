import os
import os.path
import sys
	
sys.path.append('/home/meguz.com/')
sys.path.append('/home/meguz.com/meguz')

os.environ['PYTHON_EGG_CACHE'] = '/home/meguz.com/egg_cache'
os.environ['DJANGO_SETTINGS_MODULE'] = 'meguz.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
