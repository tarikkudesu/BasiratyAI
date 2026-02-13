import * as ImageManipulator from 'expo-image-manipulator';
import { API_BASE_URL, IMAGE_MAX_SIZE } from '../constants/config';

/**
 * Resize image while preserving aspect ratio before sending to server.
 * This reduces upload time and server processing load.
 */
const resizeImage = async (uri) => {
	try {
		const result = await ImageManipulator.manipulateAsync(
			uri,
			[{ resize: { width: IMAGE_MAX_SIZE } }],
			{ compress: 0.8, format: ImageManipulator.SaveFormat.JPEG }
		);
		return result.uri;
	} catch (error) {
		console.warn('Image resize failed, using original:', error);
		return uri;
	}
};

export const sendFrameToServer = async (fileUri) => {
	// Resize image before sending (preserves aspect ratio)
	const resizedUri = await resizeImage(fileUri);
	
	const formData = new FormData();

	// Create a file object from the URI for form-data
	formData.append('file', {
		uri: resizedUri,
		type: 'image/jpeg',
		name: 'frame.jpg',
	});
	console.log(`${API_BASE_URL}/navigate`);
	console.log("fetching");
	const response = await fetch(`${API_BASE_URL}/navigate`, {
		method: 'POST',
		body: formData,
	});
	console.log("fetching ended");

	if (!response.ok) {
		const errorText = await response.text();
		console.error('API Response:', errorText);
		throw new Error(`API error: ${response.status}`);
	}

	return response.json();
};
