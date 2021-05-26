from os import path
import telebot, config, markup, calendar, database, module, strings, requests, sys, logging, eventlet, json, time, os
from telebot.types import LabeledPrice, ShippingOption
from threading import Thread, Lock, Timer
from flask import Flask, render_template, request, Response, abort, jsonify
from flask_socketio import SocketIO, disconnect
from datetime import datetime
from telebot import types
bot = telebot.TeleBot(config.token)
root = path.dirname(path.abspath(__file__)) + '/'



logging.basicConfig(format='%(asctime)s (%(filename)s:%(lineno)d) %(levelname)s:%(name)s:"%(message)s"',
					datefmt="%Y-%m-%d %H:%M:%S")

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
app = Flask(__name__)
socketio = SocketIO(app, async_mode='eventlet', logger=False, engineio_logger=False)
admins = [7480922, 1087731479]

@bot.message_handler(commands=['broadcast'])
def broadcast_handler(message):
	if message.from_user.id in admins and message.reply_to_message:
		bot.send_message(message.chat.id, 'Рассылка запущена.')
		broadcast_made(message.from_user.id, message.reply_to_message.message_id)


def broadcast_made(chat_id, message_id):
	for m in database.get_info(config.users):
		try:
			bot.forward_message(m['user_id'], chat_id, message_id)
			time.sleep(5)
		except Exception as e:
			bot.send_message(chat_id, str(e))


@bot.message_handler(commands=['start'])
def start_handler(message):
	if not module.check_in_mongo(config.users, {'user_id' : message.from_user.id}):
		database.insert_into(config.users, module.new_user(message))
	user_info = database.get_info(config.users, {'user_id' : message.from_user.id})[0]
	lang = user_info['lang']
	database.update_info(config.users, {'user_id' : message.from_user.id}, {'where' : None})
	bot.send_message(message.chat.id, strings.text[lang]['message']['welcome'], reply_markup=markup.main_menu(lang))

@bot.message_handler(content_types=['text'])
def text_handler(message):
	user_info = database.get_info(config.users, {'user_id' : message.from_user.id})[0]
	lang = user_info['lang']
	where = user_info['where']
	if message.text == strings.text[lang]['buttons']['order']:
		bot.send_message(message.chat.id, strings.text[lang]['message']['select']['room'], reply_markup=markup.room_menu(lang))
	elif message.forward_from_chat:
		if message.forward_from_chat.id == config.channel_id:
			reserve_info = database.get_info(config.orders, {'message_id' : message.forward_from_message_id})[0]
			for m in reserve_info['reserved']:
				database.update_info(config.times, {'code' : m}, {'active' : True})
				database.update_info(config.times, {'code' : int(m)}, {'active' : True})
			bot.send_message(config.channel_id, 'Бронь отменен', reply_to_message_id=reserve_info['message_id'])
			bot.send_message(message.chat.id, '✅')
	elif message.text == strings.text[lang]['buttons']['see_loft']:
		bot.send_media_group(message.chat.id, [types.InputMediaPhoto('https://telegra.ph/file/a9858237cacab82df3bc3.jpg'), types.InputMediaPhoto('https://telegra.ph/file/01c0f4fdbb57f95b8f166.jpg'), types.InputMediaPhoto('https://telegra.ph/file/62d152de66b469e644a74.jpg'), types.InputMediaPhoto('https://telegra.ph/file/216ce41ada2276efe29b3.jpg'), types.InputMediaPhoto('https://telegra.ph/file/c9d667c7a9ee69cf8fc3c.jpg')])
	elif message.text == strings.text[lang]['buttons']['see_white']:
		bot.send_media_group(message.chat.id, [types.InputMediaPhoto('https://telegra.ph/file/0c99b6b4fa0292bdbafec.jpg'), types.InputMediaPhoto('https://telegra.ph/file/dab304b17095446ae1a99.jpg'), types.InputMediaPhoto('https://telegra.ph/file/e78f1ff277022020a3ff5.jpg'), types.InputMediaPhoto('https://telegra.ph/file/2318e2ec97181306eb7ce.jpg'), types.InputMediaPhoto('https://telegra.ph/file/66d57e663be1951e71454.jpg')])
	elif message.text == strings.text[lang]['buttons']['info']:
		bot.send_message(message.chat.id, strings.text[lang]['message']['info'])
		bot.send_photo(message.chat.id, "https://telegra.ph/file/01febaff80f89f6b48d07.jpg")
	elif message.text == strings.text[lang]['buttons']['price_rules']:
		bot.send_media_group(1087731479, [types.InputMediaPhoto('https://telegra.ph/file/dfc175a1b79d3a58ba24c.jpg', caption='''Уважаемые и любимые посетители студии «Poligon», просим вас внимательно ознакомиться с обновлённым прайсом, который вступает в силу с 1.11.2020 года, а так же с правилами пребывания в нашей студии📷\n\nС уважением, администрация студии “Poligon”'''),types.InputMediaPhoto('https://telegra.ph/file/294dad25fca7d3530cc70.jpg'),types.InputMediaPhoto('https://telegra.ph/file/01febaff80f89f6b48d07.jpg')])
	elif message.text == strings.text[lang]['buttons']['geo']:
		bot.send_message(message.chat.id, strings.text[lang]['message']['geo'])
		bot.send_location(message.chat.id, 41.30473, 69.282675)
	elif where:
		if where[:4] == 'send':
			if where[5:] == 'payment':
				if message.text in strings.text[lang]['buttons']['payments']:
					reserve_code = module.make_code(1, 8)[0]
					database.update_info(config.users, {'user_id' : message.from_user.id}, {'where' : None, 'payment' : message.text})
					bot.send_message(message.chat.id, strings.text[lang]['message']['sended'], reply_markup=markup.main_menu(lang))
					msg = bot.send_message(config.channel_id, module.get_order_text(message.from_user.id), reply_markup=markup.admin_menu(config.main_lang, reserve_code), parse_mode='html')
					database.insert_into(config.orders, {'code' : reserve_code, 'user_id' : message.from_user.id,  'people' : user_info['people'], 'message_id' : msg.message_id, 'reserved' : user_info['reserved']})
					for m in user_info['reserved']:
						database.update_info(config.times, {'code' : m}, {'active' : False})
						database.update_info(config.times, {'code' : int(m)}, {'active' : False})
			elif where[5:] == 'phone':
				database.update_info(config.users, {'user_id' : message.from_user.id}, {'where' : 'send:payment', 'phone' : message.text})
				bot.send_message(message.chat.id, strings.text[lang]['message']['send']['payment'], reply_markup=markup.payment_menu(lang))
				
