import os
import sys
import argparse
from joblib import Parallel, delayed
import socket

parser = argparse.ArgumentParser()
parser.add_argument('--dataset_root_dir', type=str, default="/mnt/data/ShapeNetCore.v2.Rendering")
parser.add_argument('--gsplat_root_dir', type=str, default="/mnt/data/ShapeNetCore.v2.GaussianSplats")
parser.add_argument('--filelist_dir', type=str, default="./test_filelists")
parser.add_argument('--num_gpu', type=int, default=2)
args = parser.parse_args()

dataset_root_dir = args.dataset_root_dir
gsplat_root_dir = args.gsplat_root_dir
filelist_dir = args.filelist_dir

def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

def train_gsplats(dataset_root_dir, cat_id, obj_id, gpu_id):
	dataset_path = os.path.join(dataset_root_dir, cat_id, obj_id)
	output_dir = os.path.join(gsplat_root_dir, cat_id, obj_id)
	os.makedirs(output_dir, exist_ok=True)
	if os.path.exists(os.path.join(output_dir, "point_cloud", "iteration_30000", "point_cloud.ply")):
		print("Exist!!! Skip %s %s" % (cat_id, obj_id))
	else:
		print("Start %s %s" % (cat_id, obj_id))
		free_port = find_free_port()
		os.system('CUDA_VISIBLE_DEVICES=%s python /gaussian-splatting/train.py -s %s -m %s --port %s' % (gpu_id, dataset_path, output_dir, free_port))

print("==========Start Gaussian Splatting==========")
for filename in os.listdir(filelist_dir):
	if filename.endswith(".lst"):
		cat_id = filename.split(".")[0]
		print("Start New Category %s"%cat_id)
		file = os.path.join(filelist_dir, filename)
		lst = []
		with open(file) as f:
			content = f.read().splitlines()
			for line in content:
				lst.append(line)

		dataset_root_dir_lst = [dataset_root_dir for i in range(len(lst))]
		cat_id_lst = [cat_id for i in range(len(lst))]
		with Parallel(n_jobs=args.num_gpu) as parallel:
			parallel(delayed(train_gsplats)(dataset_root_dir, cat_id, obj_id, idx % args.num_gpu) for
					 idx, (dataset_root_dir, cat_id, obj_id) in
					 enumerate(zip(dataset_root_dir_lst, cat_id_lst, lst)))
	print("Finished Category %s"%cat_id)
print("==========Finished Gaussian Splatting==========")