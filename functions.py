import classes
from datetime import datetime

def getChannelID(youtube_id):
	yt_obj = classes.Youtube(youtube_id)

	return yt_obj.info['channel_id']

def currentIncrement():
	# Get the current time
	current_time = datetime.now().time()

	current_minute = current_time.minute

	if current_minute == 0:
		current_minute = 60

	# Define the increments and their corresponding intervals
	increments = {
		1: 60,
		2: 30,
		3: 20,
		4: 15,
		6: 10,
		12: 5
	}

	# Find the current increment
	current_increment = None
	for increment, interval in increments.items():
		if current_minute % interval == 0:
			current_increment = increment
			break

	return current_increment

def calculate_aspect_ratio(width, height):
	# Calculate aspect ratio
	gcd_value = 1  # Initialize with 1 in case width and height are coprime
	for i in range(1, min(width, height) + 1):
		if width % i == 0 and height % i == 0:
			gcd_value = i

	aspect_ratio_width = width // gcd_value
	aspect_ratio_height = height // gcd_value

	aspect_ratio = f"{aspect_ratio_width}:{aspect_ratio_height}"\

	return aspect_ratio