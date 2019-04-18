# kkeomalaythong edit 2019-04-17: improved runtime of render_images()
# TODO: implement multithreading for DB API
from util import CNN
import os
import glob
import json
from util import bat
import sqlite3
import gc
import matplotlib.pyplot as plt
import ast
import zipfile
from keras.models import load_model
import shutil
import numpy as np
from scipy.signal import savgol_filter


# TODO: consider whether to put all of clean_graph() into insert_pulse()
def clean_graph(filename, graph=None, dy_cutoff=2000, dx_cutoff=.2, pulse_size=20):
    if graph is None:
        print('File is empty')

    zc_x, zc_y = graph[0], graph[1]

    # Identify pulses
    graph, pulse = list(), list()
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
                        pulse[i][1] = (pulse[i - 1][1] + pulse[i + 1][1]) / 2
                    elif dy[i + 2] < dy_cutoff:
                        pulse[i][1] = (pulse[i - 1][1] + pulse[i + 2][1]) / 2
                elif dy[i - 2] < dy_cutoff:
                    if dy[i + 1] < dy_cutoff:
                        pulse[i][1] = (pulse[i - 2][1] + pulse[i + 1][1]) / 2
                    elif dy[i + 2] < dy_cutoff:
                        pulse[i][1] = (pulse[i - 2][1] + pulse[i + 2][1]) / 2
            i += 1

    # Clean pulses
    cg = list()
    for k, pulse in enumerate(graph):
        i = 1
        while i < len(pulse):
            j = i

            # Count neighboring points
            while j < len(pulse) - 1 and graph_dy[k][j] <= dy_cutoff:
                j += 1

            # If there are enough neighbors, it's good
            if j - i >= pulse_size:
                cg.append(pulse[i:j])

            i = j + 1

    # Distance functions
    def dist(ax, ay, bx, by):
        return np.sqrt((ax - bx)**2 + (ay - by)**2)

    def dista(pair):
        return dist(pair[0][0], pair[0][1], pair[1][0], pair[1][1])

    # Clean pulses more
    cleaner_graph = list()
    smooth_graph = list()
    for pulse in cg:

        # Build smooth graph using Savitzky-Golay filter
        # Left param is all x values in current pulse, right param is smoothed y values
        # Params are zipped together then converted to list
        # This is the dark side of pythonic code
        smooth_pulse = list(zip([point[0] for point in pulse], savgol_filter(
            [point[1] for point in pulse], 17, 3)))
        smooth_graph.extend(smooth_pulse)

        # Build clean pulse
        # Iterate through zipped list of smooth_pulse and pulse, producing [[ax, ay],[bx, by]]
        # Keep only those where the absolute distance between pair 1 and pair 2 is less than 1/2 dy_cutoff
        # This is the even darker side of pythonic code
        cleaner_graph.append([pair[0] for pair in zip(
            pulse, smooth_pulse) if dista(pair) < dy_cutoff / 2])

    return cleaner_graph


# 0: Source ZC name, 1: image data, 2: classified, 3: metadata, 4: uid
def get_tables():
    conn = sqlite3.connect('../Bat_Echolocation_2019/db.sqlite3')
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [i[0] for i in c.fetchall()]
    return tables


# TODO: try adding the contents of clean_graph() to this function
def insert_pulse(uid, file_name, file):
    """ Clean ZC file and add to DB """
    conn = sqlite3.connect('../Bat_Echolocation_2019/db.sqlite3')
    c = conn.cursor()

    # If images table doesn't exist yet, make it
    if 'pulses' not in get_tables():
        with conn:
            query = '''CREATE TABLE pulses (name VARCHAR(255),
                                            raw BLOB,
                                            classification VARCHAR(255),
                                            metadata VARCHAR(255),
                                            uid INTEGER);'''
            c.execute(query)

    # Extract data from ZC file
    try:
        raw = list(bat.extract_anabat_zc(file))
    except Exception as e:
        print('Unexpected error processing file ', file, '- ', str(e))
        return

    # Metadata from ZC
    metadata = raw[3]
    metadata['date'] = metadata['date'].decode()
    metadata['pos'] = 0
    metadata['timestamp'] = str(metadata['timestamp'])
    metadata_str = json.dumps(metadata)

    # Get cleaned pulse data
    pulses = clean_graph(filename='', graph=[raw[0], raw[1]])

    # Add each pulse and associated metadata to DB
    c.execute('SELECT * from pulses;')
    found = c.fetchall()

    if not any(i[0] == file_name and i[4] == uid for i in found):
        with conn:
            for pulse in pulses:
                c.execute('INSERT INTO pulses VALUES (?, ?, ?, ?, ?);',
                          (file_name, str(pulse), '0', metadata_str, uid))


