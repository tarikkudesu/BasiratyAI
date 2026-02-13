import { StyleSheet, Text, View, TouchableOpacity } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';

const WelcomeScreen = ({ onStart, onRequestPermission, hasPermission }) => {
	if (!hasPermission) {
		return (
			<LinearGradient colors={['#6f0699', '#700491', '#4B0082']} style={styles.container}>
				<View style={styles.content}>
					<Text style={styles.title}>Camera Access Required</Text>
					<Text style={styles.description}>We need your permission to access the camera</Text>
					<TouchableOpacity style={styles.permissionButton} onPress={onRequestPermission}>
						<Text style={styles.buttonText}>Grant Permission</Text>
					</TouchableOpacity>
				</View>
			</LinearGradient>
		);
	}

	return (
		<TouchableOpacity style={styles.container} activeOpacity={0.9} onPress={onStart}>
			<LinearGradient colors={['#6f0699', '#4B0082']} style={styles.container}>
				<View style={styles.content}>
					<Text style={styles.title}>Welcome to BasiratyAI</Text>
					<Text style={styles.description}>Your intelligent AI companion for an enhanced lifestyle</Text>
					<Text style={styles.tapHint}>Tap to start</Text>
				</View>
			</LinearGradient>
		</TouchableOpacity>
	);
};

export default WelcomeScreen;

const styles = StyleSheet.create({
	container: {
		flex: 1,
		width: '100%',
		justifyContent: 'center',
		alignItems: 'center',
	},
	content: {
		alignItems: 'center',
		paddingHorizontal: 30,
		zIndex: 1,
		width: '100%',
	},
	title: {
		fontSize: 42,
		fontWeight: 'bold',
		color: '#FFFFFF',
		marginBottom: 20,
		textAlign: 'center',
	},
	description: {
		fontSize: 16,
		color: '#F0E6FF',
		textAlign: 'center',
		lineHeight: 24,
		marginBottom: 30,
	},
	tapHint: {
		fontSize: 14,
		color: '#FFFFFF',
		textAlign: 'center',
		marginTop: 20,
		opacity: 0.7,
		fontStyle: 'italic',
		width: '100%',
	},
	permissionButton: {
		backgroundColor: '#FF00FF',
		paddingHorizontal: 30,
		paddingVertical: 15,
		borderRadius: 25,
		marginTop: 20,
	},
	buttonText: {
		color: '#FFFFFF',
		fontSize: 16,
		fontWeight: 'bold',
	},
});
