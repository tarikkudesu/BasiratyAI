"""
Image processing utilities
"""

import io
import logging
import os
from datetime import datetime

import cv2
import numpy as np
from PIL import Image, ExifTags

from config import TARGET_IMAGE_SIZE, PROCESSED_IMAGES_DIR, SAVE_PROCESSED_IMAGES

logger = logging.getLogger(__name__)


def apply_exif_orientation(pil_image: Image.Image) -> Image.Image:
    """
    Apply EXIF orientation to correct image rotation.
    Mobile cameras often store rotation in EXIF metadata rather than rotating pixels.
    """
    try:
        # Find the orientation tag
        orientation_key = None
        for key in ExifTags.TAGS:
            if ExifTags.TAGS[key] == "Orientation":
                orientation_key = key
                break

        if orientation_key is None:
            return pil_image

        exif = pil_image._getexif()
        if exif is None:
            return pil_image

        orientation = exif.get(orientation_key)
        if orientation is None:
            return pil_image

        # Apply rotation based on EXIF orientation value
        if orientation == 2:
            pil_image = pil_image.transpose(Image.FLIP_LEFT_RIGHT)
        elif orientation == 3:
            pil_image = pil_image.rotate(180)
        elif orientation == 4:
            pil_image = pil_image.transpose(Image.FLIP_TOP_BOTTOM)
        elif orientation == 5:
            pil_image = pil_image.rotate(-90, expand=True).transpose(Image.FLIP_LEFT_RIGHT)
        elif orientation == 6:
            pil_image = pil_image.rotate(-90, expand=True)
        elif orientation == 7:
            pil_image = pil_image.rotate(90, expand=True).transpose(Image.FLIP_LEFT_RIGHT)
        elif orientation == 8:
            pil_image = pil_image.rotate(90, expand=True)

        return pil_image
    except Exception as e:
        logger.warning(f"Could not apply EXIF orientation: {e}")
        return pil_image


def bytes_to_image(image_bytes: bytes) -> np.ndarray:
    """Convert raw bytes to OpenCV BGR image array with correct orientation"""
    try:
        pil_image = Image.open(io.BytesIO(image_bytes))

        # Apply EXIF orientation to fix rotation from mobile cameras
        pil_image = apply_exif_orientation(pil_image)

        image_rgb = np.array(pil_image.convert("RGB"))
        return cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
    except Exception as e:
        logger.error(f"Image conversion error: {e}")
        raise


def resize_image(image: np.ndarray, max_size: int = TARGET_IMAGE_SIZE) -> np.ndarray:
    """
    Resize image while preserving aspect ratio.
    Only downscales if the image is larger than max_size.
    """
    height, width = image.shape[:2]

    # If image is already smaller than max_size, return as-is
    if max(height, width) <= max_size:
        return image

    # Calculate scale factor to fit within max_size while preserving aspect ratio
    scale = max_size / max(height, width)
    new_width = int(width * scale)
    new_height = int(height * scale)

    return cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LINEAR)


def save_processed_image(image: np.ndarray, boxes: list = None, status: str = "unknown", confidence: float = 0.0) -> str:
    """
    Save processed image with detection bounding boxes drawn.

    Args:
        image: Original image (BGR format)
        boxes: List of bounding box coordinates [(x1, y1, x2, y2), ...]
        status: Detection status (PROCEED, STOP, etc.)
        confidence: Detection confidence score

    Returns:
        Path to saved image or empty string if saving is disabled
    """
    if not SAVE_PROCESSED_IMAGES:
        return ""

    try:
        # Create output directory if it doesn't exist
        os.makedirs(PROCESSED_IMAGES_DIR, exist_ok=True)

        # Create a copy of the image to draw on
        output_image = image.copy()

        # Define colors based on status
        color_map = {
            "PROCEED": (0, 255, 0),  # Green
            "STOP": (0, 0, 255),  # Red
            "WARNING": (0, 165, 255),  # Orange
            "ERROR": (128, 128, 128),  # Gray
        }
        color = color_map.get(status, (255, 255, 255))  # Default white

        # Draw bounding boxes if provided
        if boxes:
            for box in boxes:
                x1, y1, x2, y2 = map(int, box)
                cv2.rectangle(output_image, (x1, y1), (x2, y2), color, 2)

        # Add status label
        label = f"{status} ({confidence:.2f})"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.7
        thickness = 2

        # Get text size for background rectangle
        (text_width, text_height), baseline = cv2.getTextSize(label, font, font_scale, thickness)

        # Draw background rectangle for text
        cv2.rectangle(output_image, (10, 10), (20 + text_width, 30 + text_height), color, -1)

        # Draw text
        cv2.putText(output_image, label, (15, 25 + text_height // 2), font, font_scale, (255, 255, 255), thickness)

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"{status.lower()}_{timestamp}.jpg"
        filepath = os.path.join(PROCESSED_IMAGES_DIR, filename)

        # Save the image
        cv2.imwrite(filepath, output_image)
        logger.info(f"Saved processed image: {filepath}")

        return filepath

    except Exception as e:
        logger.error(f"Error saving processed image: {e}")
        return ""
