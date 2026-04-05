"""
Graphical user interface for the LogseqHelper tool.
"""

import customtkinter as ctk

from src.stats import get_stats
from src.file_processing import process_files_for_link_changes, build_asset_map
from src.image_utils import load_thumbnail, load_full_image
from src.video_utils import load_video_thumbnail
from src.lazy_gallery import LazyGallery
from src.scroll_utils import on_mousewheel, bind_mousewheel, unbind_mousewheel
from src.system_utils import open_file
from src.tasks import run_in_thread


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("LogseqHelper")
        self.geometry("1200x800")
        self.resizable(False, False)

        self.mode = "images"
        self.gallery = None

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)     # images/videos
        self.grid_rowconfigure(1, weight=1)     # output textbox

        self._create_sidebar()
        self._create_main_area()

        self.asset_map = build_asset_map()
        self.load_images()
        self._render_job = None

    def _create_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=200)
        sidebar.grid(row=0, column=0, rowspan=2, sticky="ns")

        ctk.CTkLabel(
            sidebar,
            text="View",
            font=ctk.CTkFont(weight="bold")
        ).pack(pady=(20, 10))

        self.toggle_button = ctk.CTkButton(
            sidebar,
            text="Switch to Videos",
            command=self.toggle_mode
        )
        self.toggle_button.pack(pady=10)

        words, journals, pages, images, whiteboards, videos, links = get_stats()

        ctk.CTkFrame(sidebar, height=2).pack(fill="x", padx=10, pady=15)

        ctk.CTkLabel(
            sidebar,
            text="Stats",
            font=ctk.CTkFont(weight="bold")
        ).pack(pady=(15, 10))

        for label, value in [
        ("Words", words),
        ("Journals", journals),
        ("Pages", pages),
        ("Whiteboards", whiteboards),
        ("Images", images),
        ("Videos", videos),
        ]:
            ctk.CTkLabel(sidebar, text=f"{label}: {value}").pack(pady=5)
        
        # In case the number of links needs to be updated
        self.links_label = ctk.CTkLabel(sidebar, text=f"Links: {links}")
        self.links_label.pack(pady=5)

        ctk.CTkFrame(sidebar, height=2).pack(fill="x", padx=10, pady=15)

        ctk.CTkLabel(
            sidebar,
            text="Linking Actions",
            font=ctk.CTkFont(weight="bold")
        ).pack(pady=(20, 10))

        ctk.CTkButton(
            sidebar,
            text="See unlinked Pages",
            command=lambda: self.run_script("preview")
        ).pack(pady=10)

        ctk.CTkButton(
            sidebar,
            text="Link unlinked Pages",
            command=lambda: self.run_script("change")
        ).pack(pady=10)

    def _create_main_area(self):
        self.image_frame = ctk.CTkScrollableFrame(self)
        self.image_frame.grid(row=0, column=1, sticky="nsew")

        self.image_frame.bind("<Enter>", self._bind_mousewheel)
        self.image_frame.bind("<Leave>", self._unbind_mousewheel)

        self.output = ctk.CTkTextbox(self)
        self.output.configure(state="disabled")
        self.output.grid(row=1, column=1, sticky="nsew")

    def toggle_mode(self):
        if self.mode == "images":
            self.mode = "videos"
            self.toggle_button.configure(text="Switch to Images")
            self.load_videos()
        else:
            self.mode = "images"
            self.toggle_button.configure(text="Switch to Videos")
            self.load_images()

    def log(self, text: str):
        self.output.configure(state="normal")
        self.output.insert("end", text)
        self.output.see("end")
        self.output.configure(state="disabled")

    def run_script(self, mode: str):
        self.output.configure(state="normal")
        self.output.delete("1.0", "end")
        self.output.configure(state="disabled")

        def callback(text):
            self.output.after(0, lambda: self._append_output(text))

        def process_and_update():
            # Process files in a separate thread and update link count after processing
            process_files_for_link_changes(mode, callback)
            self.output.after(0, self.update_links_count)

        run_in_thread(process_and_update)

    def _append_output(self, text):
        # Temporarily enable textbox to insert
        self.output.configure(state="normal")
        self.output.insert("end", text)
        self.output.see("end")
        self.output.configure(state="disabled")

    def update_links_count(self):
        words, journals, pages, images, whiteboards, videos, links = get_stats()

        if self.links_label:
            self.links_label.configure(text=f"Links: {links}")

    def open_image(self, img_path):
        top = ctk.CTkToplevel(self)
        top.title(img_path.name)
        top.geometry("800x800")

        img = load_full_image(img_path, max_size=(800, 800))

        ctk_img = ctk.CTkImage(
            light_image=img,
            dark_image=img,
            size=img.size
        )

        label = ctk.CTkLabel(top, image=ctk_img, text="")
        label.image = ctk_img
        label.pack(expand=True, padx=10, pady=10)

    def open_video(self, video_path):
        open_file(video_path)

    def delayed_render(self):
        # Cancel the previous scheduled render if it exists
        if self._render_job:
            self.after_cancel(self._render_job)
    
        self._render_job = self.after(50, self.gallery.render_visible)

    def _on_mousewheel(self, event):
        on_mousewheel(event, self.image_frame._parent_canvas)

        if self.gallery:
            self.delayed_render()

    def _bind_mousewheel(self, event):
        bind_mousewheel(self.image_frame, self._on_mousewheel)

    def _unbind_mousewheel(self, event):
        unbind_mousewheel(self.image_frame)

    def _init_gallery(self, valid_extensions, loader, click_handler):
        self.gallery = LazyGallery(
            self.image_frame,
            valid_extensions,
            loader,
            click_handler,
            asset_map=self.asset_map
        )

        self.gallery.clear()
        self.gallery.render_visible()

        canvas = self.image_frame._parent_canvas

        canvas.configure(yscrollcommand=self._on_canvas_scroll)

    def _on_canvas_scroll(self, *args):
        if self.image_frame._scrollbar:
            self.image_frame._scrollbar.set(*args)

        if self.gallery:
            self.delayed_render()

    def load_images(self):
        self._init_gallery(
            {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"},
            load_thumbnail,
            self.open_image
        )
        canvas = self.image_frame._parent_canvas
        canvas.yview_moveto(0)

    def load_videos(self):
        self._init_gallery(
            {".mp4", ".mov", ".avi", ".mkv", ".webm"},
            load_video_thumbnail,
            self.open_video
        )
        canvas = self.image_frame._parent_canvas
        canvas.yview_moveto(0)
