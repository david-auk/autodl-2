import secret
import classes
import functions
from datetime import datetime, timezone
import scrapetube
import os

current_increment = functions.currentIncrement()

db = classes.MySQL(secret.mysql['database'], secret.mysql['user'], secret.mysql['password'])

if current_increment:
	increment_statement = f'SELECT id, title, req_user_id FROM yt_channel WHERE pulling_increment >= {current_increment} AND is_pulling = 1'
else:
	increment_statement = 'SELECT id, title, req_user_id FROM yt_channel WHERE is_pulling = 1'

for channel_id, channel_title, content_requester in db.run(increment_statement): # For each account where i should pull

	videos = scrapetube.get_channel(channel_id)

	for video in videos:
		if not db.run(f'SELECT * FROM yt_content WHERE id = "{video["videoId"]}"'): # If the video is not in the database (yet..)
			
			video_obj = classes.Youtube(video["videoId"], video_dir=secret.configuration['video_dir'], audio_dir=secret.configuration['audio_dir'], thumbnail_dir=secret.configuration['thumbnail_dir'], subtitle_dir=secret.configuration['subtitle_dir'])

			# Downloading the video:
			video_path = video_obj.dlVideo()

			# Downloading the audio:
			audio_path = video_obj.dlAudio()			

			# Downloading subtitles, if avalible:
			subtitle_path = video_obj.dlSubtitles()

			data = (
				video_obj.info["id"],
				video_obj.info["title"],
				video_obj.info['description'],
				channel_id,
				content_requester,
				#'auto',
				#0, # Refine 'latest_pull'
				datetime.strptime(video_obj.info["upload_date"], "%Y%m%d").strftime("%Y-%m-%d %H:%M:%S"),
				datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
				video_path,
				audio_path,
				subtitle_path,
				os.path.getsize(video_path),
				video_obj.info['duration'],
				video_obj.info['width'],
				video_obj.info['height']
			)

			db.run(f"INSERT INTO yt_content(id, title, description, channel_id, req_user_id, upload_date, download_date, video_path, audio_path, subtitle_path, video_size, duration, image_height, image_width) VALUES {data}")