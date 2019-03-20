'''end goal of code is to send data from ZC file to database'''
# next goal: send images to GUI

from src.util import data_processing
import pandas as pd
import os


def get_tables(conn):
    c = conn.cursor()
    c.execute('SELECT name FROM sqlite_master WHERE type=\'table\'')
    tables = [i[0] for i in c.fetchall()]
    return tables


def create_table(conn, table):
    c = conn.cursor()

    if table == 'images':
        sql_query = f'CREATE TABLE {table} (name VARCHAR(255) PRIMARY KEY, classification VARCHAR(255), raw_data BLOB);'
    elif table == 'users':
            sql_query = f'CREATE TABLE {table} (username VARCHAR(255) PRIMARY KEY, password VARCHAR(255), ' \
                'email VARCHAR(255), first_name VARCHAR(255), mid_init CHAR(1), last_name VARCHAR(255));'

    with conn:
        c.execute(sql_query)


# grab uploaded ZC file from GUI, get its cleaned pulses, convert them into PNG images, and insert them into DB
def insert(conn, indir, outdir):
    data_processing.zc_prc(indir, outdir)
    df_queries = data_processing.png_to_binary(outdir)

    # get list of tables currently in DB
    tables = get_tables(conn)

    if 'images' not in tables:
        create_table(conn, 'images')

    def insert_image(conn, name, raw, classification):
        c = conn.cursor()
        with conn:
            c.execute('INSERT INTO images VALUES (?, ?, ?);', (name, classification, raw))

    for column in df_queries.columns:
        df_queries[column].apply(lambda q: insert_image(conn, q[0], q[1], column))


# fetch images from DB and pass them to GUI - IN PROGRESS
def fetch_images(conn, fields=None):
    c = conn.cursor()
    c.execute('SELECT * FROM images;')
    df = pd.DataFrame.from_records(c.fetchall(), columns=['name', 'classification', 'raw'])

    def decode_to_png(name, classification, raw):
        path = os.path.realpath(f'../django_photo_gallery/media/pulses/{classification}/{name}')
        with open(path, 'wb') as png_file:
            png_file.write(raw)

    df.apply(lambda r: decode_to_png(r[0], r[1], r[2]), axis=1)
