import bpy
import os.path as op
import importlib
import glob
import sys
import time
import numpy as np
import os.path as op

import traceback

import sts_utils

bpy.types.Scene.ply_file = bpy.props.StringProperty(
    name="hoc file",
    description="",
    subtype="FILE_PATH")


def _addon():
    return STSPanel.addon


def load_ply_file():
    ply_fname = bpy.path.abspath(bpy.context.scene.ply_file)
    print('Loading ply file {}'.format(ply_fname))
    if op.isfile(ply_fname):
        bpy.ops.import_mesh.ply(filepath=ply_fname)
        cur_obj = bpy.data.objects['DiffMuscle2']
        cur_obj.select = True
        bpy.ops.object.shade_smooth()
        cur_obj.hide = False
        cur_obj.name = 'DiffMuscle2'
        cur_obj.active_material = bpy.data.materials['Activity_map_mat']
        return True
    else:
        return False


def process_ply():
    cm = bpy.context.scene.colorbar_files.replace('-', '_')
    set_values_variables()
    change_cm(cm)
    _addon().set_colorbar_max_min(STSPanel.data_max, STSPanel.data_min)
    color_surface(cm)


def color_surface(cm):
    root_fol = bpy.path.abspath('//')
    colormap_fname = op.join(root_fol, 'cm', '{}.npy'.format(cm))
    print('Coloring using {}'.format(colormap_fname))
    cm = np.load(colormap_fname)
    colors_indices = ((np.array(STSPanel.vert_values) - STSPanel.data_min) * STSPanel.colors_ratio).astype(int)
    # take care about values that are higher or smaller than the min and max values that were calculated (maybe using precentiles)
    colors_indices[colors_indices < 0] = 0
    colors_indices[colors_indices > 255] = 255
    verts_colors = cm[colors_indices]

    scn = bpy.context.scene
    valid_verts = range(STSPanel.vert_values.shape[0])

    basename = sts_utils.namebase(bpy.path.abspath(bpy.context.scene.ply_file))
    cur_obj = bpy.data.objects[basename]
    scn.objects.active = cur_obj
    mesh = cur_obj.data
    bpy.ops.mesh.vertex_color_remove()
    vcol_layer = mesh.vertex_colors.new('Col')
    for vert in valid_verts:
        x = STSPanel.lookup[vert]
        for loop_ind in x[x > -1]:
            d = vcol_layer.data[loop_ind]
            colors = verts_colors[vert]
            d.color = colors



def change_cm(cm):
    root_fol = bpy.path.abspath('//')
    print('Chaging cm to {}'.format(cm))
    cb_title = 'values'

    colormap_fname = op.join(root_fol, 'cm', '{}.npy'.format(cm))
    colormap = np.load(colormap_fname)
    for ind in range(colormap.shape[0]):
        cb_obj_name = 'cb.{0:0>3}'.format(ind)
        cb_obj = bpy.data.objects[cb_obj_name]
        cur_mat = cb_obj.active_material
        cur_mat.diffuse_color = colormap[ind]

    bpy.data.objects['colorbar_title'].data.body = bpy.data.objects['colorbar_title_camera'].data.body = cb_title
    bpy.data.objects['colorbar_max'].data.body = '{:.2f}'.format(STSPanel.data_max)
    bpy.data.objects['colorbar_min'].data.body = '{:.2f}'.format(STSPanel.data_min)


def sts_draw(self, context):
    layout = self.layout
    layout.label(text='ply file:')
    layout.prop(context.scene, 'ply_file', text="")
    layout.operator(LoadButton.bl_idname, text="Load ply file", icon='LOAD_FACTORY')


class LoadButton(bpy.types.Operator):
    bl_idname = "sts.load_ply"
    bl_label = "Load Ply"
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        if load_ply_file():
            process_ply()
        return {'PASS_THROUGH'}


class STSPanel(bpy.types.Panel):
    bl_space_type = "GRAPH_EDITOR"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "ScattToSurf"
    bl_label = "Load ply"
    addon = None
    init = False

    def draw(self, context):
        if STSPanel.init:
            sts_draw(self, context)


def init(addon):
    print('Loading sts panel')
    STSPanel.addon = addon
    set_values_variables()
    register()
    STSPanel.init = True


def set_values_variables():
    root_fol = bpy.path.abspath('//')
    basename = sts_utils.namebase(bpy.path.abspath(bpy.context.scene.ply_file))
    values_fname = op.join(root_fol, '{}_values.npy'.format(basename))
    if op.isfile(values_fname):
        STSPanel.vert_values = np.load(values_fname)
        STSPanel.lookup = np.load(op.join(root_fol, '{}_faces_verts.npy'.format(basename)))
        STSPanel.data_min = np.min(STSPanel.vert_values)
        STSPanel.data_max = np.max(STSPanel.vert_values)
        _addon().set_colorbar_max_min(STSPanel.data_max, STSPanel.data_min)
        STSPanel.colors_ratio = 256 / (STSPanel.data_max - STSPanel.data_min)


def register():
    try:
        unregister()
        bpy.utils.register_class(STSPanel)
        bpy.utils.register_class(LoadButton)
    except:
        print("Can't register Morph Panel!")
        print(traceback.format_exc())


def unregister():
    try:
        bpy.utils.unregister_class(STSPanel)
        bpy.utils.unregister_class(LoadButton)
    except:
        pass
