'''end goal of code is to send data from ZC file to database'''
# next goal: send images to GUI

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

# grab uploaded ZC file from GUI, get its cleaned pulses, convert them into PNG images, and insert them into DB
def insert(conn, username, file_name, file):
    # get list of tables currently in DB and check whether table "images" exists in DB
    if 'images' not in get_tables(conn):
        c = conn.cursor()
        with conn:
            c.execute('CREATE TABLE images (name VARCHAR(255), raw BLOB, classification VARCHAR(255), metadata VARCHAR(255));')

    raw = list(bat.extract_anabat_zc(file))

    # obtain metadata from raw ZC file (here, it's a dict)
    metadata = raw[3]
    metadata['date'] = metadata['date'].decode()
    metadata['pos'] = 0
    metadata['timestamp'] = str(metadata['timestamp'])
    metadata_str = json.dumps(metadata)

    '''# assuming that GUI requests images w/ tagged metadata...
    metadata_split = metadata_str.split(',')
    print(metadata_split)
    metadata_split = [str.split('=') for str in metadata_split]
    print(metadata_split)
    dct = {key: value for (key, value) in metadata_split}
    print(dct)
    dct['species'] = ast.literal_eval(dct['species'])
    print(dct)'''

    pulses = data_processing.clean_graph(filename = '', graph=[raw[0], raw[1]])

    for pulse in enumerate(pulses):
        c = conn.cursor()
        with conn:
            c.execute('INSERT INTO images VALUES (?, ?, ?, ?);', (file_name, json.dumps(pulses), ' ', metadata_str,))

# 0: Source name, 1: Image data, 2: classification, 3: metadata, 4: username
def load_images(conn, username, outdir):
    c = conn.cursor()
    c.execute('SELECT * FROM images')   # TODO update to check for username

    fig, ax = plt.subplots()
    for row in c:
        pulse = json.loads(row[1])
        
        # get pulse points' coordinates
        x = [point[0] for point in pulse]
        y = [point[1] for point in pulse]

        # obtain a linear fit and classify
        #plyft = polyfit(x=x, y=y, deg=1)
        #classification = '/echolocation/' if plyft[1] < 0 else '/abnormal/'

        # create and save PNG files of pulses
        #save_path = os.path.realpath(f'{outdir}{classification}{zc_filename_split}_{i}.png')
        save_path = os.path.realpath(f'{outdir}{row[0]}_{i}.png')
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
