import numpy as np
from scipy.spatial import Delaunay
import scipy.io as sio
import os.path as op
import matplotlib.pyplot as plt
import shutil
import glob

try:
    from preproc import trig_utils
    from preproc import utils
    from preproc import args_utils as au
except:
    pass

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
    input_file_type = utils.file_type(input_fname)
    if input_file_type == 'mat':
        d = sio.loadmat(input_fname)
        var_name = utils.get_matlab_var_name(d)
        data = d[var_name]
    elif input_file_type == 'npy':
        data = np.load(input_fname)
    elif input_fname == 'csv':
        data = np.genfromtxt(input_fname, dtype=float, delimiter=',')
    verts = data[:, :3]
    values = data[:, 3]
    values[np.isnan(values)] = 0
    return verts, values


def copy_files(root_fol, data_name):
    new_blend_fname = op.join(root_fol, '{}.blend'.format(data_name))
    create_new_blend_file = True
    if op.isfile(new_blend_fname):
        ret = input("The blend file {} already exist, overwrite (y/n)? ".format(new_blend_fname))
        if not au.is_true(ret):
            create_new_blend_file = False
    if create_new_blend_file:
        shutil.copy(op.join(root_fol, 'empty_surface.blend'), new_blend_fname)
    utils.make_dir(op.join(root_fol, 'cm'))
    cm_fol = op.join(utils.get_parent_fol(__file__, 2), 'resources', 'cm')
    for cm_file in glob.glob(op.join(cm_fol, '*.npy')):
        new_cm_fname = op.join(root_fol, 'cm', cm_file.split(op.sep)[-1])
        shutil.copy(cm_file, op.join(root_fol, 'cm', new_cm_fname))


def main(root_fol, data_name, function, perim_threshold=0, plot_perim_hist=True):
    mat_fname = '{}.mat'.format(data_name)
    ply_fname = op.join(root_fol, '{}.ply'.format(data_name))
    faces_verts_fname = op.join(root_fol, '{}_faces_verts.npy'.format(data_name))
    values_fname = op.join(root_fol, '{}_values.npy'.format(data_name))
    faces_perim_fname = op.join(root_fol, '{}_faces_perim.pkl'.format(data_name))
    verts, values = load_verts_data(root_fol, mat_fname)

    if utils.should_run(function, 'plot_perim_hist'):
        new_perim_threshold = calc_perim_cutoff(verts, faces_perim_fname, plot_perim_hist)
        if perim_threshold == 0:
            perim_threshold = new_perim_threshold

    if utils.should_run(function, 'create_mesh'):
        create_mesh(verts, perim_threshold, faces_perim_fname, ply_fname, faces_verts_fname)
        np.save(values_fname, values)


    if utils.should_run(function, 'copy_files'):
        copy_files(root_fol, data_name)


def help():
    print('''
        -d: Data file name, without the suffix ('data' for example) points_num x 4, where the first 3 columns are the
            x,y,z coordinates, and the fourth is the values. The supported data types are mat (matlab), npy (python)
            and csv.
        -r: Root folder, where the data file is located
        -f: Which function to run:
            plot_perim_hist: Plot the faces perimeters histogram
            create_mesh: Create the mesh file. The faces perimeters threshold is taken from the faces perimeters histogram
                (mean + std) or from the cmd arguments
            all (default): Run all of the above
        --plot_perim_hist: Whether to plot the perimeters histogram or not (default is True)
        --perim_threshld: Set the perim threshold and not taking it from the hist (default is 0, so it's taken from the
                          faces perimeters histogram (mean + std)

    Example: python -m preproc.create_mesh -d file-name -r root-fol
    ''')


def read_cmd_args(argv=None):
    import argparse
    parser = argparse.ArgumentParser(description='Scatter 3D to Surface')
    parser.add_argument('-d', '--data_name', help='data file name', required=True)
    parser.add_argument('-r', '--root_fol', help='data file folder', required=True)
    parser.add_argument('-f', '--function', help='function name', required=False, default='all', type=au.str_arr_type)
    parser.add_argument('--plot_perim_hist', help='plt perim hist', required=False, default=True, type=au.is_true)
    parser.add_argument('--perim_threshold', help='faces perim threshold', required=False, default=0, type=float)
    parser.add_argument('--n_jobs', help='cpu num', required=False, default=-1)
    args = utils.Bag(au.parse_parser(parser, argv))
    if not op.isdir(args.root_fol):
        raise Exception('Root fol is not a dir!')
    input_fname = op.join(args.root_fol, '{}.mat'.format(args.data_name))
    if not op.isfile(input_fname):
        raise Exception("Can't find {}!".format(input_fname))
    return args


if __name__ == '__main__':
    import sys
    from os import environ as env
    # argv = None
    # if env.get('STS_HOME', '') != '' and op.isdir(env.get('STS_HOME', '')):
    #     argv = utils.Bag(root_fol=env['STS_HOME'])
    #     print('Root folder is {}'.format(env['STS_HOME']))
    if len(sys.argv) == 1 or sys.argv[1] in ['--help', '-h']:
        help()
    else:
        args = read_cmd_args()
        main(args.root_fol, args.data_name, args.function, args.perim_threshold, args.plot_perim_hist)
        print('finish!')

    # root_fol = '/home/npeled/Documents/reza'
    # data_name = 'DiffMuscle2'
    # func_name = 'all' #'plot_perim_hist'
    # perim_threshold = 0
    # plot_perim_hist = True

