"""
Smart Glasses Navigation Server
Real-Time Computer Vision System for the Blind
Author: Principal Software Architect
"""

import asyncio
import io
import logging
import os
from typing import Dict, Optional
from ultralytics import YOLO

# Set PyTorch to allow loading legacy weights (must be set before importing torch)
os.environ["TORCH_FORCE_WEIGHTS_ONLY_LOAD"] = "0"

import cv2
import numpy as np
import torch
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image

# Monkey-patch torch.load to use weights_only=False by default for ultralytics compatibility
_original_torch_load = torch.load


def _patched_torch_load(f, *args, **kwargs):
    """Patched torch.load that defaults to weights_only=False for YOLO model compatibility"""
    if "weights_only" not in kwargs:
        kwargs["weights_only"] = False
    return _original_torch_load(f, *args, **kwargs)


torch.load = _patched_torch_load


# PyTorch 2.6+ compatibility: Add required classes to safe globals
try:
    torch.serialization.add_safe_globals(
        [
            torch.nn.modules.container.Sequential,
            torch.nn.modules.conv.Conv2d,
            torch.nn.modules.pooling.MaxPool2d,
            torch.nn.modules.activation.ReLU,
            torch.nn.modules.batchnorm.BatchNorm2d,
        ]
    )
except Exception:
    pass  # Fallback for older PyTorch versions

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Smart Glasses Navigation API", description="Real-time object detection and navigation for visually impaired users", version="1.0.0")

# CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global YOLOv8-nano model (loaded once at startup)
model: Optional[YOLO] = None

# COCO class IDs for navigation - Expanded Detection List
MONITORED_CLASSES = {
    # Vehicles
    0: "person",
    1: "bicycle",
    2: "car",
    3: "motorcycle",
    5: "bus",
    6: "train",
    7: "truck",
    # Street Items
    9: "traffic light",
    10: "fire hydrant",
    11: "stop sign",
    13: "bench",
    # Animals
    15: "cat",
    16: "dog",
    17: "horse",
    # Trip Hazards
    24: "backpack",
    25: "umbrella",
    26: "handbag",
    28: "suitcase",
    32: "sports ball",
    # Indoor Obstacles
    56: "chair",
    57: "couch",
    58: "potted plant",
    59: "bed",
    60: "dining table",
    61: "toilet",
}

# Constants for Safe Zone Algorithm
SAFE_ZONE_CENTER_PERCENT = 0.50  # Center 50% of image
IMMEDIATE_DANGER_RATIO = 0.4  # Box height > 40% of image height
APPROACHING_RATIO = 0.2  # Box height > 20% of image height
TARGET_IMAGE_SIZE = 640  # YOLOv8 input size


@app.on_event("startup")
async def load_model():
    """Load YOLOv8-nano model at server startup"""
    global model
    try:
        logger.info("Loading YOLOv8-nano model...")
        model = YOLO("yolov8n.pt")  # YOLOv8-nano for speed
        logger.info("✓ Model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise


def bytes_to_image(image_bytes: bytes) -> np.ndarray:
    """
    Convert raw bytes to OpenCV image array

    Args:
        image_bytes: Raw image data as bytes

    Returns:
        numpy.ndarray: Image in BGR format for OpenCV/YOLO
    """
    try:
        # Convert bytes to PIL Image
        pil_image = Image.open(io.BytesIO(image_bytes))

        # Convert to RGB (PIL) then to BGR (OpenCV)
        image_rgb = np.array(pil_image.convert("RGB"))
        image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

        return image_bgr
    except Exception as e:
        logger.error(f"Image conversion error: {e}")
        raise


def resize_image(image: np.ndarray, target_size: int = TARGET_IMAGE_SIZE) -> np.ndarray:
    """
    Resize image to target size for YOLO inference

    Args:
        image: Input image
        target_size: Target size (default 640x640)

    Returns:
        Resized image
    """
    return cv2.resize(image, (target_size, target_size), interpolation=cv2.INTER_LINEAR)


def calculate_position(box_center_x: float, image_width: int) -> str:
    """
    Determine if object is left, center, or right of frame

    Args:
        box_center_x: X coordinate of bounding box center
        image_width: Width of the image

    Returns:
        Position as string: "left", "center", or "right"
    """
    left_boundary = image_width * 0.33
    right_boundary = image_width * 0.67

    if box_center_x < left_boundary:
        return "left"
    elif box_center_x > right_boundary:
        return "right"
    else:
        return "center"


def calculate_distance(box_height: float, image_height: int) -> str:
    """
    Calculate proximity based on box height ratio

    Args:
        box_height: Height of bounding box
        image_height: Height of the image

    Returns:
        Distance classification: "immediate", "approaching", or "far"
    """
    ratio = box_height / image_height

    if ratio > IMMEDIATE_DANGER_RATIO:
        return "immediate"
    elif ratio > APPROACHING_RATIO:
        return "approaching"
    else:
        return "far"


def is_in_safe_zone(box_center_x: float, image_width: int) -> bool:
    """
    Check if object is within the Safe Path (center 50% of image)

    Args:
        box_center_x: X coordinate of bounding box center
        image_width: Width of the image

    Returns:
        True if object is in safe zone, False otherwise
    """
    safe_zone_start = image_width * (0.5 - SAFE_ZONE_CENTER_PERCENT / 2)
    safe_zone_end = image_width * (0.5 + SAFE_ZONE_CENTER_PERCENT / 2)

    return safe_zone_start <= box_center_x <= safe_zone_end


def process_detections(results, image_width: int, image_height: int) -> Optional[Dict]:
    """
    Process YOLO detections and apply Safe Zone algorithm

    Args:
        results: YOLO inference results
        image_width: Width of the image
        image_height: Height of the image

    Returns:
        Most critical obstacle in Safe Zone, or None if path is clear
    """
    critical_obstacle = None
    max_threat_score = 0.0

    for result in results:
        boxes = result.boxes

        for box in boxes:
            # Extract detection data
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])

            # Filter: Only process monitored classes
            if class_id not in MONITORED_CLASSES:
                continue

            # Extract bounding box coordinates
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            box_center_x = (x1 + x2) / 2
            box_height = y2 - y1

            # CRITICAL: Filter out objects outside Safe Zone
            if not is_in_safe_zone(box_center_x, image_width):
                continue

            # Calculate threat metrics
            distance = calculate_distance(box_height, image_height)
            position = calculate_position(box_center_x, image_width)
            label = MONITORED_CLASSES[class_id]

            # Threat scoring (higher = more dangerous)
            threat_score = confidence
            if distance == "immediate":
                threat_score *= 3.0
            elif distance == "approaching":
                threat_score *= 2.0

            # Select most critical obstacle
            if threat_score > max_threat_score:
                max_threat_score = threat_score
                critical_obstacle = {"label": label, "distance": distance, "position": position, "confidence": round(confidence, 2)}

    return critical_obstacle


