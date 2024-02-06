import mysql.connector
from yt_dlp import YoutubeDL
import re

class Youtube(object):
	"""docstring for Youtube"""
	def __init__(self, ytId):

		self.ytId = ytId
		
		''' General info gathering '''

		downloadDir = '/home/david/Downloads' #conf.configuration['general']['audio']['downloadDir']
		ydl_opts = {
			'outtmpl': downloadDir,
			'subtitleslangs': ['all', '-live_chat'],
			'writesubtitles': True,
			'embedsubtitles': True,
			'format': 'bestvideo+bestaudio[ext=m4a]/bestvideo+bestaudio',
			'quiet': True
		}

		with YoutubeDL(ydl_opts) as ydl:
			self.info = ydl.extract_info(f'https://www.youtube.com/watch?v={self.ytId}', download=False)

		''' Filename formatting '''

		# Lowercase all characters
		fileName = self.info['title'].lower()

		# Replace non-alphanumeric characters with underscores
		fileName = re.sub(r'[^a-zA-Z0-9\-]+', '_', fileName)

		# Remove any leading Underscores
		fileName = re.sub(r'^_+', '', fileName)

		# Remove any trailing Underscores
		fileName = fileName.rstrip('_')

		# Cut the resulting filename to a maximum length of 255 bytes
		fileName = fileName[:255]

		''' Defining basics '''

		self.info['fileName'] = f'{fileName}_{self.ytId}'

		self.info['videoRootPath'] = None #conf.configuration['general']['video']['downloadDir']
		self.info['fileFormatVideo'] = 'mp4'

		self.info['audioRootPath'] = None #conf.configuration['general']['audio']['downloadDir']
		self.info['fileFormatAudio'] = 'wav'

		self.info['imageRootPath'] = None #conf.configuration['general']['image']['downloadDir']

	def dlVideo(self):

		ydl_opts = {
			'outtmpl': f'{self.info["videoRootPath"]}/{self.info["fileName"]}',
			'format': f'bestvideo+bestaudio[ext={self.info["fileFormatAudio"]}]/bestvideo+bestaudio',
			'merge_output_format': self.info['fileFormatVideo']
		}

		with YoutubeDL(ydl_opts) as ydl:
			ydl.download([f'https://www.youtube.com/watch?v={self.ytId}'])

		return f"{self.info['videoRootPath']}/{self.info['fileName']}.{self.info['fileFormatVideo']}"

	def dlAudio(self):
		
		ydl_opts = {
			'outtmpl': f'{self.info["audioRootPath"]}/{self.info["fileName"]}',
			'format': f'bestaudio',
			'postprocessors': [{
				'key': 'FFmpegExtractAudio',
				'preferredcodec': self.info['fileFormatAudio'],
				'preferredquality': '0'
			}]
		}

		with YoutubeDL(ydl_opts) as ydl:
			ydl.download([f'https://www.youtube.com/watch?v={self.ytId}'])

		return f"{self.info['audioRootPath']}/{self.info['fileName']}.{self.info['fileFormatAudio']}"

	def dlImage(self):

		success = False
		tries = 0

		while not success:
			try:
				if tries == 3:
					break 
				urllib.request.urlretrieve(f'https://img.youtube.com/vi/{self.ytId}/maxresdefault.jpg', f'{self.info["imageRootPath"]}/{self.info["fileName"]}.jpg')	# Downloading the best img quality url
				success = True
			except Exception as e:
				tries += 1

		if success:
			return f'{self.info["imageRootPath"]}/{self.info["fileName"]}.jpg'

		tries = 0
		while not success:
			try:
				if tries == 5:
					raise Exception('Something went wrong trying to download the thumbnail') 
				urllib.request.urlretrieve(self.info['thumbnail'], f'{self.info["imageRootPath"]}/{self.info["fileName"]}.jpg')
				success = True
			except Exception as e:
				tries += 1

		return f'{self.info["imageRootPath"]}/{self.info["fileName"]}.jpg'

class MySQL(object):
	"""docstring for MySQL"""
	def __init__(self, database, db_user, db_user_password, host='localhost'):
		self.database = database
		
		self.mysqlInterface = mysql.connector.connect(
			database=self.database,
			user=db_user,
			password=db_user_password,
			host=host,
			converter_class=mysql.connector.conversion.MySQLConverter
		)

	def disconnect(self):
		self.mysqlInterface.disconnect()

	def run(self, statement):
		if not self.mysqlInterface.is_connected():
			self.mysqlInterface.reconnect()

		# Fix INSERT None to NULL translation
		if statement.upper().startswith('INSERT'):

			statement = re.sub(r'\(None\b', '(NULL', statement) # Replace with null value if begins with
			statement = re.sub(r',\s*None\b', ', NULL', statement) # Replace with null value if anywhere else

		with self.mysqlInterface.cursor(buffered=True) as cursor:
			cursor.execute(statement)

			try:
				return cursor.fetchall()

			except:
				self.mysqlInterface.commit()
				return None