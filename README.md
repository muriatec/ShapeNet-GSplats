# Gaussian splats for ShapeNet
You can use this repo to create Gaussian splats for ShapeNet models. We run it on ShapeNetCore.v2.
## Installation
We use blender 3.6.13 to render the objects, you can download it [here](https://mirrors.ocf.berkeley.edu/blender/release/Blender3.6/blender-3.6.13-linux-x64.tar.xz). After extracting blender, please go to ```/path/to/blender/3.6/python/bin/python3.10``` and install ```numpy```, ```opencv-python```, ```trimesh``` and ```plyfile```.

## Usage
To use the rendering scripts, just run
```
/path/to/blender --background --python render_blender_uniform.py -- --ntheta 12 --nphi 6 --output_dir /path/to/output /path/to/my.obj
```

To render objects in batch, run
```
/path/to/blender/python -u render_batch_uniform.py --model_root_dir {ShapeNet root dir} --render_root_dir {where you store the rendering dataset} --filelist_dir {which models you want to render} --blender_location {where you blender is installed} --num_thread {10} --shapenetversion {support v1, v2} --debug {False}
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

## Known issues from ShapeNet dataset
The following 19 models from category `02958343` lack model files to be rendered, which we omitted for our GSplats dataset:
```
8070747805908ae62a9eb0f146e94477 
f5bac2b133a979c573397a92d1662ba5 
e6c22be1a39c9b62fb403c87929e1167 
d6ee8e0a0b392f98eb96598da750ef34 
3ffeec4abd78c945c7c79bdb1d5fe365 
2307b51ca7e4a03d30714334794526d4 
407f2811c0fe4e9361c6c61410fc904b 
7aa9619e89baaec6d9b8dfa78596b717 
806d740ca8fad5c1473f10e6caaeca56 
ea3f2971f1c125076c4384c3b17a86ea 
4ddef66f32e1902d3448fdcb67fe08ff 
986ed07c18a2e5592a9eb0f146e94477 
302612708e86efea62d2c237bfbc22ca 
9fb1d03b22ecac5835da01f298003d56 
93ce8e230939dfc230714334794526d4 
207e69af994efa9330714334794526d4 
3c33f9f8edc558ce77aa0b62eed1492 
5bf2d7c2167755a72a9eb0f146e94477 
5973afc979049405f63ee8a34069b7c5
```
