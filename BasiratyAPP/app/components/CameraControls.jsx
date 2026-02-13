import { StyleSheet, View, TouchableOpacity, Text } from 'react-native';

const CameraControls = ({ onFlipCamera, onCloseCamera }) => {
	return (
		<View style={styles.container}>
			<TouchableOpacity style={styles.button} onPress={onFlipCamera}>
				<Text style={styles.buttonText}>Flip Camera</Text>
			</TouchableOpacity>
			<TouchableOpacity style={styles.button} onPress={onCloseCamera}>
				<Text style={styles.buttonText}>Close Camera</Text>
			</TouchableOpacity>
		</View>
	);
};

export default CameraControls;

const styles = StyleSheet.create({
	container: {
		position: 'absolute',
		bottom: 0,
		left: 0,
		right: 0,
		flexDirection: 'row',
		justifyContent: 'space-around',
		paddingBottom: 40,
		paddingHorizontal: 20,
	},
	button: {
		backgroundColor: 'rgba(209, 57, 255, 0.8)',
		paddingHorizontal: 20,
		paddingVertical: 10,
		borderRadius: 20,
	},
	buttonText: {
		color: '#FFFFFF',
		fontSize: 16,
		fontWeight: 'bold',
	},
});