def insert_zip(uid, outdir, file_name, file):
    """Add all contents of zip file to DB"""

    # Extract zip and delete it
    z_name = outdir + '/' + 'temp.zip'
    z = open(z_name, 'wb')
    z.write(file)
    zip_data = zipfile.ZipFile(z_name, 'r')
    zip_data.extractall(outdir)
    zip_data.close()
    os.remove(z_name)

    # Select all valid files for processing
    # TODO- Extend with more filetypes.
    #       Make global list of accepted extensions?
    filenames = glob.glob(outdir + '/**/*#', recursive=True)
    filenames.extend(glob.glob(outdir + '/**/*.zip', recursive=True))
    filenames.extend(glob.glob(outdir + '/**/*.zca', recursive=True))

    # Recursively handle zip files, insert others to database.
    # TODO- extend with more filetypes
    for file in filenames:
        f = open(file, 'rb')
        z = f.read()
        if file.endswith('.zip'):
            subdir = os.paths.join(outdir, os.path.basename(file))
            os.mkdir(subdir)
            insert_zip(uid, subdir, os.path.basename(file), z)
        else:
            insert_pulse(uid, os.path.basename(file), z)

        # Delete file after processing
        f.close()
        os.remove(file)


def render_images(uid, outdir):
    """ Load images from DB and render """
    conn = sqlite3.connect('../Bat_Echolocation_2019/db.sqlite3')
    c = conn.cursor()

    # Load users image data
    c.execute('SELECT * FROM pulses WHERE uid=?;', (uid,))
    table = c.fetchall()
    table = [t for t in table if t[4] == uid]

    # Load CNN
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    model = load_model(__location__ + '/CNN200x300ep30.h5')

    fig, ax = plt.subplots()

    for i, row in enumerate(table):
        # Only render files that haven't been rendered yet
        if row[2] == '1':
            continue

        # Mark pulse as rendered
        with conn:
            c.execute(f"UPDATE pulses SET classification = '1' WHERE {str(i)} = ROWID;")

        # Convert DB string to 2d list
        pulse = ast.literal_eval(row[1])

        # Split pulse into x and y coords
        x = [point[0] for point in pulse]
        y = [point[1] for point in pulse]

        # Generate image path
        save_path = f"{outdir}/^_{row[0].replace('#', '')}_{i}.png"

        # Render the image
        ax.axis('off')
        ax.scatter(x, y)
        fig.savefig(save_path, format='png', Transparency=True, dpi=50)
        plt.cla()

        # Classify as normal or abnormal
        # TODO- perform at insert?
        if not CNN.classifyCNN(save_path, model) == 0:
            os.rename(save_path, save_path.replace('^', 'e'))
        else:
            os.rename(save_path, save_path.replace('^', 'a'))

    gc.collect()


def load_metadata(uid):
    conn = sqlite3.connect('../Bat_Echolocation_2019/db.sqlite3')
    c = conn.cursor()
    c.execute('SELECT * FROM pulses;')
    table = c.fetchall()

    return [[row[0], row[3]] for row in table if row[4] == uid]


def add_user_organization(username, organization):
    conn = sqlite3.connect('../Bat_Echolocation_2019/db.sqlite3')
    c = conn.cursor()

    # make "organizations" table if it doesn't already exist
    if 'organizations' not in get_tables():
        query = 'CREATE TABLE organizations (username VARCHAR(255), organization VARCHAR(255));'
        with conn:
            c.execute(query)

    # add new user and user-defined organization to "organizations" table
    with conn:
        query = 'INSERT INTO organizations VALUES (?, ?);'
        c.execute(query, (username, organization))


def erase_data(uid):
    """ Remove all user data from pulses table. Only call on logout """
    conn = sqlite3.connect('../Bat_Echolocation_2019/db.sqlite3')
    with conn:
        c = conn.cursor()
        c.execute('DELETE FROM pulses WHERE uid=?;', (uid,))


def make_zip(indir, outdir):
    """ Make a zip file with all generated pulses """

    # Make appropriate directories if possible
    noutdir = outdir + '/buildazip'
    try:
        os.makedirs(noutdir)
    except:
        pass
    try:
        os.mkdir(noutdir + '/abnormal')
        os.mkdir(noutdir + '/echolocation')
    except:
        pass

    # Get all files in directory
    onlyfiles = os.listdir(indir)

    # Organize files into echolocation or abnormal
    for file in onlyfiles:
        f = file
        file = indir + '/' + file
        if f.startswith('a_'):
            shutil.copy2(file, os.path.join(noutdir, 'abnormal', f))
        elif f.startswith('e_'):
            shutil.copy2(file, os.path.join(noutdir, 'echolocation', f))

    # Make zip and load into memory
    shutil.make_archive(outdir + '/results', 'zip', noutdir)
    z = open(outdir + '/results.zip', 'rb')
    m = z.read()
    z.close()

    # Delete everything
    shutil.rmtree(noutdir)

    return 'results.zip', m