def generate_navigation_response(obstacle: Optional[Dict]) -> Dict:
    """
    Generate navigation JSON response with voice feedback

    Args:
        obstacle: Most critical detected obstacle or None

    Returns:
        Navigation response dictionary
    """
    if obstacle is None:
        return {"status": "CLEAR", "voice_feedback": "Path is clear. Safe to proceed.", "obstacle": None}

    # Determine status based on distance
    if obstacle["distance"] == "immediate":
        status = "STOP"
        action = "Stop"
    elif obstacle["distance"] == "approaching":
        status = "WARNING"
        action = "Caution"
    else:
        status = "CLEAR"
        action = "Aware"

    # Generate natural voice feedback
    label_capitalized = obstacle["label"].title()
    position_text = obstacle["position"]
    distance_text = obstacle["distance"]

    if obstacle["distance"] == "immediate":
        voice_feedback = f"{action}. {label_capitalized} immediately ahead."
    else:
        voice_feedback = f"{action}. {label_capitalized} {distance_text} on the {position_text}."

    return {"status": status, "voice_feedback": voice_feedback, "obstacle": obstacle}


async def run_inference(image: np.ndarray) -> Dict:
    """
    Run YOLOv8 inference and generate navigation response

    Args:
        image: Input image as numpy array

    Returns:
        Navigation response dictionary
    """
    try:
        # Resize image for optimal YOLO performance
        resized_image = resize_image(image)
        image_height, image_width = resized_image.shape[:2]

        # Run YOLO inference (blocking operation in executor to avoid blocking event loop)
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(None, lambda: model(resized_image, conf=0.25, verbose=False))

        # Process detections with Safe Zone algorithm
        critical_obstacle = process_detections(results, image_width, image_height)

        # Generate navigation response
        response = generate_navigation_response(critical_obstacle)

        return response

    except Exception as e:
        logger.error(f"Inference error: {e}")
        return {"status": "ERROR", "voice_feedback": "System error. Please reconnect.", "obstacle": None}


@app.websocket("/ws/navigate")
async def websocket_navigate(websocket: WebSocket):
    """
    WebSocket endpoint for real-time navigation

    Accepts continuous image stream and returns navigation feedback
    Implements frame skipping (processes every 3rd frame)
    """
    await websocket.accept()
    logger.info(f"WebSocket connected: {websocket.client}")

    frame_counter = 0

    try:
        while True:
            # Receive binary image data
            image_bytes = await websocket.receive_bytes()
            frame_counter += 1

            # Frame Skipping: Process only every 3rd frame
            if frame_counter % 3 != 0:
                continue

            # Convert bytes to image
            image = bytes_to_image(image_bytes)

            # Run inference and get navigation response
            response = await run_inference(image)

            # Send JSON response back to client
            await websocket.send_json(response)

            # Log critical alerts
            if response["status"] in ["STOP", "WARNING"]:
                logger.warning(f"Alert: {response['voice_feedback']}")

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {websocket.client}")

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.close()
        except:  # noqa: E722
            pass


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"service": "Smart Glasses Navigation API", "status": "operational", "model": "YOLOv8-nano", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {"status": "healthy", "model_loaded": model is not None, "monitored_classes": len(MONITORED_CLASSES), "safe_zone_width": f"{SAFE_ZONE_CENTER_PERCENT * 100}%"}


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting Smart Glasses Navigation Server...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info", ws_ping_interval=20, ws_ping_timeout=20)
