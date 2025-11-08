import cv2
import numpy as np

def rgb_to_lab(img):
    """Converte imagem RGB (ou BGR) para espaço Lab (0–255)."""
    if img is None or len(img.shape) < 3:
        raise ValueError("Imagem inválida.")
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    return lab.astype(np.float32)

def rgb_to_ycrcb(img):
    """Converte imagem RGB (ou BGR) para espaço YCrCb (0–255)."""
    if img is None or len(img.shape) < 3:
        raise ValueError("Imagem inválida.")
    ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
    return ycrcb.astype(np.float32)

def normalize_channel(channel):
    """Normaliza um canal para 0–1."""
    ch = channel.astype(np.float32)
    min_val, max_val = np.min(ch), np.max(ch)
    if max_val - min_val == 0:
        return np.zeros_like(ch, dtype=np.float32)
    norm = (ch - min_val) / (max_val - min_val)
    return np.clip(norm, 0, 1)
