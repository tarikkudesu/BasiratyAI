"""
Image processing utilities
"""

import io
import logging

import cv2
import numpy as np
from PIL import Image

from config import TARGET_IMAGE_SIZE

logger = logging.getLogger(__name__)


def bytes_to_image(image_bytes: bytes) -> np.ndarray:
    """Convert raw bytes to OpenCV BGR image array"""
    try:
        pil_image = Image.open(io.BytesIO(image_bytes))
        image_rgb = np.array(pil_image.convert("RGB"))
        return cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
    except Exception as e:
        logger.error(f"Image conversion error: {e}")
        raise


def resize_image(image: np.ndarray, target_size: int = TARGET_IMAGE_SIZE) -> np.ndarray:
    """Resize image to target size for YOLO inference"""
    return cv2.resize(image, (target_size, target_size), interpolation=cv2.INTER_LINEAR)
