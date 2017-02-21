# The setup suppose to run *before* installing python libs, so only python vanilla can be used here

import os
import os.path as op
from preproc import utils
import shutil
import traceback
import glob

TITLE = 'ScattToSurf Installation'
BLENDER_WIN_DIR = 'C:\Program Files\Blender Foundation\Blender'


def install_reqs(only_verbose=False):
    import pip
    pip.main(['install', '--upgrade', 'pip'])
    retcode = 0
    reqs_fname = op.join(utils.get_parent_fol(levels=2), 'requirements.txt')
    with open(reqs_fname, 'r') as f:
        for line in f:
            if only_verbose:
                print('Trying to install {}'.format(line.strip()))
            else:
                pipcode = pip.main(['install', line.strip()])
                retcode = retcode or pipcode
    return retcode


def main(args):
    # 1) Install dependencies from requirements.txt (created using pipreqs)
    if utils.should_run(args, 'install_reqs'):
        install_reqs(args.only_verbose)

    # 2) Install the addon in Blender (depends on resources and links)
    if utils.should_run(args, 'install_addon'):
        from addon.scripts import install_addon
        install_addon.wrap_blender_call(args.only_verbose)

    print('Finish!')


def print_help():
    str = 'functions: install_reqs, install_addon'
    print(str)


if __name__ == '__main__':
    import argparse
    from preproc import args_utils as au
    parser = argparse.ArgumentParser(description='MMVT Setup')
    parser.add_argument('-l', '--links', help='links folder name', required=False, default='links')
    parser.add_argument('-g', '--gui', help='choose folders using gui', required=False, default='1', type=au.is_true)
    parser.add_argument('-v', '--only_verbose', help='only verbose', required=False, default='0', type=au.is_true)
    parser.add_argument('-f', '--function', help='functions to run', required=False, default='all', type=au.str_arr_type)
    args = utils.Bag(au.parse_parser(parser))
    if 'help' in args.function:
        print_help()
    else:
        main(args)
