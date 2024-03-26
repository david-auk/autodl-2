import classes
import functions
import secret
import logging
import time
from datetime import datetime, timezone
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, ChatAction

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)
logger = logging.getLogger(__name__)

#tgUserDb = classes.Database(filename='/opt/minecraft/tools/python/telegramData.csv', index=('chatId', 'firstName', 'userName', 'role', 'authenticated'), primaryKey='chatId')
db = classes.MySQL(secret.mysql['database'], secret.mysql['user'], secret.mysql['password'])

# Define password variable
user_password = secret.telegram['user_password']

def userInnit(chat_id, username, first_name, last_name):

	if db.run(f'SELECT id FROM tg_user WHERE id = {chat_id}'): # If  user is registerd
		
		# Check if the user info changed
		db_values = db.run(f'SELECT username, first_name, last_name FROM tg_user WHERE id = {chat_id}')[0]

		if not (username, first_name, last_name) == db_values:	
			# Updating the data in the db
			db.run(f'UPDATE tg_user SET username = "{username}", first_name = "{first_name}", last_name = "{last_name}" WHERE id = {chat_id}')
	
	else:
		# Registering the user to the db
		data = (chat_id, username, first_name, last_name, 'subscriber', None, 0, datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"))
		db.run(f"INSERT INTO tg_user VALUES {data}")

# Define handlers for each command
def start(update, context):
	"""Send a message when the command /start is issued."""
	update.message.reply_text('Welcome to the *Telegram Command Interface*\n\nAuthenticate: /passwd\nUse: /help', parse_mode='MarkdownV2')
	user = update.message.from_user

	userInnit(user.id, user.username, user.first_name, user.last_name)

def helpMenu(update, context):
	"""Send a message when the command /help is issued."""
	update.message.reply_text('The following commands are available:\n\n'
							  'Aurhorise using: /passwd\n\n'
							  'Send me a link!\n'
							  'I\'ll download the link or add a channel to backup\n\n'
							  'View the latest videos with: /latest \n'
							  '/info - Get info about a link\n'
							  '/send VIDID to view the content')

def check_password(update, context):
	"""Check the user's password."""
	# Get the chat ID
	chat_id = update.message.chat_id
	userMessageId = update.message.message_id

	#if db.run(f'SELECT is_authenticated FROM tg_user WHERE id = {chat_id}')

	login_attempts = db.run(f'SELECT COUNT(*) FROM tg_login_attempt GROUP BY tg_user_id HAVING tg_user_id = {chat_id}')
	if login_attempts:
		login_attempts = login_attempts[0][0]
	else:
		login_attempts = 0


	if login_attempts >= secret.telegram['max_tries']:
		
		message = context.bot.send_message(chat_id=chat_id, text="Max login login attempts reached..")
		context.bot.delete_message(chat_id=chat_id, message_id=userMessageId, timeout=2000.0)
		context.bot.delete_message(chat_id=chat_id, message_id=message.message_id, timeout=2000.0)
	
	else:

		if db.run(f'SELECT is_authenticated FROM tg_user WHERE id = {chat_id}')[0][0]:
			message = context.bot.send_message(chat_id=chat_id, text="Already authorized ✅")

			context.bot.delete_message(chat_id=chat_id, message_id=userMessageId, timeout=1500.0)
			context.bot.delete_message(chat_id=chat_id, message_id=message.message_id, timeout=1500.0)
		else:
			# Send a message to the user asking for their password
			message = context.bot.send_message(chat_id=chat_id, text="Please enter your password:")

			# Set the next handler to wait for the user's password
			context.user_data["passwdinfo"] = {'user_message_id': f'{userMessageId}', 'bot_message_id': f'{message.message_id}'}
			context.user_data["next_handler"] = "check_password"

def startServer(update, context):
	pass

def statusServer(update, context):
	pass

def msgHandler(update, context):
	"""Handle links sent by the user."""
	# Get the message text and chat ID
	message_text = update.message.text
	userMessageId = update.message.message_id
	chat_id = update.message.chat_id

	# Check if the user's input is the correct password (if the previous handler was check_password)
	if context.user_data.get("next_handler") == "check_password":
		passwdInfo = context.user_data.get("passwdinfo")
		initialUserMessageId = passwdInfo['user_message_id']
		initialBotRespondMessageId = passwdInfo['bot_message_id']
		passwordMessageId = userMessageId
		if message_text == user_password:
			message = context.bot.send_message(chat_id=chat_id, text="Correct password ✅")
			finalBotResponceMessageId = message.message_id

			data = (chat_id, 1, datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"))
			db.run(f'INSERT INTO tg_login_attempt (tg_user_id, is_correct, date) VALUES {data}')
			db.run(f'UPDATE tg_user SET is_authenticated = 1 WHERE id = {chat_id}')
			#functions.msgHost(f"The user {name} just got added to the Database", False)

			#time.sleep(1.5)
			context.bot.delete_message(chat_id=chat_id, message_id=initialUserMessageId, timeout=1500)
			context.bot.delete_message(chat_id=chat_id, message_id=initialBotRespondMessageId, timeout=1500)
			context.bot.delete_message(chat_id=chat_id, message_id=passwordMessageId, timeout=1500)
			#time.sleep(1.5)
			context.bot.delete_message(chat_id=chat_id, message_id=finalBotResponceMessageId, timeout=3000)
		else:
			message = context.bot.send_message(chat_id=chat_id, text="Sorry, that's not the correct password.")
			
			data = (chat_id, 0, datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"))
			db.run(f'INSERT INTO tg_login_attempt (tg_user_id, is_correct, date) VALUES {data}')

			finalBotResponceMessageId = message.message_id
			time.sleep(1.5)
			context.bot.delete_message(chat_id=chat_id, message_id=initialUserMessageId)
			context.bot.delete_message(chat_id=chat_id, message_id=initialBotRespondMessageId)
			context.bot.delete_message(chat_id=chat_id, message_id=passwordMessageId)
			context.bot.delete_message(chat_id=chat_id, message_id=finalBotResponceMessageId)

		context.user_data["next_handler"] = ""

def error(update, context):
	"""Echo the user message."""
	update.message.reply_text(f"Unknown command: {update.message.text}")

def main():
	# Set up the Telegram bot
	updater = Updater(secret.telegram['token'], use_context=True)

	# Get the dispatcher to register handlers
	dp = updater.dispatcher

	# Add handlers for different commands
	dp.add_handler(CommandHandler("start", start))
	dp.add_handler(CommandHandler("start_server", startServer))
	dp.add_handler(CommandHandler("help", helpMenu))
	dp.add_handler(CommandHandler("passwd", check_password))
	dp.add_handler(MessageHandler(Filters.text & (~Filters.command), msgHandler))
	dp.add_handler(MessageHandler(Filters.text & Filters.command, error))

	# Start the bot
	updater.start_polling()

	# Run the bot until you press Ctrl-C or the process is stopped
	updater.idle()

if __name__ == '__main__':
	main()