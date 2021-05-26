import database, time, config, random, strings, os, pytz, telebot, requests
import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile
from os import path
from geopy.distance import geodesic
from datetime import datetime
from threading import Thread, Lock, Timer
bot = telebot.TeleBot(config.token)
root = path.dirname(path.abspath(__file__)) + '/'
os.environ['TZ']  = 'Asia/Tashkent'
time.tzset()


def get_datetime(value, secs=False):
    if secs:
        return datetime.fromtimestamp(secs).strftime(value)
    return datetime.now(pytz.timezone('Asia/Tashkent')).strftime(value)

def date_to_secs(year, month, day, hour, mins):
    return time.mktime(datetime(year, month, day, hour, mins).timetuple())

def get_order_text(user_id):
    user_info = database.get_info(config.users, {'user_id' : user_id})[0]
    times = []
    for m in user_info['reserved']:
        try:
            times.append(
                database.get_info(config.times, {'code' : m})[0]['name']
            )
        except:
            times.append(
                database.get_info(config.times, {'code' : int(m)})[0]['name']
            )
            
    return strings.text[user_info['lang']]['message']['new_order'].format(
        strings.text[user_info['lang']]['buttons']['rooms'][user_info['room']], get_datetime('%d.%m.%Y', user_info['date']), ', '.join(times), user_info['phone'], user_id, user_info['user']['name'], user_info['payment'], strings.text['ru']['message']['peoples'][user_info['people']],
    )

def generate_password(m):
    pass1 = 'ABCDEFGHJKLMNPQRSTUVWXYZ'
    pass2 = 'abcdefghijkmnpqrstuvwxyz'
    pass3 = '23456789'
    pass4 = ''
    pass5 = [1,2,3]
    pass6 = 'abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789'
    for i in range(3):
        v = random.choice(pass5)
        if v == 1:
            pass4 += random.choice(pass1)
        elif v == 2:
            pass4 += random.choice(pass2)
        else:   
            pass4 += random.choice(pass3)
        if i == 0:
            if v == 1:
                pass5.remove(1)
            if v == 2:
                pass5.remove(2)
            if v == 3:
                pass5.remove(3)
        elif i == 1:
            if 3 in pass5:
                if 2 in pass5:
                    if v == 2:
                        pass5.remove(2)
                    else:
                        pass5.remove(3)
                else:
                    if v == 1:
                        pass5.remove(1)
                    else:
                        pass5.remove(3)
            else:
                if v == 1:
                    pass5.remove(1)
                else:
                    pass5.remove(2)
    for i in range(m-3):
        pass7 = random.choice(pass6)
        pass4 += pass7
    return pass4

    
def generate_code(connector, checker, length, check_lower=False):
	code = make_code(1, length)[0]
	if check_lower:
		if not(check_in_mongo(connector, {checker : code.lower()})):
			return code
	else:
		if not(check_in_mongo(connector, {checker : code})):
			return code
	generate_code(connector, checker, length, check_lower)

def make_code(n, m):
    pass8 = []
    for i in range(n):
        q = generate_password(m)
        while q in pass8:
            q = generate_password(m)
        pass8.append(q)
    return pass8 


# def deliveryPrice(location):
#     km = round(geodesic((41.263506, 69.228728), location).km)+1
#     km2 = round(geodesic((41.232527, 69.366414), location).km)
#     if km2 <= 3:
#         km+=5
#     if km<=3:
#         return 0
#     elif km>3:
#         return (km-3)*1500

def check_in_mongo(connecter, data):
	try:
		database.get_info(connecter, data)[0]
		return True
	except:
		return False

def check_func(func, value):
	try:
		func(value)
		return True
	except:
		return False

# for x in database.get_info(config.months, {'month' : '03.21', 'room' : 0}):
#     for y in database.get_info(config.days, {'month' : x['code']}):
#         print(y)

# import database, strings, config
# months = []
# days = []
# times = []
# for x in range(0, 2):
#     database.insert_into(config.months, {
#         'code' : str(database.get_count(config.months, {}) + 1),
#         'room' : x,
#         'month' : '04.21'
#     })
#     for y in range(1, 31):
#         database.insert_into(config.days, {
#             'code' : database.get_count(config.days, {})+1,
#             'day' : int(y),
#             'month' : str(database.get_count(config.months, {}))
#         })
#         for z in strings.text['ru']['buttons']['time']:
#             database.insert_into(config.times, {
#                 'code' : database.get_count(config.times, {})+1,
#                 'name' : z['name'],
#                 'day' : database.get_count(config.days, {}),
#                 'active' : True
#             })

# for y in range(1, 29):
#     database.insert_into(config.days, {
#         'code' : database.get_count(config.days, {})+1,
#         'day' : int(y),
#         'month' : '9'
#     })
#     for z in strings.text['ru']['buttons']['time']:
#         database.insert_into(config.times, {
#             'code' : database.get_count(config.times, {})+1,
#             'name' : z['name'],
#             'day' : database.get_count(config.days, {}),
#             'active' : True
#         })


def new_user(message):
	return {
		'user_id' : message.from_user.id,
        'user' : {
            'name' : message.from_user.first_name,
        },
        'where' : None,
        'lang' : 'ru',
        'time' : time.time()
	}
