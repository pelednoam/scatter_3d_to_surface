import os.path as op
try:
    import bpy
except:
    pass

def get_parent_fol(fol=None):
    if fol is None:
        fol = op.dirname(op.realpath(__file__))
    return op.split(fol)[0]


def namebase(file_name):
    return op.splitext(op.basename(file_name))[0]


def file_fol():
    return op.dirname(bpy.data.filepath)
