'''end goal of code is to send data from ZC file to database'''

from util import data_processing
from numpy.polynomial.polynomial import polyfit
import csv, glob, gc, pandas as pd, matplotlib.pyplot as plt, numpy as np, os, PIL, sqlite3
from os.path import realpath
from PIL import Image

#conn = sqlite3.connect('')

# query handler module
def query_handler(queries):
    print(queries)

# PNG-binary conversion modules
def png_to_binary(dir):
    png_echo = glob.glob(realpath(f'{dir}/echolocation/*.png'), recursive=True)
    png_abnm = glob.glob(realpath(f'{dir}/abnormal/*.png'), recursive=True)

    df_echo = pd.DataFrame({'path': png_echo})
    df_abnm = pd.DataFrame({'path': png_abnm})

    # helper function for png_to_binary
    # creates a list of queries for each image and corresponsing raw binary data
    def create_query(names, raw_data_series):
        print(len(raw_data_series.iloc[0]))
        s = pd.Series(list(zip(names, raw_data_series)))
        s = s.apply(lambda t: f'INSERT INTO Images VALUES ({t[0]}, {t[1]});')
        return s

    if len(png_echo) > 0:
        df_echo['name'] = df_echo['path'].apply(lambda p: p[p.rfind('\\')+1:])
        df_echo['raw'] = df_echo['path'].apply(lambda p: (Image.open(p)).tobytes())
        df_echo['query'] = create_query(df_echo['name'], df_echo['raw'])
        query_handler(df_echo['query'])
        df_echo['path'].apply(lambda p: os.remove(p))

    if len(png_abnm) > 0:
        df_abnm['name'] = df_abnm['path'].apply(lambda p: p[p.rfind('\\')+1:])
        df_abnm['raw'] = df_abnm['path'].apply(lambda p: (Image.open(p)).tobytes())
        df_abnm['query'] = create_query(df_abnm['name'], df_abnm['raw'])
        query_handler(df_abnm['query'])
        df_abnm['path'].apply(lambda p: os.remove(p))

    # return query lists for both classes?

# decode incoming binary data into PNG file and save it to a directory
def binary_to_png(bin):
    pass

# fetch uploaded ZC files
def fetch_zc(indir, outdir):
    data_processing.zc_prc(indir, outdir)
    png_to_binary(outdir)
    #pass
