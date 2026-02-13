import { useState, useRef, useCallback } from 'react';
import * as Speech from 'expo-speech';
import { sendFrameToServer } from '../services/api';
import { CAMERA_CONFIG, SPEECH_CONFIG } from '../constants/config';

export const useFrameCapture = () => {
	const [status, setStatus] = useState('CLEAR');
	const [feedback, setFeedback] = useState('Initializing...');
	const isCapturingRef = useRef(false);

	const captureAndSendFrame = useCallback(async (cameraRef) => {
		if (!cameraRef?.current || isCapturingRef.current) {
			return;
		}

		console.log('Screen Pressed');
		isCapturingRef.current = true;

		try {
			const photo = await cameraRef.current.takePictureAsync(CAMERA_CONFIG);
			if (photo.uri) {
				const data = await sendFrameToServer(photo.uri);
				// setStatus(data.status);
				console.log(data);
				// setFeedback(data.voice_feedback);
				// Speech.speak(data.voice_feedback, SPEECH_CONFIG);
			}
		} catch (error) {
			console.error('Frame capture error:', error);
			setFeedback('Connection error');
		} finally {
			isCapturingRef.current = false;
		}
	}, []);

	const resetFeedback = useCallback(() => {
		setFeedback('Camera ready');
	}, []);

	return {
		status,
		feedback,
		captureAndSendFrame,
		resetFeedback,
	};
};
