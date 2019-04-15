from util import data_processing
from util import CNN
import pandas as pd
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

# kkeomalaythong edit 2019-04-14: added in a specific path location for local db file
#     -project ended up creating the db file outside Bat_Echolocation_2019 folder instead of using existing one
db_path = os.path.realpath('../Bat_Echolocation_2019/db.sqlite3')
# end kkeomalaythong edit 2019-04-14


# 0: Source ZC name, 1: image data, 2: classified, 3: metadata, 4: uid
def get_tables():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [i[0] for i in c.fetchall()]
    return tables


# kkeomalaythong edit 2019-04-14: added function for obtaining output of a specific table - may remove later on
def select_table(table):
    if table not in get_tables():
        print(f'table "{table}" does not exist')
    else:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        # get column names of table
        c.execute(f'PRAGMA table_info({table});')
        columns = pd.DataFrame.from_records(c.fetchall()).iloc[:, 1]

        # get table
        c.execute(f'SELECT * FROM {table};')
        df_table = pd.DataFrame.from_records(c.fetchall(), columns=columns)
        return df_table
# end kkeomalaythong edit 2019-04-14


def insert_pulse(uid, file_name, file):
    """ Clean ZC file and add to DB """
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # If images table doesn't exist yet, make it
    if 'images' not in get_tables():
        with conn:
            query = '''CREATE TABLE images (name VARCHAR(255),
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
    pulses = data_processing.clean_graph(filename='', graph=[raw[0], raw[1]])

    # Add each pulse and associated metadata to DB
    # kkeomalaythong edit 2019-04-14: original "with conn:"code block is rearranged
    '''    with conn:
        c = conn.cursor()
        c.execute('SELECT * from images',)
        found = c.fetchall()
        if not any(i[0] == file_name and i[4] == uid for i in found):
            for pulse in pulses:
                c.execute('INSERT INTO images VALUES (?, ?, ?, ?, ?);',
                          (file_name, str(pulse), '0', metadata_str, uid))'''

    c.execute('SELECT * from images', )
    found = c.fetchall()

    if not any(i[0] == file_name and i[4] == uid for i in found):
        with conn:
            for pulse in pulses:
                c.execute('INSERT INTO images VALUES (?, ?, ?, ?, ?);',
                          (file_name, str(pulse), '0', metadata_str, uid))
    # end kkeomalaythong edit 2019-04-14


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
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Load users image data
    c.execute('SELECT * FROM images WHERE uid=?', (uid,))
    table = c.fetchall()
    table = [t for t in table if t[4] == uid]
    # Load CNN
    __location__ = os.path.realpath(os.path.join(
        os.getcwd(), os.path.dirname(__file__)))
    model = load_model(__location__ + '/CNN200x300ep30.h5')

    fig, ax = plt.subplots()
    for i, row in enumerate(table):
        # Only render files that haven't been rendered yet
        if row[2] == '1':
            continue

        # Mark pulse as rendered
        sql = '''UPDATE images
                 SET classification = '1'
                 WHERE ''' + str(i) + ''' = ROWID;'''
        conn.cursor().execute(sql)

        # Convert DB string to 2d list
        pulse = ast.literal_eval(row[1])

        # Split pulse into x and y coords
        x = [point[0] for point in pulse]
        y = [point[1] for point in pulse]

        # Generate image path
        save_path = outdir + '/' + '^_' + \
            row[0].replace('#', '') + '_' + str(i) + '.png'

        # Render the image
        ax.axis('off')
        ax.scatter(x, y)
        fig.savefig(save_path, transparent=True, dpi=50)
        plt.cla()
        gc.collect()

        # Classify as normal or abnormal
        # TODO- perform at insert?
        if not CNN.classifyCNN(save_path, model) == 0:
            os.rename(save_path, save_path.replace('^', 'e'))
        else:
            os.rename(save_path, save_path.replace('^', 'a'))


# kkeomalaythong edit 2019-04-14: method is commented out until purpose is either reevaluated or method is deleted
'''def select_images(name=None, classification=None):
    conn = sqlite3.connect('../db.sqlite3')
    c = conn.cursor()
    # both name==... and classification==...
    if name is not None and classification is not None:
        c.execute('SELECT * FROM images WHERE name=? AND classification=?;',
                  (name, classification))
    elif name is not None:  # name==...
        c.execute('SELECT * FROM images WHERE name=?;', (name,))
    elif classification is not None:  # classification==...
        c.execute('SELECT * FROM images WHERE classification=?;',
                  (classification,))
    else:  # both name==None and classification==None
        c.execute('SELECT * FROM images;')

    df = pd.DataFrame.from_records(
        c.fetchall(), columns=['name', 'raw', 'classification', 'metadata'])
    print(df)  # temporary

    # convert binary into PNG images and store them in .../media folder
    df.apply(lambda r: data_processing.binary_to_png(r[0], r[1], r[2]), axis=1)'''
# end kkeomalaythong edit 2019-04-14


def load_metadata(uid):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT * FROM images')
    table = c.fetchall()

    return [[row[0], row[3]] for row in table if row[4] == uid]


# kkeomalaythong edit 2019-04-14: changed db utility call lines
def add_user_organization(username, organization):
    conn = sqlite3.connect(db_path)
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
# end kkeomalaythong edit 2019-04-14


def erase_data(uid):
    """ Remove all user data from images table. Only call on logout """
    conn = sqlite3.connect(db_path)
    conn.cursor().execute('DELETE FROM images WHERE uid=?', (uid,))


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
            os.rename(file, os.path.join(noutdir, 'abnormal', f))
        elif f.startswith('e_'):
            os.rename(file, os.path.join(noutdir, 'echolocation', f))

    # Make zip and load into memory
    shutil.make_archive(outdir + '/results', 'zip', noutdir)
    z = open(outdir + '/results.zip', 'rb')
    m = z.read()
    z.close()

    # Delete everything
    shutil.rmtree(noutdir)
    shutil.rmtree(indir)

    return 'results.zip', m
