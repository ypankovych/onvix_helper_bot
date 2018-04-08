import os
import utils
import telebot
from fsm import FSM

bot = telebot.TeleBot(os.environ.get('token'))
fsm_obj = FSM('old_account')


@bot.message_handler(commands=['start'])
def start(message):
	fsm_obj.init_state(message.chat.id)
	bot.send_message(message.chat.id, 'Send data from your old account in this format:\nemail@gmail.com password')


@bot.message_handler(func=lambda m: fsm_obj.get_state(m.chat.id) == 'old_account')
def collect_favorites(message):
	login_data = message.text.split()
	if len(login_data) == 2:
		user = utils.login(*login_data)
		if user:
			movies = utils.get_favorites(user['session'])
			fsm_obj.add_extra_state(message.chat.id, 'movies', movies)
			fsm_obj.set_state(message.chat.id, 'new_account')
			bot.send_message(message.chat.id, f'{len(movies)} movies collected')
			bot.send_message(message.chat.id, 'Send data from your new account in same format:')
		else:
			wrong_password(message)
	else:
		invalid_format(message)


@bot.message_handler(func=lambda m: fsm_obj.get_state(m.chat.id) == 'new_account')
def addition(message):
	login_data = message.text.split()
	if len(login_data) == 2:
		user = utils.login(*login_data)
		if user:
			bot.send_message(message.chat.id, 'It may take a few minutes.')
			utils.process(user, fsm_obj.get_extra_state(message.chat.id, 'movies'))
			fsm_obj.remove_extra_state(message.chat.id)
			fsm_obj.remove_state(message.chat.id)
			bot.send_message(message.chat.id, 'Done. /start')
		else:
			wrong_password(message)
	else:
		invalid_format(message)


def wrong_password(message):
	bot.send_message(message.chat.id, 'Wrong login or password, try again:')


def invalid_format(message):
	bot.send_message(message.chat.id, 'Invalid format, try again:')

if __name__ == '__main__':
	bot.polling(none_stop=True, timeout=10000*5)
