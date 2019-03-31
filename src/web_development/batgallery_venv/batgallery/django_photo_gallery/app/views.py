#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Kevin's code
import os
import sys
path = os.getcwd()
while path[path.rfind('/' if path.startswith('/') else '\\') + 1:] != 'Bat_Echolocation_2019':
    path = os.path.dirname(path)
sys.path.insert(0, path)
import sqlite3
from src.util.database import db_API
import pandas as pd
import fs
# End Kevin's code

from django.shortcuts import render, redirect
from django.http import HttpRequest
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import DetailView
from django.core.files.storage import FileSystemStorage
from app.signupforms import SignUPForm
from django.contrib.auth.models import User
from os import listdir
from os.path import isfile, join
from app.models import Album, AlbumImage
import logging
import zipfile

# Kevin's code
'''with sqlite3.connect('../django_photo_gallery/db.sqlite3') as conn:
    c = conn.cursor()
    c.execute('DELETE FROM images;')
    db_API.fetch_images(conn)
    db_API.fetch_images(conn, name='')
    db_API.fetch_images(conn)
    c.execute('DROP TABLE images;')
    c.execute('DROP TABLE users;')
    c.execute('CREATE TABLE users (username VARCHAR(255) PRIMARY KEY, password VARCHAR(255), ' \
              'email VARCHAR(255), first_name VARCHAR(255), last_name VARCHAR(255));')
    
    c.execute('CREATE TABLE images (username VARCHAR(255), name VARCHAR(255) PRIMARY KEY, raw BLOB,'
              ' classification VARCHAR(255), metadata VARCHAR(255), FOREIGN KEY (username) REFERENCES users(username))')
    
    c.execute('CREATE TABLE images (name VARCHAR(255) PRIMARY KEY, raw BLOB,'
              ' classification VARCHAR(255), metadata VARCHAR(255))')
              
    c.execute('SELECT * FROM users;')
    df = pd.DataFrame.from_records(c.fetchall(), columns=['username', 'password', 'email', 'first_name', 'last_name'])
    print(df)'''
# End Kevin's code

username = ''

def upload(request):
    context = {}
    if request.method == 'POST':
        uploaded_file = request.FILES['document']

        file_name = uploaded_file.name
        file = uploaded_file.read()

        # Zip of ZC files
        if file_name.endswith('.zip'):
            with zipfile.ZipFile(file, 'r') as z:
                for name in z.namelist():
                    if not (name.endswith('.\d\d#') or name.endswith('.zc')):
                        f = z.open(name)
                        with sqlite3.connect('../db.sqlite3') as conn:
                            db_API.insert(conn, username, name, f.read())
        # Single ZC file
        else:
            with sqlite3.connect('../db.sqlite3') as conn:
                db_API.insert(conn, username, file_name, file)

        #context['url'] = fs.url(uploaded_name)
    if request.POST.get('Next'):
        return redirect('displayImages')
    return render(request, 'upload.html')


def displayImages(request):
    outdir = os.path.join(os.getcwd(), 'media', 'test_images')
    if request.method == 'GET':
        with sqlite3.connect('../db.sqlite3') as conn:
            db_API.load_images(conn, username, outdir)

    onlyfiles = [f for f in listdir("media/test_images/") if isfile(join("media/test_images/", f))]
    return render(request, 'displayImages.html', {'onlyfiles': onlyfiles})


def gallery(request):
    list = Album.objects.filter(is_visible=True).order_by('-created')
    paginator = Paginator(list, 10)

    page = request.GET.get('page')
    try:
        albums = paginator.page(page)
    except PageNotAnInteger:
        albums = paginator.page(1)  # If page is not an integer, deliver first page.
    except EmptyPage:
        # If page is out of range (e.g.  9999), deliver last page of results.
        albums = paginator.page(paginator.num_pages)

    return render(request, 'gallery.html', {'albums': list})


class AlbumDetail(DetailView):
    model = Album

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(AlbumDetail, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the images
        context['images'] = AlbumImage.objects.filter(album=self.object.id)
        return context


def handler404(request):
    assert isinstance(request, HttpRequest)
    return render(request, 'handler404.html', None, None, 404)


def signup(request):
    if request.method == 'POST':
        form = SignUPForm(request.POST or None)

        if form.is_valid():
            form.save()
            return redirect('gallery')
        else:
            args = {'form': form}
            return render(request, 'signup.html', args)
    else:
        form = SignUPForm()

        args = {'form': form}
        return render(request, 'signup.html', args)
