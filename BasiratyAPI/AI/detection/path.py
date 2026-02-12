"""
Path detection processing for navigation
"""

import logging
from typing import Dict, Optional

import numpy as np

from core import get_path_model
from utils.image import save_processed_image

logger = logging.getLogger(__name__)


def analyze_path(image: np.ndarray) -> Optional[Dict]:
    """
    Analyze image for walkable path using the trained path detection model.

    Returns:
        Dictionary with path analysis or None if no path detected
    """
    try:
        path_model = get_path_model()
        if path_model is None:
            logger.error("Path detection model not loaded")
            return None

        # Run path detection inference
        results = path_model(image, conf=0.5, verbose=False)

        if not results or len(results) == 0:
            # Save image with no detection
            save_processed_image(image, boxes=None, status="STOP", confidence=0.0)
            return {"path_available": False, "confidence": 0.0, "action": "STOP", "reason": "No path detected"}

        # Process results - assuming the model detects "path" class
        for result in results:
            if result.boxes is None or len(result.boxes) == 0:
                continue

            for box in result.boxes:
                confidence = float(box.conf[0])
                class_id = int(box.cls[0])

                # Get bounding box coordinates
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()

                # Calculate path metrics
                box_width = x2 - x1
                box_height = y2 - y1
                image_height, image_width = image.shape[:2]

                # Path coverage - how much of the image is path
                path_coverage = (box_width * box_height) / (image_width * image_height)

                # Path position (vertical) - lower in image means closer
                vertical_position = (y1 + y2) / 2 / image_height

                # Determine if user can proceed
                can_proceed = evaluate_path_safety(confidence, path_coverage, vertical_position, box_width, image_width)

                # Save processed image with bounding box
                status = "PROCEED" if can_proceed else "STOP"
                save_processed_image(image, boxes=[(x1, y1, x2, y2)], status=status, confidence=confidence)

                return {
                    "path_available": can_proceed,
                    "confidence": round(confidence, 2),
                    "coverage": round(path_coverage * 100, 1),
                    "action": "PROCEED" if can_proceed else "STOP",
                    "reason": get_path_feedback(can_proceed, confidence, path_coverage),
                }

        # No valid path detected - save image
        save_processed_image(image, boxes=None, status="STOP", confidence=0.0)
        return {"path_available": False, "confidence": 0.0, "action": "STOP", "reason": "No clear path detected"}

    except Exception as e:
        logger.error(f"Path analysis error: {e}")
        return None


def evaluate_path_safety(confidence: float, coverage: float, vertical_position: float, path_width: float, image_width: float) -> bool:
    """
    Evaluate if the detected path is safe for the user to proceed.

    Args:
        confidence: Model confidence in path detection (0-1)
        coverage: Percentage of image covered by path (0-1)
        vertical_position: Vertical position of path center (0=top, 1=bottom)
        path_width: Width of detected path in pixels
        image_width: Width of image in pixels

    Returns:
        True if safe to proceed, False otherwise
    """
    # Minimum confidence threshold
    MIN_CONFIDENCE = 0.5

    # Minimum path coverage (path should cover at least 15% of image)
    MIN_COVERAGE = 0.15

    # Path should be in lower part of image (closer to user)
    MIN_VERTICAL_POSITION = 0.3

    # Path should be wide enough (at least 40% of image width)
    MIN_WIDTH_RATIO = 0.4

    width_ratio = path_width / image_width

    # All safety criteria must be met
    is_confident = confidence >= MIN_CONFIDENCE
    is_sufficient_coverage = coverage >= MIN_COVERAGE
    is_close_enough = vertical_position >= MIN_VERTICAL_POSITION
    is_wide_enough = width_ratio >= MIN_WIDTH_RATIO

    # Convert to native Python bool for JSON serialization
    return bool(is_confident and is_sufficient_coverage and is_close_enough and is_wide_enough)


def get_path_feedback(can_proceed: bool, confidence: float, coverage: float) -> str:
    """Generate human-readable feedback about path status"""
    if can_proceed:
        if confidence > 0.85 and coverage > 0.3:
            return "Clear wide path ahead"
        elif confidence > 0.7:
            return "Path detected, proceed with caution"
        else:
            return "Narrow path detected"
    else:
        if confidence < 0.6:
            return "Uncertain path detection"
        elif coverage < 0.15:
            return "Path too narrow"
        else:
            return "Path not safe for navigation"
