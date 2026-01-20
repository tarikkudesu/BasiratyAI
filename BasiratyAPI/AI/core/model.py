"""
YOLO model loading and PyTorch compatibility patches
"""

import logging
import os
from typing import Optional

os.environ["TORCH_FORCE_WEIGHTS_ONLY_LOAD"] = "0"

import torch
from ultralytics import YOLO

logger = logging.getLogger(__name__)

# Global model instance
_model: Optional[YOLO] = None

# Patch torch.load for ultralytics compatibility
_original_torch_load = torch.load


def _patched_torch_load(f, *args, **kwargs):
    if "weights_only" not in kwargs:
        kwargs["weights_only"] = False
    return _original_torch_load(f, *args, **kwargs)


torch.load = _patched_torch_load

# PyTorch 2.6+ compatibility
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
    pass


def load_yolo_model(model_path: str = "yolov8n.pt") -> YOLO:
    """Load YOLOv8 model and cache globally"""
    global _model
    logger.info(f"Loading YOLO model: {model_path}")
    _model = YOLO(model_path)
    logger.info("✓ Model loaded successfully")
    return _model


def get_model() -> Optional[YOLO]:
    """Get the cached YOLO model instance"""
    return _model
