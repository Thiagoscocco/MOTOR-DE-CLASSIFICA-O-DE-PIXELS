import numpy as np

def calculate_percentages(seg_map):
    """
    Calcula a porcentagem de pixels de cada classe:
    0 = solo, 1 = palha, 2 = planta.
    """
    if seg_map is None or seg_map.size == 0:
        return {"planta_%": 0.0, "palha_%": 0.0, "solo_%": 0.0}

    total = seg_map.size
    counts = {
        0: np.sum(seg_map == 0),
        1: np.sum(seg_map == 1),
        2: np.sum(seg_map == 2),
    }

    return {
        "solo_%": round((counts[0] / total) * 100, 2),
        "palha_%": round((counts[1] / total) * 100, 2),
        "planta_%": round((counts[2] / total) * 100, 2),
    }