@bot.message_handler(content_types=['contact'])
def contact_handler(message):
	user_info = database.get_info(config.users, {'user_id' : message.from_user.id})[0]
	lang = user_info['lang']
	where = user_info['where']
	if where:
		if where[:4] == 'send':
			if where[5:] == 'phone':
				database.update_info(config.users, {'user_id' : message.from_user.id}, {'where' : 'send:payment', 'phone' : message.contact.phone_number})
				bot.send_message(message.chat.id, strings.text[lang]['message']['send']['payment'], reply_markup=markup.payment_menu(lang))


@bot.callback_query_handler(func=lambda call:True)
def call_handler(call):
	user_info = database.get_info(config.users, {'user_id' : call.from_user.id})[0]
	lang = user_info['lang']
	if call.data[:4] == 'room':
		database.update_info(config.users, {'user_id' : call.from_user.id}, {'room' : int(call.data[5:])})
		bot.edit_message_text(strings.text[lang]['message']['select']['month'], call.message.chat.id, call.message.message_id, reply_markup=markup.month_menu(lang, call.data[5:]))
	elif call.data[:5] == 'month':
		database.update_info(config.users, {'user_id' : call.from_user.id}, {'month' : int(call.data[6:].split('.')[0]), 'year' : int(call.data[6:].split('.')[1])})
		bot.edit_message_text(strings.text[lang]['message']['select']['day'], call.message.chat.id, call.message.message_id, reply_markup=markup.day_menu(lang, call.data[6:], user_info['room']))
	elif call.data == 'time':
		# database.update_info(config.users, {'user_id' : call.from_user.id}, {'where' : 'send:phone'})
		# bot.delete_message(call.message.chat.id, call.message.message_id)
		# bot.send_message(call.message.chat.id, strings.text[lang]['message']['send']['phone'], reply_markup=markup.phone_menu(lang))
		bot.edit_message_text(strings.text[lang]['message']['select']['people'], call.message.chat.id, call.message.message_id, reply_markup=markup.people_menu(lang))
	elif call.data[:6] == 'people':
		database.update_info(config.users, {'user_id' : call.from_user.id}, {'where' : 'send:phone', 'people' : int(call.data[7:])})
		bot.delete_message(call.message.chat.id, call.message.message_id)
		bot.send_message(call.message.chat.id, strings.text[lang]['message']['send']['phone'], reply_markup=markup.phone_menu(lang))

	elif call.data[:4] == 'time':
		if call.data[5:] not in user_info['reserved']:
			user_info['reserved'].append(call.data[5:])
		else:
			user_info['reserved'].remove(call.data[5:])
		database.update_info(config.users, {'user_id' : call.from_user.id},  {'reserved' : user_info['reserved']})
		bot.edit_message_text(strings.text[lang]['message']['select']['time'], call.message.chat.id, call.message.message_id, reply_markup=markup.time_menu(lang, user_info['day'], user_info['room'], user_info['reserved']))
	elif call.data[:3] == 'day':
		try:
			date = int(module.date_to_secs(*list(map(int, module.get_datetime('20{}.{}'.format(user_info['year'], user_info['month'])).split('.'))), database.get_info(config.days, {'code' : int(call.data[4:])})[0]['day'], 00, 00))
		except:
			date = int(module.date_to_secs(*list(map(int, module.get_datetime('20{}.{}'.format(user_info['year'], user_info['month'])).split('.'))), database.get_info(config.days, {'code' : str(call.data[4:])})[0]['day'], 00, 00))

		database.update_info(config.users, {'user_id' : call.from_user.id}, {'date' : date, 'day' : call.data[4:], 'reserved' : []})
		bot.edit_message_text(strings.text[lang]['message']['select']['time'], call.message.chat.id, call.message.message_id, reply_markup=markup.time_menu(lang, call.data[4:], user_info['room'], []))
	elif call.data[:4] == 'back':
		if call.data[5:] == 'room':
			bot.edit_message_text(strings.text[lang]['message']['select']['room'], call.message.chat.id, call.message.message_id, reply_markup=markup.room_menu(lang))
		elif call.data[5:] == 'month':
			bot.edit_message_text(strings.text[lang]['message']['select']['month'], call.message.chat.id, call.message.message_id, reply_markup=markup.month_menu(lang, user_info['room']))
		elif call.data[5:] == 'day':
			bot.edit_message_text(strings.text[lang]['message']['select']['day'], call.message.chat.id, call.message.message_id, reply_markup=markup.day_menu(lang, str(user_info['month'])+'.'+str(user_info['year']), user_info['room']))

	elif call.data[:2] == 'ok':
		order_info = database.get_info(config.orders, {'message_id' : call.message.message_id})[0]
		if 'PayMe' in call.message.text:
			bot.send_invoice(order_info['user_id'], title='Оплата Poligon Studio',
						description='Мы успешно обработали вашу заявку, пожалуйста оплатите счет',
						provider_token=config.provider_tokens['payme'],
						currency='UZS',
						photo_url='https://telegra.ph/file/28afa71035bba73290172.jpg',
						photo_height=512,  # !=0/None or picture won't be shown
						photo_width=512,
						photo_size=512,
						is_flexible=False,  # True If you need to set up Shipping Fee
						prices=[LabeledPrice(label='Оплата Poligon Studio', amount=strings.text['ru']['message']['prices'][order_info['people']]*len(order_info['reserved']))],
						start_parameter='test-id-for-you',
						invoice_payload=call.message.message_id)
		bot.edit_message_text(call.message.text+'\nПринял: <a href=\"tg://user?id={}\">{}</a>'.format(call.from_user.id, call.from_user.first_name), call.message.chat.id, call.message.message_id, parse_mode='html')
		bot.send_media_group(order_info['user_id'], [types.InputMediaPhoto('https://telegra.ph/file/d088c723ee3460261cf1e.jpg', caption='''Ваша заявка принята)) 
Пожалуйста ознакомьтесь с правилами пребывания и оплаты в нашей студии ) 
Спасибо за ваш выбор😊'''), types.InputMediaPhoto('https://telegra.ph/file/ff915573e8fdc054e1819.jpg')])
	elif call.data[:2] == 'no':
		reserve_info = database.get_info(config.orders, {'code' : call.data[3:]})[0]
		for m in reserve_info['reserved']:
			database.update_info(config.times, {'code' : m}, {'active' : True})
			database.update_info(config.times, {'code' : int(m)}, {'active' : True})
		bot.edit_message_text(call.message.text+'\nОтменил: <a href=\"tg://user?id={}\">{}</a>'.format(call.from_user.id, call.from_user.first_name), call.message.chat.id, call.message.message_id, parse_mode='html')


