from __future__ import absolute_import, unicode_literals
from celery import shared_task
from util import db_API

@shared_task(name="render_images")
def render_images(uid, outdir):
    db_API.render_images(uid, outdir)
