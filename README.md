# Gaussian splats for ShapeNet
You can use this repo to create Gaussian splats for ShapeNet models. We run it on ShapeNetCore.v2.
## Installation
We use blender 3.6.13 to render the objects, you can download it [here](https://www.blender.org/download/release/Blender3.6/blender-3.6.13-linux-x64.tar.xz). After extracting blender, please go to ```/path/to/blender/3.6/python/bin/python3.10``` and install ```numpy```, ```opencv-python```, ```trimesh``` and ```plyfile```.

After running the dataset preparation script, you will get the GS-ready dataset organized as follows:
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
