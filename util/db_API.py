from util import data_processing
from util import CNN
import pandas as pd
import os
import glob
import numpy as np 
import json
from util import bat
import sqlite3
import gc
import matplotlib.pyplot as plt
import datetime
import ast
import zipfile
import numpy as np
from numpy.polynomial.polynomial import polyfit
from keras.models import load_model


def get_tables(conn):
    c = conn.cursor()
    c.execute('SELECT name FROM sqlite_master WHERE type=\'table\'')
    tables = [i[0] for i in c.fetchall()]
    return tables


# Clean ZC file and add to DB
def insert(conn, uid, file_name, file):

    # If images table doesn't exist yet, make it
    if 'images' not in get_tables(conn):
        c = conn.cursor()
        with conn:
            c.execute('CREATE TABLE images (name VARCHAR(255), raw BLOB, classification VARCHAR(255), metadata VARCHAR(255), uid INTEGER);')

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
    pulses = data_processing.clean_graph(filename = '', graph=[raw[0], raw[1]])

    # Add each pulse and associated metadata to DB
    with conn:
        c = conn.cursor()
        c.execute('SELECT * from images',)
        found = c.fetchall()
        if not any(i[0] == file_name for i in found):
            for pulse in pulses:    
                c.execute('INSERT INTO images VALUES (?, ?, ?, ?, ?);', (file_name, str(pulse), '0', metadata_str, uid))


# Add zip file to DB
def insert_zip(conn, uid, outdir, file_name, file):

    # Extract zip and delete it
    z_name = outdir + '/' + 'temp.zip'
    z = open(z_name, 'wb')
    z.write(file)
    zip_data = zipfile.ZipFile(z_name, 'r')
    zip_data.extractall(outdir)
    zip_data.close()
    os.remove(z_name)

    # Select all valid files for processing
    # TODO- extend with more filetypes. make global list of accepted extensions?
    filenames = glob.glob(outdir + '/**/*#', recursive=True)
    filenames.extend(glob.glob(outdir + '/**/*.zip', recursive=True))
    filenames.extend(glob.glob(outdir + '/**/*.zca', recursive=True))

    # Iterate through each file. Recursively handle zip files, insert others to database.
    # TODO- extend with more filetypes
    for file in filenames:
        f = open(file, 'rb')
        z = f.read()
        if file.endswith('.zip'):
            subdir = os.paths.join(outdir, os.path.basename(file))
            os.mkdir(subdir)
            insert_zip(conn, uid, subdir, os.path.basename(file), z)
        else:
            insert(conn, uid, os.path.basename(file), z)

        f.close()
        os.remove(file)

    # Empty directory when finished
    files = glob.glob(outdir)


# Load images from DB and render
# 0: Source name, 1: Image data, 2: classification, 3: metadata, 4: username
def load_images(conn, uid, outdir):

    # Load users image data
    c = conn.cursor()
    c.execute('SELECT * FROM images')
    table = c.fetchall()

    # Load CNN
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    model = load_model(__location__ + '/CNN200x300ep30.h5')

    fig, ax = plt.subplots()
    for i, row in enumerate(table):

        # Only render current user data
        if not row[4] == uid:
            continue

        # Only render files that haven't been rendered yet
        if row[2] == '1':
            continue

        # Mark pulse as rendered
        sql = ''' UPDATE images
                  SET classification = '1'
                  WHERE ''' + str(i) + ''' = ROWID'''
        c.execute(sql)

        # Convert DB string to 2d list
        pulse = ast.literal_eval(row[1])

        # Split pulse into x and y coords
        x = [point[0] for point in pulse]
        y = [point[1] for point in pulse]

        # Generate image path
        save_path = outdir + '/' + '^_' + row[0].replace('#', '') + '_' + str(i) + '.png'

        # Render the image
        ax.axis('off')
        ax.scatter(x, y)
        fig.savefig(save_path, transparent=True, dpi=50)
        plt.cla()
        gc.collect()

        # Classify as normal or abnormal
        # TODO- perform at insert?
        if CNN.classifyCNN(save_path, model) == 0:
            os.rename(save_path, save_path.replace('^', 'e'))
        else:
            os.rename(save_path, save_path.replace('^', 'a'))

def select_images(conn, name=None, classification=None):
    c = conn.cursor()
    if name is not None and classification is not None:  # both name==... and classification==...
        c.execute('SELECT * FROM images WHERE name=? AND classification=?;', (name, classification))
    elif name is not None:  # name==...
        c.execute('SELECT * FROM images WHERE name=?;', (name,))
    elif classification is not None:  # classification==...
        c.execute('SELECT * FROM images WHERE classification=?;', (classification,))
    else:  # both name==None and classification==None
        c.execute('SELECT * FROM images;')

    df = pd.DataFrame.from_records(c.fetchall(), columns=['name', 'raw', 'classification', 'metadata'])
    print(df)  # temporary

    # convert binary into PNG images and store them in .../media folder
    df.apply(lambda r: data_processing.binary_to_png(r[0], r[1], r[2]), axis=1)


# function to fetch user information (for back-end only)
def get_users(conn):
    c = conn.cursor()
    c.execute('SELECT username, password, first_name, last_name, organization FROM auth_user;')
    df = pd.DataFrame.from_records(c.fetchall(), columns=['username', 'password', 'first_name', 'last_name', 'organization'])
    print(df)

# Remove all user data from images table. Call on 'logout'
def erase_data(conn, uid) :
    c = conn.cursor()
    c.execute('DELETE FROM images WHERE uid=?', (uid,))