"""
Utility functions for loading and processing images.
"""

from PIL import Image


def load_thumbnail(img_path, size):
    """
    Loads an image and resizes it to a thumbnail.

    Args:
        img_path (Path): Path to the image file.
        size (tuple[int, int]): Maximum width and height.

    Returns:
        Image: Resized PIL Image object.
    """
    img = Image.open(img_path)
    img.thumbnail(size)
    return img


def load_full_image(img_path, max_size=None):
    """
    Loads an image, optionally resizing it to fit within max_size.

    Args:
        img_path (Path): Path to the image file.
        max_size (tuple[int, int] | None): Maximum size constraint.

    Returns:
        Image: PIL Image object.
    """
    img = Image.open(img_path)

    if max_size:
        img.thumbnail(max_size)

    return img