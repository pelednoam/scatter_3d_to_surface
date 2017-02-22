import os.path as op
import numpy as np
from collections import Counter
import traceback
import os
from addon.scripts.scripts_utils import Bag
from addon.scripts import scripts_utils as su
try:
    import cPickle as pickle
except:
    import pickle

PLY_HEADER = 'ply\nformat ascii 1.0\nelement vertex {}\nproperty float x\nproperty float y\nproperty float z\n' + \
             'element face {}\nproperty list uchar int vertex_index\nend_header\n'


get_parent_fol = su.get_parent_fol

def save(obj, fname):
    with open(fname, 'wb') as fp:
        # protocol=2 so we'll be able to load in python 2.7
        pickle.dump(obj, fp)


def load(fname):
    with open(fname, 'rb') as fp:
        obj = pickle.load(fp)
    return obj


def calc_ply_faces_verts(verts, faces, out_file, overwrite=True):
    if overwrite or op.isfile(out_file):
        _faces = faces.ravel()
        faces_arg_sort = np.argsort(_faces)
        faces_sort = np.sort(_faces)
        faces_count = Counter(faces_sort)
        max_len = max([v for v in faces_count.values()])
        lookup = np.ones((verts.shape[0], max_len)) * -1
        diff = np.diff(faces_sort)
        n = 0
        for ind, (k, v) in enumerate(zip(faces_sort, faces_arg_sort)):
            lookup[k, n] = v
            n = 0 if ind < len(diff) and diff[ind] > 0 else n+1
        np.save(out_file, lookup.astype(np.int))
        if len(_faces) != int(np.max(lookup)) + 1:
            raise Exception('Wrong values in lookup table! ' + \
                'faces ravel: {}, max looup val: {}'.format(len(_faces), int(np.max(lookup))))
    else:
        print('File already exists ({})'.format(out_file))


def write_ply_file(verts, faces, ply_file_name, write_also_npz=False):
    try:
        verts_num = verts.shape[0]
        faces_num = faces.shape[0]
        faces = np.hstack((np.ones((faces_num, 1)) * faces.shape[1], faces))
        with open(ply_file_name, 'w') as f:
            f.write(PLY_HEADER.format(verts_num, faces_num))
        with open(ply_file_name, 'ab') as f:
            np.savetxt(f, verts, fmt='%.5f', delimiter=' ')
            np.savetxt(f, faces, fmt='%d', delimiter=' ')
        if write_also_npz:
            np.savez('{}.npz'.format(op.splitext(ply_file_name)[0]), verts=verts, faces=faces)
        return True
    except:
        print('Error in write_ply_file! ({})'.format(ply_file_name))
        print(traceback.format_exc())
        return False


def should_run(function, func_name):
    return 'all' in  function or func_name in function


def make_dir(fol):
    if not op.isdir(fol):
        os.makedirs(fol)
    return fol
