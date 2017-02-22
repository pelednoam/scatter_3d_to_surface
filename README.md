# scatter 3D to surface

Transforms 3D coordinates (3D scatter plot) with values into a colored surfacce

### Installation:
- Download [Blender](https://www.blender.org/download/) (2.78 and above).
- Clone the code (git clone https://github.com/pelednoam/scatter_3d_to_surface.git)
- If you're already using python 3.4 and above, you can just use your current installation. If not, it's recommended to install [Anaconda](https://www.continuum.io/downloads), python 3.5 version, or just [python](https://www.python.org/downloads/) 3.4 and above.
- Before running the setup, be sure that by typing 'python' in the terminal you are running python 3.4 and above. You can also create an alias to python 3
- Run the mmvt setup from the project's code folder: `python -m setup` 

### Preprocessing

First you need to create a mesh from the 3D points:

'python -m preproc.create_mesh -d file-name -r root-fol'


