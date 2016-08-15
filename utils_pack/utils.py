import os

from collections import Counter

import cPickle as pickle

def pickle_in(filepath):
    with open(filepath, 'rb') as f:
        data = pickle.load(f)
    return data

def pickle_out(filepath,data):
    with open(filepath, 'wb') as f:
        pickle.dump(data,f)

def ensure_dir(f):
    if not os.path.exists(f):
        os.makedirs(f)