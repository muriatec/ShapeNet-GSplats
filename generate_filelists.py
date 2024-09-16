import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--dataset_dir', type=str, default="/mnt/data/ShapeNetCore.v2")
parser.add_argument('--filelist_dir', type=str, default="./filelists")
args = parser.parse_args()

dataset_path = args.dataset_dir
filelist_path = args.filelist_dir

os.makedirs(filelist_path, exist_ok=True)

for catID in os.listdir(dataset_path):
    cat_path = os.path.join(dataset_path, catID)

    if os.path.isdir(cat_path):
        model_ids = [modelID for modelID in os.listdir(cat_path) if os.path.isdir(os.path.join(cat_path, modelID))]
        
        lst_file = os.path.join(filelist_path, f'{catID}.lst')
        
        with open(lst_file, 'w') as f:
            for modelID in model_ids:
                f.write(f'{modelID}\n')
        print(f'Saved {lst_file} with {len(model_ids)} model IDs.')
