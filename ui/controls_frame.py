import tkinter as tk
import numpy as np
from tkinter import filedialog
import cv2
from processing.indices import compute_all_indices
from processing.realtime_adjust import adjust_segmentation, create_overlay

class ControlsFrame(tk.Frame):
    """
    Frame lateral com botões e sliders de controle.
    Interage diretamente com o CanvasView e o backend.
    """
    def __init__(self, parent, canvas_view):
        super().__init__(parent, padx=10, pady=10)
        self.canvas_view = canvas_view
        self.img_original = None
        self.indices = None
        self.seg_map = None

        # --- Botões principais ---
        tk.Button(self, text="📂 Upload Imagem", command=self.upload_image, width=20).pack(pady=5)
        tk.Button(self, text="⚙️ Processar Imagem", command=self.generate_indices, width=20).pack(pady=5)
        tk.Button(self, text="💾 Salvar Resultado", command=self.save_result, width=20).pack(pady=5)

        # --- Sliders ---
        tk.Label(self, text="🌿 Sensibilidade da Planta").pack(pady=(15,0))
        self.slider_planta = tk.Scale(self, from_=0, to=1, resolution=0.01, orient="horizontal", command=self.update_realtime)
        self.slider_planta.set(0.5)
        self.slider_planta.pack()

        tk.Label(self, text="🌾 Bias para Palha").pack(pady=(10,0))
        self.slider_palha = tk.Scale(self, from_=0, to=1, resolution=0.01, orient="horizontal", command=self.update_realtime)
        self.slider_palha.set(0.5)
        self.slider_palha.pack()

        tk.Label(self, text="🧹 Limpeza").pack(pady=(10,0))
        self.slider_limpeza = tk.Scale(self, from_=1, to=3, resolution=1, orient="horizontal", command=self.update_realtime)
        self.slider_limpeza.set(1)
        self.slider_limpeza.pack()

        # --- Texto para métricas ---
        self.metrics_label = tk.Label(self, text="Percentuais: -", justify="left")
        self.metrics_label.pack(pady=10)

        #Alterção do modo de visualização:
        tk.Label(self, text="👁️ Modo de Visualização").pack(pady=(5, 0))
        from tkinter import ttk
        self.view_mode = tk.StringVar(value="Overlay")
        self.combo_view = ttk.Combobox(self, textvariable=self.view_mode, state="readonly",
                                       values=["Overlay", "Original", "Mapa"], width=15)
        self.combo_view.pack(pady=3)
        self.combo_view.bind("<<ComboboxSelected>>", self.change_view_mode)

    def upload_image(self):
        """Abre janela de seleção e carrega imagem."""
        file_path = filedialog.askopenfilename(filetypes=[("Imagens", "*.jpg *.png *.jpeg")])
        if not file_path:
            return
        img = cv2.imread(file_path)
        if img is None:
            return
        self.img_original = img
        self.indices = None
        self.canvas_view.display_image(img)
        self.metrics_label.config(text="Percentuais: ")

        self.slider_planta.set(0.5)   # Sensibilidade da Planta
        self.slider_palha.set(0.5)    # Bias para Palha
        self.slider_limpeza.set(1)    # Limpeza
        self.seg_map = None

    def generate_indices(self):
        """Calcula índices da imagem carregada."""
        if self.img_original is None:
            return
        self.indices = compute_all_indices(self.img_original)
        seg_map, metrics = adjust_segmentation(
            self.img_original, self.indices,
            sens_planta=self.slider_planta.get(),
            bias_palha=self.slider_palha.get(),
            limpeza=self.slider_limpeza.get()
        )
        self.seg_map = seg_map
        overlay = create_overlay(self.img_original, seg_map)
        self.canvas_view.update_overlay(overlay)
        self.update_metrics(metrics)

    def update_realtime(self, *args):
        """Reprocessa a imagem em tempo real conforme sliders."""
        if self.img_original is None or self.indices is None:
            return
        seg_map, metrics = adjust_segmentation(
            self.img_original, self.indices,
            sens_planta=self.slider_planta.get(),
            bias_palha=self.slider_palha.get(),
            limpeza=self.slider_limpeza.get()
        )
        self.seg_map = seg_map
        overlay = create_overlay(self.img_original, seg_map)
        self.canvas_view.update_overlay(overlay)
        self.update_metrics(metrics)
        self.change_view_mode()


    def update_metrics(self, metrics):
        """Atualiza o texto dos percentuais."""
        text = (f"🌱 Planta: {metrics['planta_%']}%\n"
                f"🌾 Palha: {metrics['palha_%']}%\n"
                f"🪵 Solo: {metrics['solo_%']}%")
        self.metrics_label.config(text=text)

    def save_result(self):
        """Salva o resultado final (overlay e mapa de classes)."""
        if self.seg_map is None or self.img_original is None:
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                 filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg")])
        if not file_path:
            return

        mode = self.view_mode.get()
        if mode == "Original":
            img_to_save = self.img_original
        elif mode == "Mapa":
             img_to_save = self.create_color_map(self.seg_map)
        else:  # Overlay
            from processing.realtime_adjust import create_overlay
            img_to_save = create_overlay(self.img_original, self.seg_map)

        cv2.imwrite(file_path, img_to_save)


    def change_view_mode(self, event=None):
        """Atualiza a imagem exibida conforme o modo selecionado."""
        if self.img_original is None or self.seg_map is None:
            return

        mode = self.view_mode.get()
        if mode == "Original":
            self.canvas_view.display_image(self.img_original)
        elif mode == "Overlay":
            from processing.realtime_adjust import create_overlay
            overlay = create_overlay(self.img_original, self.seg_map)
            self.canvas_view.update_overlay(overlay)
        elif mode == "Mapa":
            # Cria imagem somente com as cores das classes
            mapa = self.create_color_map(self.seg_map)
            self.canvas_view.update_overlay(mapa)

    def create_color_map(self, seg_map):
        """Gera o mapa de classes colorido (sem imagem original)."""
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

