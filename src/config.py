"""
Configuration module for directory paths and UI settings.
"""

from pathlib import Path
import sys
import customtkinter as ctk


def get_base_path():
    if getattr(sys, "frozen", False):
        # Looks for the Logseq directory where the executable is placed (deployment with pyinstaller)
        return Path(sys.executable).parent
    # Looks for the Logseq directory in the root of the project (development)
    return Path(__file__).resolve().parent.parent


BASE_PATH = get_base_path()

BASE_DIR = BASE_PATH / "Notes" # Please adjust to your Logseq directory name
ASSETS_DIR = BASE_DIR / "assets"
PAGE_DIRS = [BASE_DIR / "pages", BASE_DIR / "journals"]
WHITEBOARDS_DIR = BASE_DIR / "whiteboards"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
