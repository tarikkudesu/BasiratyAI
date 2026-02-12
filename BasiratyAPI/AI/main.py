"""
Smart Glasses Navigation Server
Real-Time Computer Vision System for the Blind
"""

import logging

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from core import load_path_model, get_path_model
from services import run_inference
from utils import bytes_to_image

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title="BasiratyAI Navigation API",
    description="Real-time path detection for visually impaired users",
    version="2.0.0",
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
    """Load path detection model at server startup"""
    try:
        load_path_model("./best.pt")
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
        }


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Smart Glasses Path Detection API",
        "status": "operational",
        "model": "Path Detection (best.pt)",
        "version": "2.0.0",
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    path_model = get_path_model()
    return {
        "status": "healthy",
        "path_model_loaded": path_model is not None,
        "model_path": "../../best.pt",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=7417,
        log_level="info",
        ws_ping_interval=20,
        ws_ping_timeout=20,
    )
