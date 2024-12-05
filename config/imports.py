import tkinter as tk
from tkinter import (PhotoImage, simpledialog, messagebox, filedialog, Toplevel, Frame, Canvas, Scrollbar, Button,
                     StringVar)
import tkinter.ttk as ttk
from PIL import Image, ImageTk
import json
import os
import shutil
import webbrowser
from itertools import chain

from config.settings import (
    APP,
    SIDE_PANEL,
    INTERFACE,
    DATA_PATHS,
    ICONS_PATHS,
    PAGES_NAMES,
    BANNER_PATHS
)
from config.utils import (
    add_source_label,
    add_banner,
    resize_banner,
    add_icon_and_label,
    add_separator,
    open_link,
    title_label,
    clear_canvas,
    reset_canvas_view,
    add_image_to_grid,
    center_window_on_parent
)
