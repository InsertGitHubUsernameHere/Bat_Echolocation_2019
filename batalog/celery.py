from __future__ import absolute_import, unicode_literals
from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'batalog.settings')
app = Celery('batalog', broker='amqp://localhost', include = ['batalog.tasks'])

app.config_from_object('django.conf:settings', namespace='CELERY')

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
