from __future__ import absolute_import, unicode_literals
from celery import task
from util import db_API

@task
def render_images(uid, outdir):
    db_API.render_images(uid, outdir)