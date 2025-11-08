import cv2
import numpy as np

def clean_mask(mask, level=1):
    """
    Aplica limpeza morfológica simples (abertura + fechamento).
    level: intensidade (1 = leve, 2 = média, 3 = forte)
    """
    k = 2 * level + 1
    kernel = np.ones((k, k), np.uint8)
    cleaned = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, kernel)
    return cleaned

def apply_postprocessing(seg_map, level=1):
    """
    Limpa o mapa de segmentação classe por classe.
    """
    result = np.zeros_like(seg_map, dtype=np.uint8)
    for cls in [0, 1, 2]:  # solo, palha, planta
        mask = (seg_map == cls).astype(np.uint8)
        cleaned = clean_mask(mask, level)
        result[cleaned == 1] = cls
    return result
