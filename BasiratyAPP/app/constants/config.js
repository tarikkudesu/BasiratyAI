export const API_BASE_URL = 'https://classical-jewish-levels-projector.trycloudflare.com';

export const CAMERA_CONFIG = {
	quality: 0.8,
	base64: false,
	skipProcessing: false,  // Process to apply correct rotation
	shutterSound: false,
	exif: true,  // Include EXIF data for orientation
};

// Maximum image dimension before sending to server (preserves aspect ratio)
export const IMAGE_MAX_SIZE = 800;

export const STATUS_COLORS = {
	STOP: '#ff4444',
	WARNING: '#ffaa00',
	CLEAR: '#44ff44',
};

export const SPEECH_CONFIG = {
	language: 'en',
};
