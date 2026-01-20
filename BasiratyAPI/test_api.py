#!/usr/bin/env python3
"""
Test script for Smart Glasses Navigation API
"""

import requests

API_URL = "http://localhost:7417"


def test_health():
    """Test health endpoints"""
    print("Testing health endpoints...")

    # Root endpoint
    response = requests.get(f"{API_URL}/")
    print(f"GET / → {response.json()}")

    # Health check
    response = requests.get(f"{API_URL}/health")
    print(f"GET /health → {response.json()}\n")


def test_navigation(image_path: str):
    """Test navigation endpoint with image"""
    print(f"Testing navigation with image: {image_path}")

    with open(image_path, "rb") as image_file:
        files = {"file": image_file}
        response = requests.post(f"{API_URL}/navigate", files=files)

        result = response.json()
        print(f"Status: {result['status']}")
        print(f"Voice Feedback: {result['voice_feedback']}")
        if result["obstacle"]:
            print(f"Obstacle: {result['obstacle']}")
        print()


if __name__ == "__main__":
    # Test health endpoints
    test_health()

    # Test navigation with an image
    # Replace with your actual image path
    image_path = "test_image.jpg"

    try:
        test_navigation(image_path)
    except FileNotFoundError:
        print(f"⚠ Image not found: {image_path}")
        print("Please provide a valid image path to test navigation")
