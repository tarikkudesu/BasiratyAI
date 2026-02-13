import { StyleSheet, View } from 'react-native';
import { useCameraPermissions } from 'expo-camera';
import { useState } from 'react';
import WelcomeScreen from './screens/WelcomeScreen';
import CameraScreen from './screens/CameraScreen';

const Home = () => {
	const [permission, requestPermission] = useCameraPermissions();
	const [showCamera, setShowCamera] = useState(false);

	if (!permission) {
		return <View style={styles.container} />;
	}

	if (!showCamera || !permission.granted) {
		return (
			<WelcomeScreen hasPermission={permission.granted} onStart={() => setShowCamera(true)} onRequestPermission={requestPermission} />
		);
	}

	return <CameraScreen onClose={() => setShowCamera(false)} />;
};

export default Home;

const styles = StyleSheet.create({
	container: {
		flex: 1,
		width: '100%',
		justifyContent: 'center',
		alignItems: 'center',
	},
});
