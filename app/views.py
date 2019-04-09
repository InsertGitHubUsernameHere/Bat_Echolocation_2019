#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app.models import Album, AlbumImage
from app.signupforms import SignUPForm
from util import db_API

from django.shortcuts import render, redirect
from django.http import HttpRequest
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.files.storage import FileSystemStorage
from django.views.generic import DetailView
from django.contrib.auth.models import User
from django.contrib.auth import views as auth_views

import os
from os import listdir
from os.path import isfile, join
import logging
import zipfile
import sys
import sqlite3
import pandas as pd
import shutil

path = os.getcwd()
while path[path.rfind('/' if path.startswith('/') else '\\') + 1:] != 'Bat_Echolocation_2019':
    path = os.path.dirname(path)
sys.path.insert(0, path)

def getfiles(request):
    # Files (local path) to put in the .zip
    # FIXME: Change this (get paths from DB etc)
    # might loop through the whole folder to generate a list of images name.
    filenames = ["media/file.png", "media/file2.png"]
    zip_subdir = "media/zipfile"
    zip_filename = "%s.zip" % zip_subdir

    s = StringIO.StringIO()

    # The zip compressor
    zf = zipfile.ZipFile(s, "w")

    for fpath in filenames:
        # Calculate path for file in zip
        fdir, fname = os.path.split(fpath)
        zip_path = os.path.join(zip_subdir, fname)

        # Add file, at correct path
        zf.write(fpath, zip_path)

    # Must close zip for all contents to be written
    zf.close()

    # Grab ZIP file from in-memory, make response with correct MIME-type
    resp = HttpResponse(s.getvalue(), mimetype="application/x-zip-compressed")
    # ..and correct content-disposition
    resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename
    print(resp)
    return resp

def upload(request):
    context = {}
    if request.method == 'POST':
        # Get uploaded file & filename
        uploaded_file = request.FILES['document']
        file_name = uploaded_file.name
        file = uploaded_file.read()

        # Get user id
        uid = request.user.id
        
        # Upload file to database. Switches on filetype.
        # TODO- extend list of acceptable/unacceptable filetypes

        # Upload ZIP containing ZC files
        if file_name.endswith('.zip'):
            outdir = os.path.join(os.getcwd(), 'media', str(uid), 'zip_results')
            try:
                os.makedirs(outdir)
            except:
                pass
            with sqlite3.connect('../db.sqlite3') as conn:
                db_API.insert_zip(conn, uid, outdir, file_name, file)
        # Upload ZC file
        else:
            with sqlite3.connect('../db.sqlite3') as conn:
                db_API.insert(conn, uid, file_name, file)

    if request.POST.get('Next'):
        return redirect('displayImages')
    return render(request, 'upload.html')

def displayImages(request):
    outdir = os.path.join(os.getcwd(), 'media')

    if request.method == 'GET':

        # Get user id
        uid = request.user.id
        
        # Make output directory if it doesn't exist already
        outdir = os.path.join(outdir, str(uid), 'test_images')
        try:
            os.makedirs(outdir)
        except:
            pass

        # Load images from database
        with sqlite3.connect('../db.sqlite3') as conn:
            db_API.load_images(conn, uid, outdir)

        echofiles = [f for f in listdir(outdir) if isfile(join(outdir, f)) and f.startswith('e_')]
        abnormfiles = [f for f in listdir(outdir) if isfile(join(outdir, f)) and f.startswith('a_')]

        print(abnormfiles)
        print(echofiles)

        return render(request, 'displayImages.html', {'echofiles': echofiles, 'abnormfiles' : abnormfiles})


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


def handler404(request, exception):
    print(exception)
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

def logout(request, next_page):
    uid = request.user.id
    outdir = os.path.join(os.getcwd(), 'media', str(uid))

    try:
        os.makedirs(outdir)
    except:
        pass

    shutil.rmtree(outdir)

    with sqlite3.connect('../db.sqlite3') as conn:
        db_API.erase_data(conn, uid)

    return auth_views.LogoutView.as_view()(request, next_page)
