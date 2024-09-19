# Gaussian splats for ShapeNet
You can use this repo to create Gaussian splats for ShapeNet models. We run it on ShapeNetCore.v2.
## Installation
We use blender 3.6.13 to render the objects, you can download it [here](https://mirrors.ocf.berkeley.edu/blender/release/Blender3.6/blender-3.6.13-linux-x64.tar.xz). After extracting blender, please go to ```/path/to/blender/3.6/python/bin/python3.10``` and install ```numpy```, ```opencv-python```, ```trimesh``` and ```plyfile```.

## Usage
To use the rendering scripts, just run
```
/path/to/blender --background --python render_blender_uniform.py -- --ntheta 12 --nphi 6 --output_dir /path/to/output /path/to/my.obj
```

You will get the GS-ready dataset organized as follows:
```
└── 📁{model_ID}
    └── 📁cameras
        └── extrinsics.npy
        └── intrinsics.txt
    └── 📁images
        └── 00.png
        └── 01.png
        └── 02.png
        └── [...]
    └── pointcloud.ply
```

To render objects in batch, run
```
/path/to/blender/python -u render_batch_uniform.py --model_root_dir {ShapeNet root dir} --render_root_dir {where you store the rendering dataset} --filelist_dir {which models you want to render} --blender_location {where you blender is installed} --num_thread {10} --shapenetversion {support v1, v2} --debug {False}
```
