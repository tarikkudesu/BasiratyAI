"""
Navigation service: inference orchestration and response generation
"""

import asyncio
import logging
from typing import Dict, Optional

import numpy as np

from config import CONFIDENCE_THRESHOLD, DISTANCE_PRIORITY
from core import get_model
from detection import process_detections, detect_wall
from utils.image import resize_image

logger = logging.getLogger(__name__)


def generate_navigation_response(obstacle: Optional[Dict]) -> Dict:
    """Generate navigation JSON response with voice feedback"""
    if obstacle is None:
        return {
            "status": "CLEAR",
            "voice_feedback": "Path is clear. Safe to proceed.",
            "obstacle": None,
        }

    if obstacle["distance"] == "immediate":
        status, action = "STOP", "Stop"
    elif obstacle["distance"] == "approaching":
        status, action = "WARNING", "Caution"
    else:
        status, action = "CLEAR", "Aware"

    label = obstacle["label"].title()
    position = obstacle["position"]
    meters = obstacle["distance_meters"]

    if obstacle["distance"] == "immediate":
        voice_feedback = f"{action}. {label} {meters} meters ahead."
    else:
        voice_feedback = f"{action}. {label} {meters} meters on the {position}."

    return {"status": status, "voice_feedback": voice_feedback, "obstacle": obstacle}


async def run_inference(image: np.ndarray) -> Dict:
    """Run YOLOv8 inference and generate navigation response"""
    try:
        resized_image = resize_image(image)
        image_height, image_width = resized_image.shape[:2]

        model = get_model()
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(None, lambda: model(resized_image, conf=CONFIDENCE_THRESHOLD, verbose=False))

        critical_obstacle = process_detections(results, image_width, image_height)

        # Check for walls and compare priority
        wall_obstacle = detect_wall(resized_image)
        if wall_obstacle:
            if critical_obstacle is None:
                critical_obstacle = wall_obstacle
            elif DISTANCE_PRIORITY.get(wall_obstacle["distance"], 0) > DISTANCE_PRIORITY.get(critical_obstacle["distance"], 0):
                critical_obstacle = wall_obstacle

        return generate_navigation_response(critical_obstacle)

    except Exception as e:
        logger.error(f"Inference error: {e}")
        return {
            "status": "ERROR",
            "voice_feedback": "System error. Please reconnect.",
            "obstacle": None,
        }
