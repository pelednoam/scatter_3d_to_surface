bl_info = {
    "name": "Multi-modal visualization tool",
    "author": "Ohad Felsenstein & Noam Peled",
    "version": (1, 2),
    "blender": (2, 7, 2),
    "api": 33333,
    "location": "View3D > Add > Mesh > Say3D",
    "description": "Multi-modal visualization tool",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Add Mesh"}

import bpy
import os
import os.path as op
import sys
import importlib
import traceback
import logging

import sts_utils
importlib.reload(sts_utils)
import sts_panel
importlib.reload(sts_panel)
import colorbar_panel
importlib.reload(colorbar_panel)


color_surface = sts_panel.color_surface
set_colorbar_max_min = colorbar_panel.set_colorbar_max_min
change_cm = sts_panel.change_cm

def init(addon_prefs):
    code_fol = sts_utils.get_parent_fol(sts_utils.get_parent_fol())
    os.chdir(code_fol)


def main(addon_prefs=None):
    init(addon_prefs)
    try:
        current_module = sys.modules[__name__]
        sts_panel.init(current_module)
        colorbar_panel.init(current_module)
    except:
        print('The classes are already registered!')
        print(traceback.format_exc())


if __name__ == "__main__":
    main()


