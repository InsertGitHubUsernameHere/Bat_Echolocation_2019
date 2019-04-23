from __future__ import absolute_import, unicode_literals
from .celery import app
from util import db_API

@app.task
def render_images(uid, outdir):
    db_API.render_images(uid, outdir)