"""
Wall detection using edge detection and contour analysis
"""

from typing import Dict, Optional

import cv2
import numpy as np

from config import (
    SAFE_ZONE_CENTER_PERCENT,
    WALL_MIN_HEIGHT_RATIO,
    WALL_MIN_WIDTH_RATIO,
    WALL_EDGE_DENSITY_THRESHOLD,
)
from utils.geometry import calculate_position


def detect_wall(image: np.ndarray) -> Optional[Dict]:
    """
    Detect walls or large vertical surfaces using edge detection.
    Returns wall obstacle dict if detected in safe zone, None otherwise.
    """
    image_height, image_width = image.shape[:2]

    safe_zone_start = int(image_width * (0.5 - SAFE_ZONE_CENTER_PERCENT / 2))
    safe_zone_end = int(image_width * (0.5 + SAFE_ZONE_CENTER_PERCENT / 2))
    safe_zone_width = safe_zone_end - safe_zone_start

    safe_zone_image = image[:, safe_zone_start:safe_zone_end]
    gray = cv2.cvtColor(safe_zone_image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)

    # Check for large contours that could be walls
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        height_ratio = h / image_height
        width_ratio = w / safe_zone_width

        if height_ratio >= WALL_MIN_HEIGHT_RATIO and width_ratio >= WALL_MIN_WIDTH_RATIO:
            bottom_y = y + h
            if bottom_y > image_height * 0.7:
                distance, distance_meters = "immediate", 1.0
            elif bottom_y > image_height * 0.5:
                distance, distance_meters = "approaching", 2.5
            else:
                distance, distance_meters = "far", 5.0

            wall_center_x = safe_zone_start + x + w / 2
            position = calculate_position(wall_center_x, image_width)
            confidence = round(min(height_ratio * width_ratio * 2, 0.95), 2)

            return {
                "label": "wall",
                "distance": distance,
                "distance_meters": distance_meters,
                "position": position,
                "confidence": confidence,
            }

    # Alternative: analyze edge density in horizontal bands
    wall = _detect_wall_by_edge_density(gray, edges, safe_zone_width, image_height)
    if wall:
        return wall

    return None


def _detect_wall_by_edge_density(
    gray: np.ndarray,
    edges: np.ndarray,
    safe_zone_width: int,
    image_height: int,
) -> Optional[Dict]:
    """Detect walls by analyzing edge density patterns in horizontal bands"""
    band_height = image_height // 4

    for i in range(4):
        band = edges[i * band_height : (i + 1) * band_height, :]
        band_density = np.sum(band > 0) / (safe_zone_width * band_height)

        if i >= 2 and band_density > WALL_EDGE_DENSITY_THRESHOLD:
            vertical_edges = cv2.Sobel(gray[i * band_height : (i + 1) * band_height, :], cv2.CV_64F, 1, 0)
            if np.mean(np.abs(vertical_edges)) > 10:
                distance = "immediate" if i == 3 else "approaching"
                distance_meters = 1.5 if i == 3 else 3.0

                return {
                    "label": "wall",
                    "distance": distance,
                    "distance_meters": distance_meters,
                    "position": "center",
                    "confidence": 0.7,
                }

    return None
