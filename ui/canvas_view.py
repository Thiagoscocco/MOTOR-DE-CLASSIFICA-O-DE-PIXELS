import tkinter as tk
from PIL import Image, ImageTk
import cv2
import numpy as np

class CanvasView(tk.Label):
    """
    Exibe a imagem no formato PhotoImage dentro do Tkinter.
    Atualiza em tempo real conforme o overlay muda.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.image_tk = None
        self.current_img = None

    def display_image(self, img_bgr):
        """Exibe imagem BGR (OpenCV) no canvas Tkinter."""
        if img_bgr is None:
            return
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(np.uint8(img_rgb))
        img_resized = img_pil.resize((600, 400))
        self.image_tk = ImageTk.PhotoImage(img_resized)
        self.configure(image=self.image_tk)
        self.current_img = img_bgr

    def update_overlay(self, overlay_bgr):
        """Atualiza o canvas com o overlay (imagem processada)."""
        self.display_image(overlay_bgr)
