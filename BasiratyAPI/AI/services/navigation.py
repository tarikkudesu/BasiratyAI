"""
Navigation service: inference orchestration and response generation
"""

import asyncio
import logging
from typing import Dict, Optional

import numpy as np

from detection import analyze_path
from utils.image import resize_image

logger = logging.getLogger(__name__)


def generate_navigation_response(path_analysis: Optional[Dict]) -> Dict:
    """
    Generate navigation response based on path detection only.
    
    Decision logic:
    - Path available and safe -> PROCEED
    - No path detected -> STOP
    """
    if path_analysis is None:
        logger.error("Path analysis unavailable")
        return {
            "status": "STOP",
            "voice_feedback": "Unable to detect path. Please try again.",
        }
    
    path_available = path_analysis.get("path_available", False)
    path_confidence = path_analysis.get("confidence", 0.0)
    path_reason = path_analysis.get("reason", "Unknown")
    
    if not path_available:
        return {
            "status": "STOP",
            "voice_feedback": f"Stop. {path_reason}.",
            "path": path_analysis,
        }
    
    # Path is available
    if path_confidence > 0.8:
        feedback = "Safe to proceed. Clear path ahead."
    elif path_confidence > 0.6:
        feedback = f"Proceed with caution. {path_reason}."
    else:
        feedback = f"Uncertain path. {path_reason}."
    
    return {
        "status": "PROCEED",
        "voice_feedback": feedback,
        "path": path_analysis,
    }


async def run_inference(image: np.ndarray) -> Dict:
    """Run path detection inference and generate navigation response"""
    try:
        resized_image = resize_image(image)

        # Analyze path using the path detection model
        loop = asyncio.get_event_loop()
        path_analysis = await loop.run_in_executor(None, lambda: analyze_path(resized_image))
        
        # Generate response based on path detection only
        return generate_navigation_response(path_analysis)

    except Exception as e:
        logger.error(f"Inference error: {e}")
        return {
            "status": "ERROR",
            "voice_feedback": "System error. Please reconnect.",
        }
