"""
Geometric calculations for distance and position estimation
"""

from config import (
    SAFE_ZONE_CENTER_PERCENT,
    IMMEDIATE_DANGER_RATIO,
    APPROACHING_RATIO,
    TYPICAL_HEIGHTS,
)


def calculate_position(box_center_x: float, image_width: int) -> str:
    """Determine if object is left, center, or right of frame"""
    left_boundary = image_width * 0.33
    right_boundary = image_width * 0.67

    if box_center_x < left_boundary:
        return "left"
    elif box_center_x > right_boundary:
        return "right"
    return "center"


def calculate_distance(box_height: float, image_height: int) -> str:
    """Calculate proximity classification based on box height ratio"""
    ratio = box_height / image_height

    if ratio > IMMEDIATE_DANGER_RATIO:
        return "immediate"
    elif ratio > APPROACHING_RATIO:
        return "approaching"
    return "far"


def estimate_distance_meters(box_height: float, image_height: int, object_label: str) -> float:
    """
    Estimate distance to object in meters using perspective projection.
    Uses typical real-world heights and inverse perspective formula.
    """
    real_height = TYPICAL_HEIGHTS.get(object_label, 1.5)
    focal_length = image_height * 0.8

    if box_height > 0:
        distance = (real_height * focal_length) / box_height
        return round(distance, 1)

    return 10.0


def is_in_safe_zone(x1: float, x2: float, image_width: int) -> bool:
    """Check if bounding box intersects with the safe zone (center 50% of image)"""
    safe_zone_start = image_width * (0.5 - SAFE_ZONE_CENTER_PERCENT / 2)
    safe_zone_end = image_width * (0.5 + SAFE_ZONE_CENTER_PERCENT / 2)

    return x2 > safe_zone_start and x1 < safe_zone_end
