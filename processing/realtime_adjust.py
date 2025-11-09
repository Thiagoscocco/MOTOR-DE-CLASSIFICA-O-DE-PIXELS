import numpy as np
import cv2
from skimage.filters import threshold_otsu
from processing.postprocessing import apply_postprocessing
from utils.metrics import calculate_percentages

def adjust_segmentation(img, indices, sens_planta=0.5, bias_palha=0.5, limpeza=1):
    """
    Atualiza a segmentação conforme os sliders do usuário:
    sens_planta → sensibilidade da planta (0–1)
    bias_palha  → viés da palha (0–1)
    limpeza     → intensidade da limpeza (1–3)
    """

    # --- Índices principais ---
    exg = indices["ExG"]
    exgr = indices["ExGR"]
    ndi = indices["NDI"]
    cive = indices["CIVE"]
    straw = indices["StrawIndex"]

    # --- Score para plantas ---
    veg_score = 0.4 * exg + 0.3 * exgr + 0.2 * ndi + 0.1 * (1 - cive)
    try:
        t_veg = threshold_otsu(veg_score)
    except:
        t_veg = np.percentile(veg_score, 80)
    # Ajuste do usuário → desloca o limiar de acordo com o slider
    t_veg = np.clip(t_veg * (1.0 - (sens_planta - 0.5)), 0, 1)
    mask_planta = veg_score >= t_veg

    # --- Score para palha x solo (em não-planta) ---
    ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb).astype(np.float32)
    L = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)[:, :, 0].astype(np.float32)
    Cb = ycrcb[:, :, 2]
    Cr = ycrcb[:, :, 1]

    straw_score = 0.4 * straw + 0.3 * (Cb / 255.0) - 0.3 * (Cr / 255.0) + 0.3 * (L / 255.0)
    try:
        t_straw = threshold_otsu(straw_score[mask_planta == 0])
    except:
        t_straw = np.percentile(straw_score[mask_planta == 0], 50)
    # Ajuste do usuário → desloca o limiar
    t_straw = np.clip(t_straw * (1.0 - (bias_palha - 0.5)), 0, 1)

    mask_straw = (straw_score >= t_straw) & (mask_planta == 0)
    mask_solo = (straw_score < t_straw) & (mask_planta == 0)

    # --- Monta mapa final ---
    seg_map = np.zeros_like(mask_planta, dtype=np.uint8)
    seg_map[mask_solo] = 0
    seg_map[mask_straw] = 1
    seg_map[mask_planta] = 2

    # --- Aplica limpeza morfológica ---
    seg_map_clean = apply_postprocessing(seg_map, level=int(limpeza))

    # --- Calcula porcentagens ---
    metrics = calculate_percentages(seg_map_clean)

    return seg_map_clean, metrics

def create_overlay(img, seg_map, alpha=0.4):
    """
    Cria uma sobreposição colorida do mapa de classes sobre a imagem original.
    Cores:
      Solo  = marrom
      Palha = amarelo
      Planta = verde
    """
    overlay = img.copy().astype(np.float32)
    color_map = {
        0: (42, 42, 165),   # marrom (solo) em BGR
        1: (0, 255, 255),   # amarelo (palha)
        2: (0, 200, 0)      # verde (planta)
    }
    for cls, color in color_map.items():
        mask = (seg_map == cls)
        overlay[mask] = overlay[mask] * (1 - alpha) + np.array(color, np.float32) * alpha
    return np.clip(overlay, 0, 255).astype(np.uint8)

def generate_class_map(seg_map):
    """
    Gera o mapa de classes colorido (sem imagem original).
    Mesmo esquema de cores do overlay.
    """
    color_map = {
        0: (42, 42, 165),   # marrom (solo)
        1: (0, 255, 255),   # amarelo (palha)
        2: (0, 200, 0)      # verde (planta)
    }
    h, w = seg_map.shape
    mapa = np.zeros((h, w, 3), np.uint8)
    for cls, color in color_map.items():
        mapa[seg_map == cls] = color
    return mapa

