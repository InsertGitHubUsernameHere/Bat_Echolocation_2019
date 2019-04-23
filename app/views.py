#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app.models import Album, AlbumImage
from app.signupforms import SignUPForm
from django.shortcuts import render, redirect
from django.http import HttpRequest
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import DetailView
from django.contrib.auth import views as auth_views

from batalog.tasks import render_images as render_pulses
from util import db_API
from util import graph

import os
from os import listdir
from os.path import isfile, join
import shutil

#first commit
def download_zip(request):
    uid = request.user.id

    outdir = os.path.join(os.getcwd(), 'media', str(uid))
    indir = os.path.join(os.getcwd(), 'media', str(uid), 'test_images')

    zip_filename, zip_file = db_API.make_zip(indir, outdir)

    # Grab ZIP file from in-memory, make response with correct content-type
    resp = HttpResponse(zip_file, content_type="application/x-zip-compressed")
    # ..and correct content-disposition
    resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename

    # Remove Zip file once it's been processed
    os.remove(os.path.join(outdir, zip_filename))

    return resp


def upload(request):
    return render(request, 'upload.html')


def render_images(request):
    # Get request data
    file_name = request.FILES['document'].name
    file = request.FILES['document'].read()
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
        db_API.insert_zip(uid, outdir, file_name, file)

    # Upload ZC file
    else:
        db_API.insert_pulse(uid, file_name, file)

    # Make output directory if it doesn't exist already
    outdir = os.path.join(os.getcwd(), 'media', str(uid), 'test_images')
    try:
        os.makedirs(outdir)
    except:
        pass

    # Render images to local storage
    render_pulses.delay(uid, outdir)

    return redirect('gallery', {'task_id': status.task_id})

def render_status(request):
    result = db_API.get_render_status(request.user.id)

    return HttpResponse({'status': result}, content_type='application/json')

def display_images(request):
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
    if request.method == 'POST':
        form = SignUPForm(request.POST or None)

        if form.is_valid():
            form.save()

            # Fetch registration information here and pass to DB API
            db_API.add_user_organization(request.POST['username'], request.POST['organization'])

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
