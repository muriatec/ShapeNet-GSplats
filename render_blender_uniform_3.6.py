# A simple script that uses blender to render views of a single object by rotation the camera around it.
# Also produces depth map at the same time.
#
# Example:
# blender --background --python render_blender_uniform.py -- --ntheta 12 --nphi 6 /path/to/my.obj
#

import argparse, sys, os
parser = argparse.ArgumentParser(description='Renders given obj file by rotation a camera around it.')
parser.add_argument('--ntheta', type=int, default=12,
                    help='number of sampling points along the longtitude')
parser.add_argument('--nphi', type=int, default=6,
                    help='number of sampling points along the latitude')
parser.add_argument('--npoints', type=int, default=5000,
                    help='number of sampling points for the initial point cloud')
parser.add_argument('obj', type=str,
                    help='Path to the obj file to be rendered.')
parser.add_argument('--scale', type=float, default=1,
                    help='Scaling factor applied to model. Depends on size of mesh.')
parser.add_argument('--remove_doubles', type=bool, default=False,
                    help='Remove double vertices to improve mesh quality.')
parser.add_argument('--edge_split', type=bool, default=False,
                    help='Adds edge split filter.')
parser.add_argument('--depth_scale', type=float, default=1.4,
                    help='Scaling that is applied to depth. Depends on size of mesh. Try out various values until you get a good result. Ignored if format is OPEN_EXR.')
parser.add_argument('--color_depth', type=str, default='8',
                    help='Number of bit per channel used for output. Either 8 or 16.')
parser.add_argument('--format', type=str, default='PNG',
                    help='Format of files generated. Either PNG or OPEN_EXR')
parser.add_argument('--output_dir', type=str)

argv = sys.argv[sys.argv.index("--") + 1:]
args = parser.parse_args(argv)
import numpy as np
import bpy
import cv2
import trimesh
from plyfile import PlyData, PlyElement

# Import OBJ file
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.object.select_by_type(type='MESH')
bpy.ops.object.delete()
imported_obj = bpy.ops.import_scene.obj(filepath=args.obj)
# Assumes imported obj has one main object
obj_object = bpy.context.selected_objects[0]
# Reset object's location
obj_object.location = (0, 0, 0)
bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
# Scale, remove doubles, add edge split if specified
if args.scale != 1:
    obj_object.scale = (args.scale, args.scale, args.scale)
if args.remove_doubles:
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.remove_doubles()
    bpy.ops.object.mode_set(mode='OBJECT')
if args.edge_split:
    modifier = obj_object.modifiers.new(name='EdgeSplit', type='EDGE_SPLIT')
    modifier.split_angle = 1.32645
    bpy.ops.object.modifier_apply(modifier="EdgeSplit")

# Render
# Setup lights and camera
light_data = bpy.data.lights.new(name="Light", type='POINT')
light_data.energy = 1
light_object = bpy.data.objects.new(name="Light", object_data=light_data)
bpy.context.collection.objects.link(light_object)
light_object.location = (3, 3, 5)

# Render settings
def parent_obj_to_camera(b_camera):
    origin = (0, 0, 0)
    b_empty = bpy.data.objects.new("Empty", None)
    b_empty.location = origin
    b_camera.parent = b_empty  # setup parenting

    scn = bpy.context.scene
    scn.collection.objects.link(b_empty)
    bpy.context.view_layer.objects.active = b_empty
    # scn.objects.active = b_empty
    return b_empty

def camera_info(param):
    "params: [theta, phi, rho, x, y, z, f]"
    theta = np.deg2rad(param[0])
    phi = np.deg2rad(param[1])
    # print(param[0],param[1], theta, phi, param[6])

    camY = param[3]*np.sin(phi) * param[6]
    temp = param[3]*np.cos(phi) * param[6]
    camX = temp * np.cos(theta)
    camZ = temp * np.sin(theta)
    cam_pos = np.array([camX, camY, camZ])

    axisZ = cam_pos.copy()
    axisY = np.array([0, 1, 0])
    axisX = np.cross(axisY, axisZ)
    # axisY = np.cross(axisZ, axisX)

    # cam_mat = np.array([unit(axisX), unit(axisY), unit(axisZ)])
    print("cam axis", camX, camY, camZ)
    return camX, -camZ, camY

