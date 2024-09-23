# Gaussian Splatting for ShapeNet
Running the incredible 3D Gaussian Splatting on the ShapeNet dataset. Tested on ShapeNetCore.v2.

## Rendering
### Installation
We use blender 3.6.13 to render the objects, you can download it [here](https://mirrors.ocf.berkeley.edu/blender/release/Blender3.6/blender-3.6.13-linux-x64.tar.xz). After extracting blender, please go to ```/path/to/blender/3.6/python/bin/python3.10``` and install ```numpy```, ```opencv-python```, ```trimesh``` and ```plyfile```.

### Running
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

For models missing color information, we initialize the point cloud with gray.

## Training Gaussian Splats
We modified the original 3DGS code to read our ShapeNet rendering dataset. Please follow the instructions [here](https://github.com/graphdeco-inria/gaussian-splatting/blob/8a70a8cd6f0d9c0a14f564844ead2d1147d5a7ac/README.md) to set up the necessary environment for 3DGS. You can also build a docker image using the Dockerfile we provided in this repo or directly pull it from [Docker Hub](https://hub.docker.com/r/clchen2133/gsplat). If you'd like to use our Dockerfile, please also modify the source code of the SIBR viewer as shown [here](https://github.com/graphdeco-inria/gaussian-splatting/issues/965#issuecomment-2323401099) to ensure successful installation.

To train Gaussian splats in batches, run
```
conda activate gaussian_splatting
cd /gaussian-splatting-shapenet
python gsplat_batch.py --filelist_dir ./filelists --num_gpu {number of available GPUs} --dataset_root_dir {where you store the rendering dataset} --gsplat_root_dir {where you store the Gaussians splats}
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

## Debug
We encountered this error `RuntimeError: Function _RasterizeGaussiansBackward returned an invalid gradient at index 2 - got [0, 0, 3] but expected shape compatible with [0, 16, 3]` when training Gaussian splats on the following models:
```
03325088/33faed70ef14d4b362845c6edb57fc
03325088/59d8bc2a9d837719b362845c6edb57fc
03636649/cdbb91da1b21cd9c879995e59bad3d69
03636649/f29a94f969dd55ffc35131da26f8061a
03636649/1129a07c75f5a709cf004563556ddb36
03759954/d9f87094f6a26f8ea2105179d0c9d51e
03759954/62854e501570e57f1781e1106734ef2a
04379243/4726a178bb7b40544b3c42e318f3affc
04379243/f30419ee8ff3edeaae04ebd863e388a1
```

The error is caused by low opacities of Gaussians during optimization, which leads to **all points being pruned**. To solve this issue, we simply change the initialization of opacities [here](https://github.com/graphdeco-inria/gaussian-splatting/blob/472689c0dc70417448fb451bf529ae532d32c095/scene/gaussian_model.py#L139) from 0.1 to 1.
