from __future__ import absolute_import

import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mirai_project.settings')

app = Celery('mirai_project', namespace='CELERY')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks()

@app.task
def test():
    print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")