import torch
import types
import os
from tqdm import tqdm
import numpy as np

from detectron2.config import get_cfg
from detectron2.data.detection_utils import read_image
from detectron2.projects.deeplab import add_deeplab_config
import glob
from mask2former import add_maskformer2_config
from predictor import VisualizationDemo
import matplotlib
import matplotlib.pyplot as plt
import argparse

import json

def setup_cfg(args):
    # load config from file and command-line arguments
    cfg = get_cfg()
    add_deeplab_config(cfg)
    add_maskformer2_config(cfg)
    cfg.merge_from_file(args.config_file)
    cfg.merge_from_list(args.opts)
    cfg.freeze()
    return cfg


MASK2FORMER_CONFIG_FILE = "./maskformer2_swin_large_IN21k_384_bs16_100ep.yaml"
MASK2FORMER_WEIGHTS_FILE = "./model_final_e5f453.pkl"



if __name__ == '__main__':
    torch.autograd.set_grad_enabled(False)

    parser = argparse.ArgumentParser(description="Specify dirs")
    parser.add_argument('--scene_dir_path', default="./masked_rdp_data/", type=str)
    parser.add_argument('--save_dir_path', default="./maskformer_masks/", type=str)
    args = parser.parse_args()

    scene_dir = args.scene_dir_path
    save_dir = args.save_dir_path

    os.makedirs(os.path.join(save_dir), exist_ok=True)

    for scan in tqdm(os.listdir(scene_dir)):
        os.makedirs(os.path.join(save_dir, scan), exist_ok=True)
        
        rgb_list = glob.glob(os.path.join(scene_dir, scan, "*png"))

        for img2_idx in range(len(rgb_list)):
            IMGFILE = os.path.join(scene_dir, scan, str(img2_idx) + ".png")
            MASK_LOAD_FILE = os.path.join(save_dir, scan, str(img2_idx) + ".pt")
            LOAD_IMG_HEIGHT = 512
            LOAD_IMG_WIDTH = 512
    
            cfgargs = types.SimpleNamespace()
            cfgargs.imgfile = IMGFILE
            cfgargs.config_file = MASK2FORMER_CONFIG_FILE
            cfgargs.opts = ["MODEL.WEIGHTS", MASK2FORMER_WEIGHTS_FILE]

            cfg = setup_cfg(cfgargs)
            demo = VisualizationDemo(cfg)
            
            img = read_image(IMGFILE, format="BGR")

            predictions, visualized_output = demo.run_on_image(img)
            masks = torch.nn.functional.interpolate(
                predictions["instances"].pred_masks.unsqueeze(0), [LOAD_IMG_HEIGHT, LOAD_IMG_WIDTH], mode="nearest"
            )
            masks = masks.half()
            torch.save(masks[0].detach().cpu(), MASK_LOAD_FILE)   

