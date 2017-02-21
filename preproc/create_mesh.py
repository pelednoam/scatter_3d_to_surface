import numpy as np
from scipy.spatial import Delaunay
import scipy.io as sio
import os.path as op
import matplotlib.pyplot as plt

from preproc import trig_utils
from preproc import utils


def create_mesh(verts, perim_threshold, faces_perim_fname, mesh_ply_fname, faces_verts_out_fname):
    faces, perim = calc_faces_perim(verts, faces_perim_fname)
    inds = [k for k, p in enumerate(perim) if p > perim_threshold]
    faces = np.delete(faces, inds, 0)
    utils.calc_ply_faces_verts(verts, faces, faces_verts_out_fname, overwrite=True)
    utils.write_ply_file(verts, faces, mesh_ply_fname)


def calc_perim_cutoff(verts, faces_perim_fname='', plot_hist=True):
    faces, perim = calc_faces_perim(verts, faces_perim_fname)
    perim = np.array(perim)
    threshold = np.percentile(perim, 97)
    inds = np.where(perim > threshold)[0]
    perim = np.delete(perim, inds, 0)
    plt.hist(perim, bins=100)
    cutoff = np.mean(perim) + np.std(perim)
    plt.axvline(x=cutoff, color='k', linestyle='--')
    plt.show()
    return cutoff


def calc_faces_perim(verts, faces_perim_fname=''):
    if op.isfile(faces_perim_fname):
        faces, perim = utils.load(faces_perim_fname)
    else:
        verts_tup = [(x, y, z) for x, y, z in verts]
        tris = Delaunay(verts_tup)
        faces = tris.simplices
        print(faces.shape, verts.shape)
        perim = [trig_utils.perimeter(verts[poly]) for poly in faces]
        utils.save((faces, perim), faces_perim_fname)
    return faces, perim


def load_verts_data(root_fol, mat_fname):
    input_fname = op.join(root_fol, mat_fname)
    d = sio.loadmat(input_fname)
    data = d['DiffMuscle']
    verts = data[:, :3]
    values = data[:, 3]
    values[np.isnan(values)] = 0
    return verts, values


def main(root_fol, data_name, func_name, perim_threshold=0, plot_perim_hist=True):
    mat_fname = '{}.mat'.format(data_name)
    ply_fname = op.join(root_fol, '{}.ply'.format(data_name))
    faces_verts_fname = op.join(root_fol, '{}_faces_verts.npy'.format(data_name))
    values_fname = op.join(root_fol, '{}_values.npy'.format(data_name))
    faces_perim_fname = op.join(root_fol, '{}_faces_perim.pkl'.format(data_name))

    verts, values = load_verts_data(root_fol, mat_fname)
    if func_name in ['all', 'plot_perim_hist']:
        new_perim_threshold = calc_perim_cutoff(verts, faces_perim_fname, plot_perim_hist)
        if perim_threshold == 0:
            perim_threshold = new_perim_threshold
    if func_name in ['all', 'create_mesh']:
        create_mesh(verts, perim_threshold, faces_perim_fname, ply_fname, faces_verts_fname)
        np.save(values_fname, values)


if __name__ == '__main__':
    root_fol = '/home/npeled/Documents/reza'
    data_name = 'DiffMuscle2'
    func_name = 'all' #'plot_perim_hist'
    perim_threshold = 0
    plot_perim_hist = True
    main(root_fol, data_name, func_name, perim_threshold, plot_perim_hist)
    print('finish!')

