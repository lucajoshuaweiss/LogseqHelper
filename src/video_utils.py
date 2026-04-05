"""
Utility functions for loading and processing videos.
"""

import cv2
from PIL import Image


def load_video_thumbnail(video_path, size=(200, 200)):
    """
    Extracts a thumbnail from a video (first frame).

    Args:
        video_path (Path): Path to the video file.
        size (tuple[int, int]): Maximum width and height.

    Returns:
        Image: PIL Image object.
    """
    cap = cv2.VideoCapture(str(video_path))
    success, frame = cap.read()
    cap.release()

    if not success or frame is None:
        raise ValueError(f"Cannot read video: {video_path}")

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    img = Image.fromarray(frame)
    img.thumbnail(size)

    return img