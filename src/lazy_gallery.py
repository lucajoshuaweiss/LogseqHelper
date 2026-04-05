"""
A gallery that uses lazy loading.
"""

import customtkinter as ctk

from src.config import ASSETS_DIR
from src.tasks import ThreadedExecutor


class LazyGallery:
    def __init__(self, frame, valid_extensions, loader, click_handler, asset_map):
        self.frame = frame
        self.valid_extensions = valid_extensions
        self.loader = loader
        self.click_handler = click_handler

        self.items = []
        self.loaded_widgets = {}

        self.cell_size = 200
        self.padding = 5
        self.columns = 1
        self._last_width = None

        self._collect_paths()

        self.executor = ThreadedExecutor(max_workers=2)

        self.asset_map = asset_map or {}

        self._render_pending = False

        self.ui_queue = []

        self.process_ui_queue()

    def _collect_paths(self):
        if not ASSETS_DIR.exists():
            return

        self.items = [
            p for p in ASSETS_DIR.glob("*")
            if p.suffix.lower() in self.valid_extensions
        ]

    def calculate_layout(self):
        width = self.frame.winfo_width()

        if width == self._last_width:
            return

        self._last_width = width

        self.columns = max(1, width // (self.cell_size + self.padding))
        self.cell_size = (width // self.columns) - self.padding

    def get_visible_range(self):
        canvas = self.frame._parent_canvas

        y_start = canvas.canvasy(0)
        y_end = y_start + canvas.winfo_height()

        row_height = self.cell_size + self.padding

        start_row = int(y_start // row_height)
        end_row = int(y_end // row_height) + 1

        return start_row, end_row

    def render_visible(self):
        if self._render_pending:
            return

        self._render_pending = True
        self.frame.after(50, self._perform_render)

    def _perform_render(self):
        self._render_pending = False

        self.calculate_layout()
        start_row, end_row = self.get_visible_range()

        buffer = 1

        for index, path in enumerate(self.items):
            row = index // self.columns

            if (
                row < start_row - buffer
                or row > end_row + buffer
                or index in self.loaded_widgets
            ):
                continue

            self.loaded_widgets[index] = "loading"

            self.executor.submit_task(self._threaded_load, row, index, path)

    def _threaded_load(self, row, index, path):
        try:
            col = index % self.columns

            img = self.loader(path, (self.cell_size, self.cell_size))

            ctk_img = ctk.CTkImage(
                light_image=img,
                dark_image=img,
                size=(self.cell_size, self.cell_size)
            )

            self.ui_queue.append((index, path, ctk_img, row, col))

        except Exception as e:
            print(f"Error loading {path}: {e}")

    def process_ui_queue(self):
        batch_size = 4

        for _ in range(min(batch_size, len(self.ui_queue))):
            index, path, ctk_img, row, col = self.ui_queue.pop(0)
            self._create_widget(index, path, ctk_img, row, col)

        self.frame.after(16, self.process_ui_queue)

    def _create_widget(self, index, path, ctk_img, row, col):
        label = ctk.CTkLabel(self.frame, image=ctk_img, text="")
        label.image = ctk_img

        label.bind("<Button-1>", lambda e, p=path: self.click_handler(p))
        label.bind("<Enter>", lambda e, p=path: self.show_tooltip(e, p))
        label.bind("<Leave>", self.hide_tooltip)

        label.grid(row=row, column=col, padx=5, pady=5)

        self.loaded_widgets[index] = label

    def show_tooltip(self, event, path):
        filename = path.name
        pages = self.asset_map.get(filename, [])

        text = "\n".join(pages) if pages else "No references found"

        if not hasattr(self, "tooltip") or self.tooltip is None:
            self.tooltip = ctk.CTkToplevel(self.frame)
            self.tooltip.wm_overrideredirect(True)

            self.tooltip_label = ctk.CTkLabel(self.tooltip, padx=10, pady=5)
            self.tooltip_label.pack()

        self.tooltip_label.configure(text=text)

        x = event.x_root + 10
        y = event.y_root + 10
        self.tooltip.wm_geometry(f"+{x}+{y}")
        self.tooltip.deiconify()

    def hide_tooltip(self, event=None):
        if hasattr(self, "tooltip") and self.tooltip:
            self.tooltip.withdraw()

    def clear(self):
        for widget in self.frame.winfo_children():
            widget.destroy()

        self.loaded_widgets.clear()
        self.ui_queue.clear()

    def shutdown(self):
        self.executor.shutdown()