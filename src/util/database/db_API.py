from src.util import data_processing
import pandas as pd
import os
import glob
import numpy as np 
import json
from src.util import bat
import sqlite3
import gc
import matplotlib.pyplot as plt
import datetime
import ast
import zipfile
import numpy as np
from numpy.polynomial.polynomial import polyfit

def get_tables(conn):
    c = conn.cursor()
    c.execute('SELECT name FROM sqlite_master WHERE type=\'table\'')
    tables = [i[0] for i in c.fetchall()]
    return tables


'''def create_table(conn, table):
    c = conn.cursor()

    if table == 'images':
        sql_query = f'CREATE TABLE {table} (name VARCHAR(255) PRIMARY KEY, classification VARCHAR(255), raw_data BLOB);'
    elif table == 'users':
            sql_query = f'CREATE TABLE {table} (username VARCHAR(255) PRIMARY KEY, password VARCHAR(255), ' \
                'email VARCHAR(255), first_name VARCHAR(255), mid_init CHAR(1), last_name VARCHAR(255));'

    with conn:
        c.execute(sql_query)'''

# Clean ZC file and add to DB
def insert(conn, uid, file_name, file):
    # Get list of tables currently in DB and check whether table "images" exists in DB
    if 'images' not in get_tables(conn):
        c = conn.cursor()
        with conn:
            c.execute('CREATE TABLE images (name VARCHAR(255), raw BLOB, classification VARCHAR(255), metadata VARCHAR(255));')

    # Extract data from ZC file
    raw = list(bat.extract_anabat_zc(file))

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
                c.execute('INSERT INTO images VALUES (?, ?, ?, ?);', (file_name, str(pulse), ' ', metadata_str))

# Add zip file to DB
def insert_zip(conn, uid, outdir, file_name, file):
    # Extract zip and delete it
    z_name = outdir + '/' + uid + '_temp.zip'
    z = open(z_name, 'wb')
    z.write(file)
    zip_data = zipfile.ZipFile(z_name, 'r')
    zip_data.extractall(outdir)
    zip_data.close()
    os.remove(z_name)

    # make global list of accepted extensions?
    # TODO- extend with more filetypes
    filenames = glob.glob(outdir + '/**/*#', recursive=True)
    filenames.extend(glob.glob(outdir + '/**/*.zip', recursive=True))
    filenames.extend(glob.glob(outdir + '/**/*.zca', recursive=True))

    # Iterate through each file. Recursively handle zip files, insert others to database.
    # TODO- extend with more filetypes
    for file in filenames:
        f = open(file, 'rb')
        z = f.read()
        if file.endswith('.zip'):
            insert_zip(conn, uid, outdir, os.path.basename(file), z)
        else:
            insert(conn, uid, os.path.basename(file), z)

        f.close()
        os.remove(file)

    # Empty directory when finished
    files = glob.glob(outdir)
    for f in files:
        print(f)


# Load images from DB and render
# 0: Source name, 1: Image data, 2: classification, 3: metadata, 4: username
def load_images(conn, uid, outdir):

    # Load image data
    c = conn.cursor()
    c.execute('SELECT * FROM images')
    table = c.fetchall()

    fig, ax = plt.subplots()
    for i, row in enumerate(table):

        # Convert DB string to list
        pulse = ast.literal_eval(row[1])

        # Get x/y from DB
        x = [point[0] for point in pulse]
        y = [point[1] for point in pulse]

        if polyfit(x, y, 1)[1] < 0:
            classification = 'e_'
        else:
            classification = 'a_'

        # Create and save PNG files of pulses
        save_path = outdir + '/' + classification + row[0].replace('#', '') + '_' + str(i) + '.png'
        ax.axis('off')
        ax.scatter(x, y)
        fig.savefig(save_path, transparent=True, dpi=50)
        plt.cla()
        gc.collect()

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