@bot.shipping_query_handler(func=lambda query: True)
def shipping(shipping_query):
	bot.answer_shipping_query(shipping_query.id, ok=True, shipping_options=[])

@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
	bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
	bot.send_message(config.channel_id, "Успешно оплачен", reply_to_message_id = int(message.successful_payment.invoice_payload))
	bot.send_message(message.chat.id, 'Ваш заказ успешно оплачен')



@app.route('/', methods=['POST'])
def web_hook():
	if request.headers.get('content-type') == 'application/json':
		data = request.get_data().decode("utf-8")
		update = telebot.types.Update.de_json(data)
		if update.message:
			bot.process_new_messages([update.message])
		if update.callback_query:
			bot.process_new_callback_query([update.callback_query])
		if update.inline_query:
			bot.process_new_inline_query([update.inline_query])
		if update.pre_checkout_query:
			bot.process_new_pre_checkout_query([update.pre_checkout_query])
		return ''
	abort(403)

def bot_polling():
	bot.remove_webhook()
	bot.polling(True)




def main(argv):
	if config.polling:
		logger.info('starting polling...')
		thread = Thread(target=bot_polling)
		thread.start()
	else:
		logging.info('setting webhook...')
		bot.remove_webhook()
		bot.set_webhook(config.webhook)
	me = bot.get_me()
	logger.info('Me: %s @%s', me.first_name, me.username)
	# init_commands()
	socketio.run(app, host=config.host, port=config.port, use_reloader=False,
				 debug=False)


if __name__ == '__main__':
	main(sys.argv[1:])