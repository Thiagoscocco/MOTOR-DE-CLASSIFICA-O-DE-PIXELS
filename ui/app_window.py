import tkinter as tk
from ui.canvas_view import CanvasView
from ui.controls_frame import ControlsFrame
from tkinter import ttk
import sv_ttk


class AppWindow(tk.Tk):
    """
    Janela principal do software.
    Integra o CanvasView (visualização) e o ControlsFrame (controles).
    """
    def __init__(self):
        super().__init__()
        sv_ttk.set_theme("light") 
        self._is_dark = False

        header = ttk.Frame(self, padding=(10, 8))
        header.pack(fill="x")
        ttk.Label(header, text="MOTOR DE CLASSIFICAÇÃO: IOP", font=("Segoe UI", 12, "bold")).pack(side="left")

        self.btn_theme = ttk.Button(header, text="🌙 Dark", width=10, command=self._toggle_theme)
        self.btn_theme.pack(side="right", padx=(0, 4))

        self.title("Motor: Easy IOP")
        self.geometry("950x600")
        self.resizable(False, False)

        #Canvas principal
        content = ttk.Frame(self)
        content.pack(fill="both", expand=True)

        self.canvas_view = CanvasView(content)
        self.canvas_view.pack(side="left", padx=10, pady=10)

        self.controls = ControlsFrame(content, self.canvas_view)
        self.controls.pack(side="right", fill="y", padx=10, pady=10)

    def _toggle_theme(self):
        """Alterna entre tema claro/escuro sem alterar o processamento."""
        self._is_dark = not self._is_dark
        if self._is_dark:
            sv_ttk.set_theme("dark")
            self.btn_theme.config(text="☀️ Light")
        else:
            sv_ttk.set_theme("light")
            self.btn_theme.config(text="🌙 Dark")


