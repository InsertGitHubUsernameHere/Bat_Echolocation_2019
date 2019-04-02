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
from src.util import db_API
#import pandas as pd
# End Kevin's code

from django.shortcuts import render, redirect
from django.http import HttpRequest
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import DetailView
from django.core.files.storage import FileSystemStorage
from app.signupforms import SignUPForm
from django.contrib.auth.models import User
from os import listdir
from os.path import isfile, join, realpath
import ast
from app.models import Album, AlbumImage

# Test code
'''
with sqlite3.connect('../django_photo_gallery/db.sqlite3') as conn:
    # use for calling the DB API
    db_API.fetch_images(conn)
    db_API.fetch_images(conn, name='')
    db_API.fetch_images(conn)
    
    # use for querying the DB directly from here
    c = conn.cursor()
    c.execute('DELETE FROM images;')
    c.execute('DROP TABLE images;')
    c.execute('CREATE TABLE images (username VARCHAR(255), name VARCHAR(255) PRIMARY KEY, raw BLOB,'
              ' classification VARCHAR(255), metadata VARCHAR(255), FOREIGN KEY (username) REFERENCES users(username))')
    c.execute('CREATE TABLE images (name VARCHAR(255) PRIMARY KEY, raw BLOB,'
              ' classification VARCHAR(255), metadata VARCHAR(255))')
    c.execute('SELECT * FROM users;')
    df = pd.DataFrame.from_records(c.fetchall(), columns=['username', 'password', 'email', 'first_name', 'last_name'])
    print(df)
'''
# End test code


def upload(request):
    context = {}
    if request.method == 'POST':
        uploaded_file = request.FILES['document']
        fs = FileSystemStorage()
        name = fs.save(uploaded_file.name, uploaded_file)

        # acquire username from request
        username = request.user

        # send in uploaded ZC file to database
        with sqlite3.connect('../django_photo_gallery/db.sqlite3') as conn:
            #db_API.insert(conn, fs.location, uploaded_file.name, uploaded_file)
            db_API.insert(conn, username, uploaded_file.name, uploaded_file)  # adjusted for new "images" table with "username" (foreign key from "auth-user")

        context['url'] = fs.url(name)
    if request.POST.get('Next'):
        return redirect('displayImages')
    return render(request, 'upload.html', context)


def displayImages(request):
    onlyfiles = [f for f in listdir("media/test_images/") if isfile(join("media/test_images/", f))]
    print(onlyfiles)
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
