import numpy as np
import cv2
from skimage.filters import threshold_otsu
from utils.color_utils import rgb_to_lab, rgb_to_ycrcb

def threshold_percentile(img, p=0.5):
    flat = img.flatten()
    flat = flat[~np.isnan(flat)]
    if flat.size == 0:
        return 0.5
    return np.percentile(flat, p * 100)

def initial_plant_mask(indices):
    exg = indices["ExG"]
    exgr = indices["ExGR"]
    cive = indices["CIVE"]
    ndi = indices["NDI"]

    veg_score = 0.4 * exg + 0.3 * exgr + 0.2 * ndi + 0.1 * (1 - cive)
    try:
        t = threshold_otsu(veg_score)
    except:
        t = threshold_percentile(veg_score, 0.8)
    mask = veg_score >= t
    return mask.astype(np.uint8)

def straw_soil_mask(img, indices, plant_mask):
    straw = indices["StrawIndex"]
    lab = rgb_to_lab(img)
    ycrcb = rgb_to_ycrcb(img)

    L = lab[:, :, 0]
    Cb = ycrcb[:, :, 2]
    Cr = ycrcb[:, :, 1]

    straw_score = 0.4 * straw + 0.3 * (Cb / 255.0) - 0.3 * (Cr / 255.0) + 0.3 * (L / 255.0)
    try:
        t = threshold_otsu(straw_score[plant_mask == 0])
    except:
        t = threshold_percentile(straw_score[plant_mask == 0], 0.5)
    mask_straw = (straw_score >= t) & (plant_mask == 0)
    mask_soil = (straw_score < t) & (plant_mask == 0)

    return mask_straw.astype(np.uint8), mask_soil.astype(np.uint8)

def segment_image(img, indices):
    plant = initial_plant_mask(indices)
    straw, soil = straw_soil_mask(img, indices, plant)

    seg_map = np.zeros_like(plant, dtype=np.uint8)
    seg_map[soil == 1] = 0
    seg_map[straw == 1] = 1
    seg_map[plant == 1] = 2

    return {
        "seg_map": seg_map,
        "plant_mask": plant,
        "straw_mask": straw,
        "soil_mask": soil
    }
