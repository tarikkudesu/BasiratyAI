"""
Smart Glasses Navigation Server
Real-Time Computer Vision System for the Blind
"""

import logging

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from config import MONITORED_CLASSES, SAFE_ZONE_CENTER_PERCENT
from core import load_yolo_model, get_model
from services import run_inference
from utils import bytes_to_image

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Smart Glasses Navigation API",
    description="Real-time object detection and navigation for visually impaired users",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    """Load YOLO model at server startup"""
    try:
        load_yolo_model("yolov8n.pt")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise


@app.post("/navigate")
async def navigate(file: UploadFile = File(...)):
    """Navigation endpoint: accepts image upload and returns navigation feedback."""
    try:
        image_bytes = await file.read()
        image = bytes_to_image(image_bytes)
        response = await run_inference(image)

        if response["status"] in ["STOP", "WARNING"]:
            logger.warning(f"Alert: {response['voice_feedback']}")

        return response

    except Exception as e:
        logger.error(f"Navigation error: {e}")
        return {
            "status": "ERROR",
            "voice_feedback": "System error. Please try again.",
            "obstacle": None,
        }


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Smart Glasses Navigation API",
        "status": "operational",
        "model": "YOLOv8-nano",
        "version": "1.0.0",
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    model = get_model()
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "monitored_classes": len(MONITORED_CLASSES),
        "safe_zone_width": f"{SAFE_ZONE_CENTER_PERCENT * 100}%",
    }


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting Smart Glasses Navigation Server...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        ws_ping_interval=20,
        ws_ping_timeout=20,
    )
