import secret
import classes
import functions
from datetime import datetime, timezone
import scrapetube

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
			
			video_obj = classes.Youtube(video["videoId"])

			data = (
				video_obj.info["id"],
				video_obj.info["title"],
				channel_id,
				content_requester,
				'Auto',
				0, # Refine 'latest_pull'
				datetime.strptime(video_obj.info["upload_date"], "%Y%m%d").strftime("%Y-%m-%d %H:%M:%S"),
				datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
				None,
				'/home/test/te.txt',
				'/home/test/te.mp4',
				'/home/test/te.mp3',
				0, # Refine 'size'
				video_obj.info['duration'],
				video_obj.info['width'],
				video_obj.info['height']
			)

			db.run(f"INSERT INTO yt_content VALUES {data}")

			print('+1')