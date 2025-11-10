import numpy as np
import cv2

def normalize(arr):
    arr = arr.astype(np.float32)
    min_val, max_val = np.nanmin(arr), np.nanmax(arr)
    if max_val - min_val == 0:
        return np.zeros_like(arr, dtype=np.float32)
    norm = (arr - min_val) / (max_val - min_val)
    return np.clip(norm, 0, 1)

def calculate_exg(img):
    b, g, r = cv2.split(img.astype(np.float32))
    exg = 2 * g - r - b
    return normalize(exg)

def calculate_exgr(img):
    b, g, r = cv2.split(img.astype(np.float32))
    exgr = 3 * g - 2.4 * r - b
    return normalize(exgr)

def calculate_cive(img):
    b, g, r = cv2.split(img.astype(np.float32))
    cive = 0.441 * r - 0.811 * g + 0.385 * b + 18.787
    return normalize(-cive)

def calculate_ndi(img):
    b, g, r = cv2.split(img.astype(np.float32))
    ndi = (g - r) / (g + r + 1e-6)
    return normalize(ndi)

def calculate_straw_index(img):
    b, g, r = cv2.split(img.astype(np.float32))
    straw = ((r + g) / 2) - b
    return normalize(straw)

def compute_all_indices(img):
    if img is None or len(img.shape) < 3:
        raise ValueError("Imagem inválida ou não colorida.")
    exg = calculate_exg(img)
    exgr = calculate_exgr(img)
    cive = calculate_cive(img)
    ndi = calculate_ndi(img)
    straw = calculate_straw_index(img)
    return {
        "ExG": exg,
        "ExGR": exgr,
        "CIVE": cive,
        "NDI": ndi,
        "StrawIndex": straw
    }
