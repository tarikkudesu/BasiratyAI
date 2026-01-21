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


def estimate_distance_meters(
    box_height: float,
    image_height: int,
    object_label: str,
    box_width: float = 0,
    image_width: int = 0,
    vertical_fov_degrees: float = 55.0,
) -> float:
    """
    Estimate distance to object in meters using improved perspective projection.

    Uses both height and width measurements when available, with camera FOV
    calibration for more accurate results on mobile devices.

    Args:
        box_height: Bounding box height in pixels
        image_height: Image height in pixels
        object_label: Object class label for real-world size lookup
        box_width: Bounding box width in pixels (optional, for width-based estimation)
        image_width: Image width in pixels (optional)
        vertical_fov_degrees: Camera vertical field of view (typical smartphone: 50-60°)

    Returns:
        Estimated distance in meters
    """
    import math

    if box_height <= 0:
        return 10.0

    real_height = TYPICAL_HEIGHTS.get(object_label, 1.5)

    # Calculate focal length from vertical FOV (more accurate than fixed multiplier)
    # f = (image_height / 2) / tan(fov / 2)
    vertical_fov_rad = math.radians(vertical_fov_degrees)
    focal_length = (image_height / 2) / math.tan(vertical_fov_rad / 2)

    # Height-based distance estimation
    distance_from_height = (real_height * focal_length) / box_height

    # Width-based estimation for objects with known aspect ratios (optional refinement)
    distance_from_width = None
    if box_width > 0 and image_width > 0:
        typical_widths = {
            "person": 0.5,
            "car": 1.8,
            "bicycle": 0.6,
            "motorcycle": 0.8,
            "bus": 2.5,
            "truck": 2.5,
            "chair": 0.5,
            "bench": 1.5,
            "dog": 0.4,
            "cat": 0.25,
        }
        if object_label in typical_widths:
            real_width = typical_widths[object_label]
            # Horizontal FOV approximation (assuming 4:3 or 16:9 aspect ratio)
            aspect_ratio = image_width / image_height
            horizontal_fov_rad = 2 * math.atan(math.tan(vertical_fov_rad / 2) * aspect_ratio)
            focal_length_h = (image_width / 2) / math.tan(horizontal_fov_rad / 2)
            distance_from_width = (real_width * focal_length_h) / box_width

    # Combine estimates if both available (weighted average, prefer height)
    if distance_from_width is not None:
        # Height is generally more reliable, give it 70% weight
        distance = 0.7 * distance_from_height + 0.3 * distance_from_width
    else:
        distance = distance_from_height

    # Apply correction factor for typical detection bbox inaccuracies
    # Bounding boxes often don't capture full object, making distance seem farther
    correction_factor = 0.85
    distance *= correction_factor

    # Clamp to reasonable range
    distance = max(0.3, min(distance, 20.0))

    return round(distance, 1)


def is_in_safe_zone(x1: float, x2: float, image_width: int) -> bool:
    """Check if bounding box intersects with the safe zone (center 50% of image)"""
    safe_zone_start = image_width * (0.5 - SAFE_ZONE_CENTER_PERCENT / 2)
    safe_zone_end = image_width * (0.5 + SAFE_ZONE_CENTER_PERCENT / 2)

    return x2 > safe_zone_start and x1 < safe_zone_end
