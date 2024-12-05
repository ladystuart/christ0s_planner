import tkinter as tk
from config.settings import TOOLTIP


class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.widget.bind('<Enter>', self.show_tip)
        self.widget.bind('<Leave>', self.hide_tip)

    def show_tip(self, event=None):
        if self.tip_window is not None:
            return  # Подсказка уже показана

        x, y, _, _ = self.widget.bbox("insert")  # Получаем координаты виджета
        x += self.widget.winfo_rootx() + 25  # Смещение для подсказки
        y += self.widget.winfo_rooty() + 25  # Смещение для подсказки

        # Создаем окно подсказки
        self.tip_window = tk.Toplevel(self.widget)
        self.tip_window.wm_overrideredirect(True)  # Без рамки
        self.tip_window.wm_geometry(f"+{x}+{y}")  # Устанавливаем положение подсказки

        label = tk.Label(self.tip_window, text=self.text, background=TOOLTIP['bg_color'], borderwidth=1,
                         relief=TOOLTIP['relief'], font=TOOLTIP['font'])
        label.pack()

    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None