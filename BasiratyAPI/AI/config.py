"""
Configuration constants for the Smart Glasses Navigation System
"""

# COCO class IDs for navigation - objects relevant to blind navigation
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

# Typical real-world heights in meters for distance estimation
TYPICAL_HEIGHTS = {
    "person": 1.7,
    "bicycle": 1.1,
    "car": 1.5,
    "motorcycle": 1.2,
    "bus": 3.0,
    "train": 4.0,
    "truck": 2.5,
    "traffic light": 3.5,
    "fire hydrant": 0.7,
    "stop sign": 2.0,
    "bench": 0.8,
    "cat": 0.3,
    "dog": 0.6,
    "horse": 1.6,
    "chair": 0.9,
    "couch": 0.8,
    "potted plant": 0.5,
    "bed": 0.6,
    "dining table": 0.75,
}

# Safe Zone Algorithm thresholds
SAFE_ZONE_CENTER_PERCENT = 0.50
IMMEDIATE_DANGER_RATIO = 0.4
APPROACHING_RATIO = 0.2

# YOLO configuration
TARGET_IMAGE_SIZE = 640
CONFIDENCE_THRESHOLD = 0.25
