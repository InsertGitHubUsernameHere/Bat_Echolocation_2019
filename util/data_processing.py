import csv
import glob
import gc
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import sqlite3
import ast
from numpy.polynomial.polynomial import polyfit
from scipy.signal import savgol_filter
from util import bat
import json

def clean_graph(filename, graph=None, dy_cutoff=2000, dx_cutoff=.2, pulse_size=20):
    if graph is None:
        print('File is empty')

    zc_x, zc_y = graph[0], graph[1]

    # Identify pulses
    graph = list()
    pulse = list()
    prev_x = 0
    for x, y in zip(zc_x, zc_y):
        if x - prev_x <= dx_cutoff:
            pulse.append([x, y])
        elif len(pulse) < pulse_size:
            pulse = [[x, y]]
        else:
            graph.append(pulse)
            pulse = [[x, y]]
        prev_x = x

    # Get 1st derivative
    graph_dy = list()
    prev_y = 0
    for pulse in graph:
        dy = list()
        for x, y in pulse:
            dy.append(abs(y - prev_y))
            prev_y = y
        graph_dy.append(dy)

    # Smooth holes
    for dy, pulse in zip(graph_dy, graph):
        i = 1
        while i < (len(dy) - 2):
            if dy[i] > dy_cutoff:
                if dy[i - 1] < dy_cutoff:
                    if dy[i + 1] < dy_cutoff:
                        pulse[i][1] = (pulse[i - 1][1] + pulse[i + 1][1])/2
                    elif dy[i + 2] < dy_cutoff:
                        pulse[i][1] = (pulse[i - 1][1] + pulse[i + 2][1])/2
                elif dy[i - 2] < dy_cutoff:
                    if dy[i + 1] < dy_cutoff:
                        pulse[i][1] = (pulse[i - 2][1] + pulse[i + 1][1])/2
                    elif dy[i + 2] < dy_cutoff:
                        pulse[i][1] = (pulse[i - 2][1] + pulse[i + 2][1])/2
            i += 1

    # Clean pulses
    clean_graph = list()
    for k, pulse in enumerate(graph):
        i = 1
        while i < len(pulse):
            j = i

            # Count neighboring points
            while j < len(pulse) - 1 and graph_dy[k][j] <= dy_cutoff:
                j += 1

            # If there are enough neighbors, it's good
            if j - i >= pulse_size:
                clean_graph.append(pulse[i:j])

            i = j + 1

    # Distance functions
    def dist(ax, ay, bx, by):
        return np.sqrt((ax - bx)**2 + (ay - by)**2)

    def dista(pair):
        return dist(pair[0][0], pair[0][1], pair[1][0], pair[1][1])

    # Clean pulses more
    cleaner_graph = list()
    smooth_graph = list()
    for pulse in clean_graph:

        # Build smooth graph using Savitzky-Golay filter
        # Left param is all x values in current pulse, right param is smoothed y values
        # Params are zipped together then converted to list
        # This is the dark side of pythonic code
        smooth_pulse = list(zip([point[0] for point in pulse], savgol_filter([point[1] for point in pulse], 17, 3)))
        smooth_graph.extend(smooth_pulse)

        # Build clean pulse
        # Iterate through zipped list of smooth_pulse and pulse, producing [[ax, ay],[bx, by]]
        # Keep only those where the absolute distance between pair 1 and pair 2 is less than 1/2 dy_cutoff
        # This is the even darker side of pythonic code
        cleaner_graph.append([pair[0] for pair in zip(pulse, smooth_pulse) if dista(pair) < dy_cutoff / 2])

    return cleaner_graph


# fetch ZC file from GUI upload process located at indir
# output pulses as PNG images and place them in outdir
# also obtain metadata from ZC file
# PROGRESS TAG 2019-03-27
def zc_prc(indir, outdir):
    sep = '/' if indir.startswith('/') else '\\'
    zc_path = (glob.glob(f'{indir}/**/*#', recursive=True))[0]

    data = bat.extract_anabat(zc_path)
    raw = list(data)

    # obtain metadata from raw ZC file (here, it's a dict)
    metadata = raw[3]
    metadata['date'] = ''
    metadata_str = json.dumps(metadata)
    # create a txt file to hold this metadata temporarily
    zc_name = zc_path[zc_path.rfind(sep)+1:].replace('.', '_')
    #with open(f'{indir}/metadata/{zc_name}_metadata.txt', 'w+') as f:
    #    f.write(metadata_str)

    '''# assuming that GUI requests images w/ tagged metadata...
    metadata_split = metadata_str.split(',')
    print(metadata_split)
    metadata_split = [str.split('=') for str in metadata_split]
    print(metadata_split)
    dct = {key: value for (key, value) in metadata_split}
    print(dct)
    dct['species'] = ast.literal_eval(dct['species'])
    print(dct)'''

    pulses = clean_graph(filename=zc_path, graph=[raw[0], raw[1]])
    fig, ax = plt.subplots()

    for i, pulse in enumerate(pulses):
        # get pulse points' coordinates
        x = [point[0] for point in pulse]
        y = [point[1] for point in pulse]

        # obtain a linear fit and classify
        plyft = polyfit(x=x, y=y, deg=1)
        classification = '/echolocation/' if plyft[1] < 0 else '/abnormal/'

        # create and save PNG files of pulses
        zc_filename_split = zc_path.rsplit(".", 1)[0].rsplit(sep, 1)[-1]
        save_path = os.path.realpath(f'{outdir}{classification}{zc_filename_split}_{i}.png')
        ax.axis('off')
        ax.scatter(x, y)
        fig.savefig(save_path, transparent=True, dpi=50)
        plt.cla()
        gc.collect()

    return zc_name


# encode PNG images to binary
def png_to_binary(file):
    #paths_echo = pd.Series(glob.glob(os.path.realpath(f'{dir}/echolocation/*.png'), recursive=True))
    #paths_abnm = pd.Series(glob.glob(os.path.realpath(f'{dir}/abnormal/*.png'), recursive=True))
    #df = pd.DataFrame()

    #def bin_prc(path):
        #name = path[path.rfind('/' if dir.startswith('/') else '\\') + 1:]
        #with open(path, 'rb') as binfile:
    raw = sqlite3.Binary(file)
        #os.remove(path)
    return raw

    #if len(paths_echo) > 0:
        #df['echolocation'] = paths_echo.apply(lambda p: bin_prc(p))

    #if len(paths_abnm) > 0:
        #df['abnormal'] = paths_abnm.apply(lambda p: bin_prc(p))

    #return df


# decode incoming binary data into PNG file and save it to a directory
def binary_to_png(name, raw, classification):
    path = os.path.realpath(f'../django_photo_gallery/media/pulses/{classification}/{name}')
    with open(path, 'wb') as png_file:
        png_file.write(raw)
    os.remove(path)  # -> TESTING ONLY - REMOVES PNG FILES IN /pulses/... FOLDER
