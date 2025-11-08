import tkinter as tk
from ui.canvas_view import CanvasView
from ui.controls_frame import ControlsFrame

class AppWindow(tk.Tk):
    """
    Janela principal do software.
    Integra o CanvasView (visualização) e o ControlsFrame (controles).
    """
    def __init__(self):
        super().__init__()
        self.title("Classificador de Dosséis Vegetativos 🌱")
        self.geometry("950x500")
        self.resizable(False, False)

        # --- Canvas principal (imagem/overlay) ---
        self.canvas_view = CanvasView(self)
        self.canvas_view.pack(side="left", padx=10, pady=10)

        # --- Painel lateral de controles ---
        self.controls = ControlsFrame(self, self.canvas_view)
        self.controls.pack(side="right", fill="y", padx=10, pady=10)
