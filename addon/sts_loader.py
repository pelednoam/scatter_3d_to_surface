bl_info = {
    'name': 'scatter 3d to surf loader',
    'author': 'Noam Peled',
    'version': (1, 2),
    'blender': (2, 7, 2),
    'location': 'Press [Space], search for "sts_loader"',
    'category': 'Development',
}

import bpy
from bpy.types import AddonPreferences
from bpy.props import StringProperty, BoolProperty
import sys
import os
import importlib as imp

# How to crate a launcher in mac:
# http://apple.stackexchange.com/questions/115114/how-to-put-a-custom-launcher-in-the-dock-mavericks

def current_dir():
    return os.path.dirname(os.path.realpath(__file__))

def sts_dir():
    return bpy.path.abspath('//')

# https://github.com/sybrenstuvel/random-blender-addons/blob/master/remote_debugger.py
class ScattToSurfLoaderAddonPreferences(AddonPreferences):
    # this must match the addon name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __name__

    sts_folder = StringProperty(
        name='Path of the sts addon folder', description='', subtype='DIR_PATH',
        default='') #os.path.join(sts_dir(), 'sts_addon'))

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'sts_folder')


class ScattToSurfLoaderAddon(bpy.types.Operator):
    bl_idname = 'sts_addon.run_addon'
    bl_label = 'Run STS addon'
    bl_description = 'Runs the sts_addon addon'

    def execute(self, context):
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__name__].preferences
        # sts_root = os.path.abspath(addon_prefs.sts_folder)
        sts_root = bpy.path.abspath(addon_prefs.sts_folder)
        print('sts_root: {}'.format(sts_root))
        sys.path.append(sts_root)
        import sts_addon
        # If you change the code and rerun the addon, you need to reload MMVT_Addon
        imp.reload(sts_addon)
        print(sts_addon)
        sts_addon.main(addon_prefs)
        return {'FINISHED'}


def register():
    bpy.utils.register_class(ScattToSurfLoaderAddon)
    bpy.utils.register_class(ScattToSurfLoaderAddonPreferences)


def unregister():
    bpy.utils.unregister_class(ScattToSurfLoaderAddon)
    bpy.utils.unregister_class(ScattToSurfLoaderAddonPreferences)


if __name__ == '__main__':
    register()