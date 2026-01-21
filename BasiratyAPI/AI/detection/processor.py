"""
YOLO detection processing with Safe Zone algorithm
"""

from typing import Dict, Optional

from config import MONITORED_CLASSES
from utils.geometry import (
    calculate_position,
    calculate_distance,
    estimate_distance_meters,
    is_in_safe_zone,
)


def process_detections(results, image_width: int, image_height: int) -> Optional[Dict]:
    """
    Process YOLO detections and apply Safe Zone algorithm.
    Returns the most critical obstacle in the safe zone, or None if path is clear.
    """
    critical_obstacle = None
    max_threat_score = 0.0

    for result in results:
        for box in result.boxes:
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])

            if class_id not in MONITORED_CLASSES:
                continue

            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            box_center_x = (x1 + x2) / 2
            box_height = y2 - y1
            box_width = x2 - x1

            if not is_in_safe_zone(x1, x2, image_width):
                continue

            distance = calculate_distance(box_height, image_height)
            position = calculate_position(box_center_x, image_width)
            label = MONITORED_CLASSES[class_id]
            distance_meters = estimate_distance_meters(box_height, image_height, label, box_width, image_width)

            # Threat scoring: closer objects are more dangerous
            threat_score = confidence
            if distance == "immediate":
                threat_score *= 3.0
            elif distance == "approaching":
                threat_score *= 2.0

            if threat_score > max_threat_score:
                max_threat_score = threat_score
                critical_obstacle = {
                    "label": label,
                    "distance": distance,
                    "distance_meters": distance_meters,
                    "position": position,
                    "confidence": round(confidence, 2),
                }

    return critical_obstacle
