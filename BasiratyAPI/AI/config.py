"""Configuration constants for Path Detection System"""

import os

# Image processing configuration
TARGET_IMAGE_SIZE = 640

# Processed images storage
PROCESSED_IMAGES_DIR = os.path.join(os.path.dirname(__file__), "processed_images")
SAVE_PROCESSED_IMAGES = True  # Set to False to disable saving
