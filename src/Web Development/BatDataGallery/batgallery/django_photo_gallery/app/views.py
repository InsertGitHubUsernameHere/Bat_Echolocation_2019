#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
print(os.getcwd())
path = os.getcwd()
while path[path.rfind('/')+1:] != 'Bat_Echolocation_2019':
    path = os.path.dirname(path)
print(path)
import sys
import sqlite3
sys.path.insert(0, path)
from src.util.database import db_API
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


def upload(request):
    context = {}
    if request.method == 'POST':
        uploaded_file = request.FILES['document']
        fs = FileSystemStorage()
        name = fs.save(uploaded_file.name, uploaded_file)

        with sqlite3.connect('../django_photo_gallery/db.sqlite3') as conn:
            c = conn.cursor()
            c.execute('DROP TABLE images;')
            db_API.insert(conn, fs.location, os.path.realpath(f'{fs.location}/pulses'))

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
