import { StyleSheet, View, Text } from 'react-native';
import { STATUS_COLORS } from '../constants/config';

const getStatusColor = (status) => {
	return STATUS_COLORS[status] || STATUS_COLORS.CLEAR;
};

const StatusCard = ({ status, feedback }) => {
	return (
		<View style={[styles.container, { backgroundColor: getStatusColor(status) }]}>
			<Text style={styles.statusText}>{status}</Text>
			<Text style={styles.feedbackText}>{feedback}</Text>
		</View>
	);
};

export default StatusCard;

const styles = StyleSheet.create({
	container: {
		position: 'absolute',
		top: 60,
		left: 20,
		right: 20,
		padding: 20,
		borderRadius: 10,
		alignItems: 'center',
	},
	statusText: {
		fontSize: 24,
		fontWeight: 'bold',
		color: '#FFFFFF',
		marginBottom: 10,
	},
	feedbackText: {
		fontSize: 16,
		color: '#FFFFFF',
		textAlign: 'center',
	},
});