def storePly(path, xyz, rgb, normals):
    # Define the dtype for the structured array
    dtype = [('x', 'f4'), ('y', 'f4'), ('z', 'f4'),
            ('nx', 'f4'), ('ny', 'f4'), ('nz', 'f4'),
            ('red', 'u1'), ('green', 'u1'), ('blue', 'u1')]
    
    elements = np.empty(xyz.shape[0], dtype=dtype)
    attributes = np.concatenate((xyz, normals, rgb), axis=1)
    elements[:] = list(map(tuple, attributes))

    # Create the PlyData object and write to file
    vertex_element = PlyElement.describe(elements, 'vertex')
    ply_data = PlyData([vertex_element])
    ply_data.write(path)

scene = bpy.context.scene
# Resolution
scene.render.resolution_x = 400
scene.render.resolution_y = 400
scene.render.resolution_percentage = 100

# Background
bpy.context.scene.render.dither_intensity = 0.0
bpy.context.scene.render.film_transparent = True

cam = scene.objects['Camera']
cam_constraint = cam.constraints.new(type='TRACK_TO')
cam_constraint.track_axis = 'TRACK_NEGATIVE_Z'
cam_constraint.up_axis = 'UP_Y'
b_empty = parent_obj_to_camera(cam)
cam_constraint.target = b_empty

scene.render.image_settings.file_format = 'PNG'  # set output format to .png

rotation_mode = 'XYZ'

theta_stepsize = 360 / args.ntheta
phi_stepsize = 180 / args.nphi

output_dir = args.output_dir
output_image_dir = os.path.join(output_dir, "images")
output_camera_dir = os.path.join(output_dir, "cameras")
os.makedirs(output_image_dir, exist_ok=True)
os.makedirs(output_camera_dir, exist_ok=True)

r = 1.5 # distance to object center

# generate camera viewpoints
cam_coordinates = []

for lat in np.arange(-90, 91, phi_stepsize):
    if lat == -90 or lat == 90:
        cam_coordinates.append((0, 0, r * np.sin(np.radians(lat))))
    else:
        for lon in np.arange(0, 360, theta_stepsize):
            lat_rad = np.radians(lat)
            lon_rad = np.radians(lon)

            x = r * np.cos(lat_rad) * np.cos(lon_rad)
            y = r * np.cos(lat_rad) * np.sin(lon_rad)
            z = r * np.sin(lat_rad)

            cam_coordinates.append((x, y, z))

# save camera intrinsics
cam_intrinsics_path = os.path.join(output_camera_dir, "intrinsics.txt")
width = scene.render.resolution_x # pixels
height = scene.render.resolution_y # pixels
FovX = cam.data.angle_x
FovY = 2 * np.arctan(height * np.tan(FovX / 2) / width)

with open(cam_intrinsics_path, 'w') as f:
    f.write('Width {}\n'.format(width))
    f.write('Height {}\n'.format(height))
    f.write('FovX {}\n'.format(FovX))
    f.write('FovY {}'.format(FovY))

cam_extrinsics = np.zeros((len(cam_coordinates), 4, 4))
cam_extrinsics_path = os.path.join(output_camera_dir, "extrinsics.npy")

# render images uniformly & save camera extrinsics
for i, coords in enumerate(cam_coordinates):
    camX, camY, camZ = coords
    cam.location = (camX, camY, camZ)
    scene.render.filepath = output_image_dir + '/{0:02d}'.format(i)
    bpy.ops.render.render(write_still=True)  # render still
    cam_extrinsics[i, ...] = np.array(cam.matrix_world)

np.save(cam_extrinsics_path, cam_extrinsics)

# sample initial point cloud
mesh = trimesh.load(args.obj, force='mesh')
points, face_index, colors = trimesh.sample.sample_surface(mesh, count=args.npoints, sample_color=True)
face_normals = mesh.face_normals
normals = face_normals[face_index]
output_obj_path = os.path.join(output_dir, 'pointcloud.ply')
storePly(output_obj_path, points, colors[:, :3], normals)