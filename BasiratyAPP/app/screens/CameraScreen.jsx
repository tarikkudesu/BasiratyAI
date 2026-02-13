import { StyleSheet, View, Pressable } from 'react-native';
import { CameraView } from 'expo-camera';
import { useState, useRef, useEffect } from 'react';
import Canvas from 'react-native-canvas';
import StatusCard from '../components/StatusCard';
import CameraControls from '../components/CameraControls';
import { useFrameCapture } from '../hooks/useFrameCapture';

const CameraScreen = ({ onClose }) => {
	const [facing, setFacing] = useState('back');
	const cameraRef = useRef(null);
	const canvasRef = useRef(null);
	const intervalRef = useRef(null);

	const { status, feedback, captureAndSendFrame, resetFeedback } = useFrameCapture();

	useEffect(() => {
		resetFeedback();
		startFrameCapture();

		return () => {
			if (intervalRef.current) {
				clearInterval(intervalRef.current);
			}
		};
	}, [resetFeedback]);

	const startFrameCapture = () => {
		// Uncomment to enable automatic frame capture every 5 seconds
		// intervalRef.current = setInterval(() => {
		// 	captureAndSendFrame(cameraRef);
		// }, 5000);
	};

	const handleFlipCamera = () => {
		setFacing((current) => (current === 'back' ? 'front' : 'back'));
	};

	const handleCloseCamera = () => {
		if (intervalRef.current) {
			clearInterval(intervalRef.current);
		}
		onClose();
	};

	const handleScreenTap = () => {
		captureAndSendFrame(cameraRef);
	};

	return (
		<View style={styles.container}>
			<Pressable style={styles.cameraContainer} onPress={handleScreenTap}>
				<CameraView ref={cameraRef} style={styles.camera} facing={facing} />
				<Canvas ref={canvasRef} style={styles.canvas} />
			</Pressable>
			<StatusCard status={status} feedback={feedback} />
			<CameraControls onFlipCamera={handleFlipCamera} onCloseCamera={handleCloseCamera} />
		</View>
	);
};

export default CameraScreen;

const styles = StyleSheet.create({
	container: {
		flex: 1,
		width: '100%',
	},
	cameraContainer: {
		flex: 1,
	},
	camera: {
		flex: 1,
	},
	canvas: {
		position: 'absolute',
		top: 0,
		left: 0,
		width: '100%',
		height: '100%',
		opacity: 0.5,
		pointerEvents: 'none',
	},
});
