"""
Provides statistics about notes, media, and content.
"""

import re

from src.config import BASE_DIR, ASSETS_DIR, WHITEBOARDS_DIR

WORD_REGEX = re.compile(r"\b\w+\b")
INTERNAL_LINK_REGEX = re.compile(r"\[\[.*?\]\]")


def get_stats():
    """
    Calculates statistics for notes and assets.

    Returns:
        tuple: Word count, journal count, page count,
        image count, whiteboard count, video count, link count.
    """
    word_count = 0
    journal_count = 0
    pages_count = 0
    whiteboard_count = 0
    image_count = 0
    video_count = 0
    link_count = 0

    journals_dir = BASE_DIR / "journals"
    pages_dir = BASE_DIR / "pages"

    def process_files_for_stats(files):
        nonlocal word_count, link_count

        for f in files:
            text = f.read_text(encoding="utf-8")

            word_count += len(WORD_REGEX.findall(text))

            internal_links = INTERNAL_LINK_REGEX.findall(text)
            link_count += len(internal_links)

    if journals_dir.exists():
        files = list(journals_dir.glob("*.md"))
        journal_count = len(files)
        process_files_for_stats(files)

    if pages_dir.exists():
        files = list(pages_dir.glob("*.md"))
        pages_count = len(files)
        process_files_for_stats(files)

    if WHITEBOARDS_DIR.exists():
        whiteboard_count = len([p for p in WHITEBOARDS_DIR.glob("*") if p.is_file()])

    if ASSETS_DIR.exists():
        image_exts = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"}
        video_exts = {".mp4", ".mov", ".avi", ".mkv"}

        image_count = len([p for p in ASSETS_DIR.glob("*") if p.suffix.lower() in image_exts])
        video_count = len([p for p in ASSETS_DIR.glob("*") if p.suffix.lower() in video_exts])

    return (
        word_count,
        journal_count,
        pages_count,
        image_count,
        whiteboard_count,
        video_count,
        link_count,
    )