import os
import argparse

model_num ={
    '03790512': 337, 
    '02924116': 939, 
    '04554684': 169, 
    '04379243': 8436, 
    '03207941': 93, 
    '02880940': 186, 
    '04074963': 66, 
    '02871439': 452, 
    '04256520': 3173, 
    '03691459': 1597, 
    '04090263': 2373, 
    '03261776': 73, 
    '02747177': 343, 
    '03928116': 239, 
    '03467517': 797, 
    '03938244': 96, 
    '03593526': 596, 
    '02818832': 233, 
    '02876657': 498, 
    '02691156': 4045, 
    '03710193': 94, 
    '03046257': 651, 
    '03001627': 6778, 
    '03085013': 65, 
    '03211117': 1093, 
    '02808440': 856, 
    '04330267': 218, 
    '03761084': 152, 
    '04468005': 389, 
    '04225987': 152, 
    '02942699': 113, 
    '03337140': 298, 
    '04460130': 133, 
    '02992529': 831, 
    '03991062': 602, 
    '02954340': 56, 
    '02843684': 73, 
    '04401088': 1089, 
    '04004475': 166, 
    '04530566': 1939, 
    '03797390': 214, 
    '03513137': 162, 
    '03624134': 424, 
    '02801938': 113, 
    '03325088': 744, 
    '02773838': 83, 
    '03642806': 460, 
    '03948459': 307, 
    '03636649': 2318, 
    '04099429': 85, 
    '02946921': 108, 
    '02828884': 1813, 
    '02958343': 3533, 
    '03759954': 67, 
    '02933112': 1571
}

def check_folder_structure(category, root_folder, output_file):
    if len(os.listdir(root_folder)) < model_num[category]:
        with open(output_file, 'w', buffering=1) as f:
            f.write(f"Not completed yet! Need {model_num[category]} in total, only found {len(os.listdir(root_folder))}.")
            f.close()
        return
    problematic_models = []
    with open(output_file, 'w', buffering=1) as f:
        for subdir in os.listdir(root_folder):
            subdir_path = os.path.join(root_folder, subdir)
            if os.path.isdir(subdir_path):
                invalid = False
                cameras_folder = os.path.join(subdir_path, 'cameras')
                if not os.path.exists(cameras_folder):
                    f.write(f"{subdir}: 'cameras' folder missing\n")
                    invalid = True
                intrinsics_file = os.path.join(cameras_folder, 'intrinsics.txt')
                extrinsics_file = os.path.join(cameras_folder, 'extrinsics.npy')
                if not (os.path.exists(intrinsics_file) and os.path.exists(extrinsics_file)):
                    if not os.path.exists(intrinsics_file):
                        f.write(f"{subdir}: Missing 'intrinsics.txt' in 'cameras' folder\n")
                    if not os.path.exists(extrinsics_file):
                        f.write(f"{subdir}: Missing 'extrinsics.npy' in 'cameras' folder\n")
                    invalid = True

                images_folder = os.path.join(subdir_path, 'images')
                if not os.path.exists(images_folder):
                    f.write(f"{subdir}: 'images' folder missing\n")
                    invalid = True
                images = [f"{i:02d}.png" for i in range(62)]
                missing_images = [img for img in images if not os.path.exists(os.path.join(images_folder, img))]
                if missing_images:
                    f.write(f"{subdir}: Missing images: {', '.join(missing_images)}\n")
                    invalid = True

                point_cloud_file = os.path.join(subdir_path, 'pointcloud.ply')
                if not os.path.exists(point_cloud_file):
                    f.write(f"{subdir}: 'pointcloud.ply' missing\n")
                    invalid = True

                if invalid:
                    problematic_models.append(subdir)
                else:
                    f.write(f"{subdir}: All checks passed\n")
        f.write(f"Number of problematic models: {len(problematic_models)}\n")
        f.writelines(problematic_models)
        f.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--category', ('-c'), type=str, default="04379243")
    args = parser.parse_args()
    category = args.category
    root_folder = os.path.join("/mnt/data/ShapeNetCore.v2.Rendering", category)
    output_file = os.path.join("/mnt/data/ShapeNetCore.v2.Rendering", category, "check_info.txt")
    check_folder_structure(category, root_folder, output_file)
