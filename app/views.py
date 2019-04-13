#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app.models import Album, AlbumImage
from app.signupforms import SignUPForm
from util import db_API
from util import graph
from django.shortcuts import render, redirect
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import DetailView
from django.contrib.auth import views as auth_views

import os
from os import listdir
from os.path import isfile, join
import sys
import shutil

path = os.getcwd()
while path[path.rfind('/' if path.startswith('/') else '\\') + 1:] != 'Bat_Echolocation_2019':
    path = os.path.dirname(path)
sys.path.insert(0, path)


def download_zip(request):
    uid = request.user.id

    outdir = os.path.join(os.getcwd(), 'media', str(uid))
    indir = os.path.join(os.getcwd(), 'media', str(uid), 'test_images')

    zip_filename, zip_file = db_API.make_zip(indir, outdir)

    # Grab ZIP file from in-memory, make response with correct MIME-type
    resp = HttpResponse(zip_file, content_type="application/x-zip-compressed")
    # ..and correct content-disposition
    resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename
    print(resp)
    return resp


def upload(request):
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
            outdir = os.path.join(os.getcwd(), 'media',
                                  str(uid), 'zip_results')
            try:
                os.makedirs(outdir)
            except:
                pass
            db_API.insert_zip(uid, outdir, file_name, file)

        # Upload ZC file
        else:
            db_API.insert_pulse(uid, file_name, file)

    if request.POST.get('Next'):
        return redirect('displayImages')
    return render(request, 'upload.html')


def renderImages(request):
    HttpResponseRedirect('render')

    # Get user id
    uid = request.user.id

    # Make output directory if it doesn't exist already
    outdir = os.path.join(os.getcwd(), 'media', str(uid), 'test_images')
    try:
        os.makedirs(outdir)
    except:
        pass

    # Load images from database
    db_API.load_images(uid, outdir)

    return redirect('display')


def displayImages(request):
    uid = request.user.id
    outdir = os.path.join(os.getcwd(), 'media', str(uid), 'test_images')

    # Make list of echolocation and abnormal files
    echofiles = [f for f in listdir(outdir) if isfile(
        join(outdir, f)) and f.startswith('e_')]
    abnormfiles = [f for f in listdir(outdir) if isfile(
        join(outdir, f)) and f.startswith('a_')]

    params = {'echofiles': echofiles, 'abnormfiles': abnormfiles}

    return render(request, 'display.html', params)


def draw_graph(request):
    metadata = db_API.load_metadata(request.user.id)
    graph.draw_graph(metadata, request.user.id)
    return render(request, 'graph.html')


def gallery(request):

    list = Album.objects.filter(is_visible=True).order_by('-created')
    paginator = Paginator(list, 10)

    page = request.GET.get('page')
    try:
        albums = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        albums = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g.  9999), deliver last page of results.
        albums = paginator.page(paginator.num_pages)

    return render(request, 'gallery.html', {'albums': albums})


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
    #print('in signup')
    if request.method == 'POST':
        form = SignUPForm(request.POST or None)

        if form.is_valid():
            form.save()

            # Fetch registration information here and pass to DB API
            # commented out until "organization" entry
            #db_API.add_user_organization(request.POST['username'], request.POST['organization'])

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

    db_API.erase_data(uid)

    return auth_views.LogoutView.as_view()(request, next_page)
