import database, strings, config, module, calendar, pymongo
from telebot import types

def main_menu(lang):
    menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
    menu.add(strings.text[lang]['buttons']['order'])
    menu.add(strings.text[lang]['buttons']['see_loft'], strings.text[lang]['buttons']['see_white'])
    menu.add(strings.text[lang]['buttons']['geo'], strings.text[lang]['buttons']['info'])
    return menu

def room_menu(lang):
    menu = types.InlineKeyboardMarkup()
    for m in strings.text[lang]['buttons']['rooms']:
        menu.add(types.InlineKeyboardButton(m, None, 'room:{}'.format(strings.text[lang]['buttons']['rooms'].index(m))))
    return menu

def day_menu(lang, month, room):
    menu = types.InlineKeyboardMarkup(row_width=5)
    days = []
    print({'month' :month, 'room' : room})
    try:
        month_info = database.get_info(config.months, {'month' :month, 'room' : room})[0]
    except:
        month_info = database.get_info(config.months, {'month' :'0'+month, 'room' : room})[0]
    if int(month.split('.')[0]) == int(module.get_datetime('%m')):
        for x in database.get_info(config.days, {'month' : month_info['code'], 'day'  : {'$gte' : int(module.get_datetime('%d'))}}).sort([("day", pymongo.ASCENDING)]):
            need = False
            for y in database.get_info(config.times, {'day' : int(x['code']), 'active' : True}):
                need = True
                break
            if need:
                days.append([str(x['day']), 'day:'+str(x['code'])])
    else:
        print(month_info['code'])
        for x in database.get_info(config.days, {'month' : str(month_info['code'])}).sort([("day", pymongo.ASCENDING)]):
            need = False
            print('ok')
            for y in database.get_info(config.times, {'day' : int(x['code']), 'active' : True}):
                print('ok ok')
                need = True
                break
            if need:
                days.append([str(x['day']), 'day:'+str(x['code'])])
    data = []
    for m in days:
        data.append(types.InlineKeyboardButton(str(m[0]), None, m[1]))
    menu.add(*data)
    menu.add(types.InlineKeyboardButton(strings.text[lang]['buttons']['back'], None, 'back:month'))
    return menu

def time_menu(lang, day, room, reserved):
    menu = types.InlineKeyboardMarkup(row_width=3)
    data = []
    # date = list(map(int, module.get_datetime('%d.%m.%Y', date).split('.')))
    # month_info = database.get_info(config.months, {'month' : '{}.{}'.format(date[1], date[2]-2000), 'room' : int(room)})[0]
    # day_info = database.get_info(config.days, {'month' : month_info['code'], 'day' : int(date[0])})[0]
    for m in database.get_info(config.times, {'day' : day, 'active' : True}).sort([("name", pymongo.ASCENDING)]):
        name = m['name']
        if str(m['code']) in reserved:
            name = '✅ '+m['name'] 
        data.append(types.InlineKeyboardButton(name, None, 'time:{}'.format(m['code'])))
    res = []
    if data == []:
        for m in database.get_info(config.times, {'day' : int(day), 'active' : True}).sort([("name", pymongo.ASCENDING)]):
            name = m['name']
            if str(m['code']) in reserved:
                name = '✅ '+m['name'] 
            if m['name'] in res:
                database.delete_info(config.times, {'code' : m['code']})
                continue
            res.append(m['name'])
            data.append(types.InlineKeyboardButton(name, None, 'time:{}'.format(m['code'])))
    menu.add(*data)
    menu.add(types.InlineKeyboardButton(strings.text[lang]['buttons']['book'], None, 'time'))
    menu.add(types.InlineKeyboardButton(strings.text[lang]['buttons']['back'], None, 'back:day'))
    return menu

def people_menu(lang):
    menu = types.InlineKeyboardMarkup()
    menu.add(
        types.InlineKeyboardButton(strings.text[lang]['buttons']['low_people'], None, 'people:0'),
        types.InlineKeyboardButton(strings.text[lang]['buttons']['many_people'], None, 'people:1')
    )
    return menu

def phone_menu(lang):
    menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
    menu.add(types.KeyboardButton(strings.text[lang]['buttons']['phone'], True))
    return menu


def admin_menu(lang, code):
    menu = types.InlineKeyboardMarkup()
    menu.add(
        types.InlineKeyboardButton(strings.text[lang]['buttons']['confirm'], None, 'ok:'+code),
        types.InlineKeyboardButton(strings.text[lang]['buttons']['cancel'], None, 'no:'+code)
    )
    return menu

def month_menu(lang, room):
    menu = types.InlineKeyboardMarkup()
    month = int(module.get_datetime('%m'))
    menu.add(types.InlineKeyboardButton(strings.text[lang]['buttons']['months'][month-1], None, 'month:0{}.21'.format(month)))
    menu.add(types.InlineKeyboardButton(strings.text[lang]['buttons']['months'][month], None, 'month:0{}.21'.format(month+1)))
    menu.add(types.InlineKeyboardButton(strings.text[lang]['buttons']['back'], None, 'back:room'))
    return menu


def payment_menu(lang):
    menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for m in strings.text[lang]['buttons']['payments']:
        menu.add(m)
    return menu

def remove():
    return types.ReplyKeyboardRemove()
