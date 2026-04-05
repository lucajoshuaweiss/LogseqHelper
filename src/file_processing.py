"""
Handles file scanning and link processing.
"""

from difflib import unified_diff
from pathlib import Path

from src.config import PAGE_DIRS
from src.regex_utils import protect_code, restore_code, link_text, LINK_RE, ASSET_LINK_RE


def collect_pages():
    """
    Collects all page names from markdown files and their internal links.

    Returns:
        set: Set of page names.
    """
    pages = set()

    for d in PAGE_DIRS:
        if not d.exists():
            continue

        for f in d.glob("*.md"):
            pages.add(f.stem)

    for d in PAGE_DIRS:
        if not d.exists():
            continue

        for f in d.glob("*.md"):
            text = f.read_text(encoding="utf-8")
            for link in LINK_RE.findall(text):
                pages.add(link)

    return pages


def process_files_for_link_changes(mode: str, output_callback):
    """
    Processes markdown files and applies or previews link changes.

    Args:
        mode (str): "preview" for preview, "change" to apply changes.
        output_callback (Callable): Function to handle output logging.
    """
    pages = collect_pages()
    global_changes = 0
    files_with_changes = 0

    for d in PAGE_DIRS:
        if not d.exists():
            continue

        for file in d.glob("*.md"):
            original = file.read_text(encoding="utf-8")

            protected_text, protected = protect_code(original)
            linked_text, changes = link_text(protected_text, pages)
            final_text = restore_code(linked_text, protected)

            if changes == 0:
                continue

            files_with_changes += 1
            global_changes += changes

            output_callback(f"\n{file} ({changes} changes)\n")

            if mode == "preview":
                diff = unified_diff(
                    original.splitlines(),
                    final_text.splitlines(),
                    fromfile="original",
                    tofile="linked",
                    lineterm=""
                )

                for line in diff:
                    output_callback(line + "\n")
            else:
                file.write_text(final_text, encoding="utf-8")
                output_callback("File updated\n")

    output_callback("\n" + "=" * 50 + "\n")
    output_callback(f"Mode: {mode}\n")
    output_callback(f"Files changed: {files_with_changes}\n")
    output_callback(f"Replacements: {global_changes}\n")
    output_callback("=" * 50 + "\n")

def build_asset_map():
    """
    Builds a map of asset links found in markdown files.

    Scans all markdown files in the directories specified by `PAGE_DIRS` 
    and creates a mapping of asset file names to the pages that link to them.

    Returns:
        dict: A dictionary where keys are asset file names and values are lists of page names.
    """
    asset_map = {}

    for d in PAGE_DIRS:
        if not d.exists():
            continue

        for f in d.glob("*.md"):
            text = f.read_text(encoding="utf-8")

            for match in ASSET_LINK_RE.findall(text):
                asset_path = Path(match).name

                asset_map.setdefault(asset_path, []).append(f.stem)

    return asset_map