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

# Global path detection model
_path_model: Optional[YOLO] = None

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


def load_path_model(model_path: str = "best.pt") -> YOLO:
    """Load path detection model and cache globally"""
    global _path_model
    logger.info(f"Loading path detection model: {model_path}")
    _path_model = YOLO(model_path)
    logger.info("✓ Path detection model loaded successfully")
    return _path_model


def get_path_model() -> Optional[YOLO]:
    """Get the cached path detection model instance"""
    return _path_model
